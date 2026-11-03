"""Compare the pure-Python Ineichen model to pvlib's reference implementation."""

from datetime import UTC, datetime

import numpy as np
import pandas as pd
import pvlib  # pyright: ignore[reportMissingTypeStubs]
import pytest

from custom_components.clear_sky_solar.model import compute_clear_sky

YEAR = 2024

# (name, lat, lon, altitude_m, linke_turbidity)
LOCATIONS: list[tuple[str, float, float, float, float]] = [
    ("San Francisco, US", 37.7749, -122.4194, 16.0, 3.0),
    ("Denver, US", 39.7392, -104.9903, 1609.0, 3.0),
    ("Miami, US", 25.7617, -80.1918, 2.0, 3.5),
    ("Berlin, DE", 52.5200, 13.4050, 34.0, 3.0),
    ("Nairobi, KE", -1.2921, 36.8219, 1795.0, 2.8),
    ("Tromso, NO", 69.6492, 18.9553, 10.0, 2.5),
    ("La Paz, BO", -16.4897, -68.1193, 3640.0, 2.0),
    ("Delhi, IN", 28.6139, 77.2090, 216.0, 6.0),
]

# Worst-case error in any hour (W/m²). What remains comes from small solar
# position differences (Astral vs pvlib's NREL SPA), which DNI feels most.
MAX_ABS_ERR = {"ghi": 0.5, "dni": 2.0, "dhi": 0.2}

# Ineichen DNI jumps from 0 to tens of W/m² as the sun crosses the horizon,
# so a 0.01° position difference there swings DNI a lot (GHI and DHI stay ~0).
# Skip DNI within this band around the horizon.
HORIZON_BAND_DEG = 0.1


@pytest.mark.parametrize(
    ("name", "lat", "lon", "alt_m", "tl"), LOCATIONS, ids=[loc[0] for loc in LOCATIONS]
)
def test_hourly_all_year_matches_pvlib_ineichen(
    name: str, lat: float, lon: float, alt_m: float, tl: float
) -> None:
    """Every hour of a year should match pvlib Ineichen to within ~1 W/m²."""
    times = pd.date_range(
        datetime(YEAR, 1, 1, tzinfo=UTC),
        datetime(YEAR, 12, 31, 23, tzinfo=UTC),
        freq="1h",
    )
    location = pvlib.location.Location(lat, lon, altitude=alt_m)
    ref = location.get_clearsky(times, model="ineichen", linke_turbidity=tl)
    ref_elevation = location.get_solarposition(times)["apparent_elevation"]
    off_horizon = np.abs(ref_elevation.to_numpy()) > HORIZON_BAND_DEG

    ours = [
        compute_clear_sky(
            lat, lon, ts.to_pydatetime(), elevation_m=alt_m, linke_turbidity=tl
        )
        for ts in times
    ]

    for component in ("ghi", "dni", "dhi"):
        our_vals = np.array([getattr(cs, component) for cs in ours])
        err = np.abs(our_vals - ref[component].to_numpy())
        if component == "dni":
            err = err[off_horizon]
        max_err = float(err.max())
        assert max_err <= MAX_ABS_ERR[component], (
            f"{name} {component}: max error {max_err:.2f} W/m²"
        )
