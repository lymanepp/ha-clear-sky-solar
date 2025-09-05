"""
Clear-sky solar irradiance model (Haurwitz + ERBS).

This exists because pvlib is not compatible with Home Assistant's MUSL C library.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import UTC, datetime
from math import cos, exp, pi, radians, sin
import statistics as _stats
from typing import Final

from astral import sun  # type: ignore[import-untyped]
from astral.location import LocationInfo  # type: ignore[import-untyped]
from homeassistant.util import dt as dt_util

# ---- Constants ----------------------------------------------------------------

ISC: Final[float] = 1367.0  # W/m^2, solar constant (World Radiometric Reference)

# ---- Public datatypes ---------------------------------------------------------


@dataclass(frozen=True)
class ClearSkyResult:
    """Container for clear-sky irradiance components (W/m²)."""

    ghi: float
    dni: float
    dhi: float


# ---- Small utilities ----------------------------------------------------------


def _as_aware_utc(ts: datetime) -> datetime:
    """Ensure the timestamp is timezone-aware in UTC."""
    return ts if ts.tzinfo else ts.replace(tzinfo=UTC)


def _day_of_year(ts: datetime) -> int:
    """Day of year in local time (to match typical solar geometry usage)."""
    return int(dt_util.as_local(ts).timetuple().tm_yday)


def _eccentricity_correction(n: int) -> float:
    """Spencer/NREL Earth-Sun distance correction factor E0."""
    g = 2.0 * pi * (n - 1) / 365.0
    return (
        1.00011
        + 0.034221 * cos(g)
        + 0.00128 * sin(g)
        + 0.000719 * cos(2 * g)
        + 0.000077 * sin(2 * g)
    )


def _solar_elevation(lat: float, lon: float, when: datetime) -> float:
    """Solar elevation angle (degrees) using Astral (apparent elevation)."""
    loc = LocationInfo(latitude=lat, longitude=lon)
    # Astral expects local datetime; Home Assistant helper gives local safely.
    return float(
        sun.elevation(observer=loc.observer, dateandtime=dt_util.as_local(when))
    )


def _mu_from_elevation(elev_deg: float) -> float:
    """Return μ = cos(zenith) = cos(90° - elevation)."""
    return cos(radians(90.0 - elev_deg))


# ---- Haurwitz core + gentle corrections (for GHI) -----------------------------


def _haurwitz_ghi_from_mu(mu: float) -> float:
    """
    Original Haurwitz clear-sky GHI (W/m²) as a function of μ.

    Formula: 1098 * μ * exp(-0.057 / μ)
    Guard μ to avoid division by ~0.
    """
    if mu <= 0.0:
        return 0.0
    mu_eff = max(1e-6, mu)
    return 1098.0 * mu_eff * exp(-0.057 / mu_eff)


def _mu_shape_correction(mu: float) -> float:
    """
    Mild μ-shape correction to reduce slight high-sun bias of Haurwitz.

    ~1.0 for most μ; trims a few percent near zenith.
    """
    if mu <= 0.0:
        return 0.0
    return 1.0 - 0.05 * (1.0 - mu) ** 1.6


def _altitude_gain_factor(elevation_m: float) -> float:
    """
    Empirical altitude gain: ~7% per km, clamped.

    This softens high-altitude brightening vs classic 10%/km heuristics.
    """
    f = 1.0 + 0.07 * max(0.0, elevation_m) / 1000.0
    return max(0.92, min(1.18, f))


def _turbidity_attenuation(linke_turbidity: float) -> float:
    """
    Slightly stronger attenuation vs Linke turbidity (around TL=3 baseline).

    A gentle shaping to better align with Ineichen-like behavior without pvlib.
    """
    tl = max(1.5, min(8.0, linke_turbidity))
    return exp(-0.04 * (tl - 3.0))


# ---- Diffuse split (ERBS) for DHI/DNI from GHI -------------------------------


def _erbs_diffuse_fraction(kt: float) -> float:
    """
    ERBS diffuse fraction parameterization.

    Input:
      kt : clearness index = GHI / GHI0 (extraterrestrial horizontal)
    """
    erbs_kt_overcast = 0.22  # very cloudy/overcast regime
    erbs_kt_clear = 0.80  # very clear-sky regime
    if kt < erbs_kt_overcast:
        return 1.0 - 0.09 * kt
    if kt < erbs_kt_clear:
        return 0.9511 - 0.1604 * kt + 4.388 * kt**2 - 16.638 * kt**3 + 12.336 * kt**4
    return 0.165


# ---- Public API ---------------------------------------------------------------


def compute_clear_sky(
    lat: float,
    lon: float,
    when: datetime,
    *,
    elevation_m: float = 0.0,
    linke_turbidity: float = 3.0,
) -> ClearSkyResult:
    """
    Compute clear-sky irradiance components (GHI/DNI/DHI) in W/m².

    - GHI is Haurwitz with μ-shape softening, altitude and TL adjustments,
      capped at 98% of extraterrestrial horizontal (GHI0).
    - DHI/DNI are derived from GHI via ERBS diffuse fraction.

    Parameters
    ----------
    lat, lon : float
        Site latitude/longitude in degrees (W negative).
    when : datetime
        Timestamp; naive is treated as UTC.
    elevation_m : float, default 0.0
        Site altitude in meters.
    linke_turbidity : float, default 3.0
        Linke turbidity (typical 2-5).

    Returns
    -------
    ClearSkyResult(ghi, dni, dhi)
    """
    when = _as_aware_utc(when)

    elev = _solar_elevation(lat, lon, when)
    if elev <= 0.0:
        return ClearSkyResult(0.0, 0.0, 0.0)

    mu = max(0.0, _mu_from_elevation(elev))

    # Extraterrestrial on normal and horizontal planes
    n = _day_of_year(when)
    dni0 = ISC * _eccentricity_correction(n)
    ghi0 = dni0 * mu  # extraterrestrial horizontal

    # Baseline Haurwitz with subtle shaping and site factors
    ghi_base = _haurwitz_ghi_from_mu(mu) * _mu_shape_correction(mu)
    ghi = (
        ghi_base
        * _altitude_gain_factor(elevation_m)
        * _turbidity_attenuation(linke_turbidity)
    )

    # Physical cap vs extraterrestrial horizontal
    ghi_cap = 0.98 * ghi0
    ghi = max(0.0, min(ghi, ghi_cap))

    # Diffuse split via ERBS using clearness index
    ghi0_guard = max(1e-3, ghi0)
    kt = min(1.2, ghi / ghi0_guard)
    fd = _erbs_diffuse_fraction(kt)

    dhi = max(0.0, min(ghi, fd * ghi))
    mu_guard = max(1e-3, mu)
    dni = max(0.0, (ghi - dhi) / mu_guard)

    return ClearSkyResult(ghi=ghi, dni=dni, dhi=dhi)


# ---- Optional: simple site calibration (not used by core) --------------------


def estimate_site_scale_factor(
    observed_ghi: list[float] | tuple[float, ...],
    modeled_ghi: list[float] | tuple[float, ...],
    elevations_deg: list[float] | tuple[float, ...],
    *,
    min_elev: float = 10.0,
    max_elev: float = 60.0,
) -> float:
    """
    Estimate a multiplicative site scale factor from clear-day data.

    Use several clear hours; feed in observed vs modeled GHI with corresponding
    solar elevations. The median ratio over [min_elev, max_elev] is returned.

    This can reduce local biases (sensor gain, horizon losses, albedo context).
    """

    if not (len(observed_ghi) == len(modeled_ghi) == len(elevations_deg)):
        raise ValueError("invalid_sequence_lengths")

    ghi_numeric_floor = 1e-6

    pairs: list[float] = []
    for obs, mod, el in zip(observed_ghi, modeled_ghi, elevations_deg, strict=False):
        if el < min_elev or el > max_elev:
            continue
        if mod <= ghi_numeric_floor:
            continue
        r = obs / mod
        if r > 0:
            pairs.append(r)

    if not pairs:
        return 1.0
    # Median is robust to a few outliers
    return float(_stats.median(pairs))
