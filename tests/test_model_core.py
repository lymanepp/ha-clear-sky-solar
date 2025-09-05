from __future__ import annotations

from datetime import UTC, datetime

import pytest

from custom_components.clear_sky_solar.model import ClearSkyResult, compute_clear_sky

LAT, LON = 37.7749, -122.4194  # San Francisco-ish


def _assert_cs_ok(cs: ClearSkyResult) -> None:
    assert cs.ghi >= 0 and cs.dni >= 0 and cs.dhi >= 0
    assert cs.ghi >= cs.dhi  # diffuse cannot exceed global for clear-sky


def test_midday_reasonable_magnitudes() -> None:
    # June solstice, ~1pm local (20:00 UTC) — high sun, clear
    when = datetime(2024, 6, 21, 20, 0, 0, tzinfo=UTC)
    cs = compute_clear_sky(LAT, LON, when, elevation_m=16.0, linke_turbidity=3.0)
    _assert_cs_ok(cs)
    # Typical clear-sky ranges; broad enough to be robust across small changes
    assert 800 <= cs.dni <= 1100
    assert 800 <= cs.ghi <= 1150
    assert 50 <= cs.dhi <= 220


def test_winter_midday_lower_irradiance() -> None:
    when_summer = datetime(2024, 6, 21, 20, 0, 0, tzinfo=UTC)
    when_winter = datetime(2024, 12, 21, 20, 0, 0, tzinfo=UTC)

    cs_summer = compute_clear_sky(
        LAT, LON, when_summer, elevation_m=16.0, linke_turbidity=3.0
    )
    cs_winter = compute_clear_sky(
        LAT, LON, when_winter, elevation_m=16.0, linke_turbidity=3.0
    )

    _assert_cs_ok(cs_summer)
    _assert_cs_ok(cs_winter)

    # Lower sun in winter -> lower totals
    assert cs_winter.ghi < cs_summer.ghi
    assert cs_winter.dni < cs_summer.dni


def test_horizon_zero() -> None:
    # ~1am local (08:00 UTC) — sun well below horizon
    night = datetime(2024, 6, 21, 8, 0, 0, tzinfo=UTC)
    cs = compute_clear_sky(LAT, LON, night)
    assert cs.ghi == 0
    assert cs.dni == 0
    assert cs.dhi == 0


@pytest.mark.parametrize("tl_low,tl_high", [(2.2, 5.0), (2.5, 4.0)])
def test_hazier_means_less_beam_and_global(tl_low: float, tl_high: float) -> None:
    when = datetime(2024, 6, 21, 20, 0, 0, tzinfo=UTC)
    cs_clear = compute_clear_sky(
        LAT, LON, when, elevation_m=16.0, linke_turbidity=tl_low
    )
    cs_hazy = compute_clear_sky(
        LAT, LON, when, elevation_m=16.0, linke_turbidity=tl_high
    )
    _assert_cs_ok(cs_clear)
    _assert_cs_ok(cs_hazy)

    assert cs_hazy.dni < cs_clear.dni
    assert cs_hazy.ghi < cs_clear.ghi
    # Diffuse remains bounded and not dominating on clear-sky
    assert cs_hazy.dhi <= cs_hazy.ghi
