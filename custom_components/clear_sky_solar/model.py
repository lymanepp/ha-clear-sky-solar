"""
Clear-sky solar irradiance model (Ineichen-Perez).

A pure-Python port of the Ineichen-Perez clear-sky model, matching pvlib's
``pvlib.clearsky.ineichen`` (without the optional Perez enhancement). pvlib
itself is not used because its numeric dependencies are not available on
Home Assistant's musl-based images.

References
----------
Ineichen, P. and Perez, R. (2002). A new airmass independent formulation for
the Linke turbidity coefficient. Solar Energy 73(3), 151-157.

Kasten, F. and Young, A. T. (1989). Revised optical air mass tables and
approximation formula. Applied Optics 28(22), 4735-4738.
"""

from dataclasses import dataclass
from datetime import UTC, datetime
from math import cos, exp, pi, radians, sin, tan
from typing import Final

from astral import Observer, sun  # type: ignore[import-untyped]

SOLAR_CONSTANT: Final[float] = 1366.1  # W/m², same default as pvlib
AIR_TEMPERATURE: Final[float] = 12.0  # °C, annual-average default used by pvlib


@dataclass(frozen=True)
class ClearSkyResult:
    """Clear-sky irradiance components (W/m²)."""

    ghi: float
    dni: float
    dhi: float


_NIGHT: Final[ClearSkyResult] = ClearSkyResult(0.0, 0.0, 0.0)


def _extraterrestrial_dni(when: datetime) -> float:
    """Extraterrestrial normal irradiance using Spencer's Earth-Sun distance."""
    b = 2.0 * pi * (when.timetuple().tm_yday - 1) / 365.0
    return SOLAR_CONSTANT * (
        1.00011
        + 0.034221 * cos(b)
        + 0.00128 * sin(b)
        + 0.000719 * cos(2 * b)
        + 0.000077 * sin(2 * b)
    )


def _relative_airmass(elevation_deg: float) -> float:
    """Kasten-Young (1989) relative air mass from apparent solar elevation."""
    zenith = 90.0 - elevation_deg
    return 1.0 / (cos(radians(zenith)) + 0.50572 * (96.07995 - zenith) ** -1.6364)


def _pressure_from_altitude(altitude_m: float) -> float:
    """Standard-atmosphere surface pressure (Pa) for a site altitude."""
    return 100.0 * ((44331.514 - altitude_m) / 11880.516) ** (1 / 0.1902632)


def apparent_solar_elevation(
    lat: float, lon: float, when: datetime, altitude_m: float = 0.0
) -> float:
    """
    Solar elevation (degrees) corrected for refraction at the site's pressure.

    Astral's built-in refraction assumes sea level, which puts the sun visibly
    above the horizon too early at high-altitude sites. Instead, take the
    geometric elevation from Astral and apply the NREL SPA refraction
    correction, scaled by pressure, as pvlib does.
    """
    true_elev = float(sun.elevation(Observer(lat, lon), when, with_refraction=False))
    if true_elev < -(0.26667 + 0.5667):  # sun's radius + horizon refraction
        return true_elev
    pressure_hpa = _pressure_from_altitude(altitude_m) / 100.0
    refraction = (
        (pressure_hpa / 1010.0)
        * (283.0 / (273.0 + AIR_TEMPERATURE))
        * 1.02
        / (60.0 * tan(radians(true_elev + 10.3 / (true_elev + 5.11))))
    )
    return true_elev + refraction


def compute_clear_sky(
    lat: float,
    lon: float,
    when: datetime,
    *,
    elevation_m: float = 0.0,
    linke_turbidity: float = 3.0,
) -> ClearSkyResult:
    """
    Compute clear-sky GHI, DNI and DHI (W/m²) with the Ineichen-Perez model.

    Parameters
    ----------
    lat, lon : float
        Site latitude/longitude in degrees (W negative).
    when : datetime
        Timestamp; naive values are treated as UTC.
    elevation_m : float, default 0.0
        Site altitude above sea level in meters.
    linke_turbidity : float, default 3.0
        Linke turbidity (typically 2-5; higher means hazier).
    """
    when = when.astimezone(UTC) if when.tzinfo else when.replace(tzinfo=UTC)

    elevation = apparent_solar_elevation(lat, lon, when, elevation_m)
    if elevation <= 0.0:
        return _NIGHT

    cos_zenith = cos(radians(90.0 - elevation))
    airmass = (
        _relative_airmass(elevation) * _pressure_from_altitude(elevation_m) / 101325.0
    )
    dni_extra = _extraterrestrial_dni(when)
    tl = linke_turbidity

    fh1 = exp(-elevation_m / 8000.0)
    fh2 = exp(-elevation_m / 1250.0)
    cg1 = 5.09e-5 * elevation_m + 0.868
    cg2 = 3.92e-5 * elevation_m + 0.0387

    ghi = cg1 * dni_extra * cos_zenith * exp(-cg2 * airmass * (fh1 + fh2 * (tl - 1)))

    # Beam: the lesser of Ineichen's direct formula and the GHI-consistent limit.
    b = 0.664 + 0.163 / fh1
    dni_beam = dni_extra * b * exp(-0.09 * airmass * (tl - 1))
    dni_limit = ghi * max(
        0.0, (1 - (0.1 - 0.2 * exp(-tl)) / (0.1 + 0.882 / fh1)) / cos_zenith
    )
    dni = max(0.0, min(dni_beam, dni_limit))

    dhi = max(0.0, ghi - dni * cos_zenith)

    return ClearSkyResult(ghi=max(0.0, ghi), dni=dni, dhi=dhi)
