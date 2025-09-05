from __future__ import annotations

from homeassistant.core import HomeAssistant
import pytest

from custom_components.clear_sky_solar.const import DHI, DNI, GHI
from custom_components.clear_sky_solar.coordinator import ClearSkyCoordinator


@pytest.mark.asyncio
async def test_coordinator_update_returns_expected_keys(
    hass: HomeAssistant, patch_third_party
) -> None:
    coordinator = ClearSkyCoordinator(hass)
    data = await coordinator.async_update_clear_sky_estimates()
    assert set(data.keys()) == {GHI, DNI, DHI}
    assert data[GHI] == pytest.approx(111.0)
    assert data[DNI] == pytest.approx(222.0)
    assert data[DHI] == pytest.approx(33.0)


@pytest.mark.asyncio
async def test_coordinator_refresh_populates_data(
    hass: HomeAssistant, patch_third_party
) -> None:
    coordinator = ClearSkyCoordinator(hass)
    await coordinator.async_refresh()
    assert coordinator.data is not None
    assert GHI in coordinator.data
    assert DNI in coordinator.data
    assert DHI in coordinator.data
