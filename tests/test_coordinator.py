from unittest.mock import patch

from homeassistant.core import HomeAssistant
import pytest
from pytest_homeassistant_custom_component.common import MockConfigEntry

from custom_components.clear_sky_solar.const import DHI, DNI, GHI
from custom_components.clear_sky_solar.coordinator import ClearSkyCoordinator
from custom_components.clear_sky_solar.model import ClearSkyResult


@pytest.mark.asyncio
async def test_coordinator_update_returns_expected_keys(
    hass: HomeAssistant, config_entry: MockConfigEntry, patch_third_party
) -> None:
    coordinator = ClearSkyCoordinator(hass, config_entry)
    data = await coordinator.async_update_clear_sky_estimates()
    assert set(data.keys()) == {GHI, DNI, DHI}
    assert data[GHI] == pytest.approx(111.0)
    assert data[DNI] == pytest.approx(222.0)
    assert data[DHI] == pytest.approx(33.0)


@pytest.mark.asyncio
async def test_coordinator_refresh_populates_data(
    hass: HomeAssistant, config_entry: MockConfigEntry, patch_third_party
) -> None:
    coordinator = ClearSkyCoordinator(hass, config_entry)
    await coordinator.async_refresh()
    assert coordinator.data is not None
    assert GHI in coordinator.data
    assert DNI in coordinator.data
    assert DHI in coordinator.data


async def test_update_uses_current_home_location(
    hass: HomeAssistant, config_entry: MockConfigEntry
) -> None:
    """Location and elevation are read from hass.config on every update."""
    coordinator = ClearSkyCoordinator(hass, config_entry)
    result = ClearSkyResult(ghi=1.0, dni=2.0, dhi=3.0)

    with patch(
        "custom_components.clear_sky_solar.coordinator.compute_clear_sky",
        return_value=result,
    ) as compute:
        await hass.config.async_update(
            latitude=39.74, longitude=-104.99, elevation=1609
        )
        await coordinator.async_update_clear_sky_estimates()
        args, kwargs = compute.call_args
        assert args[:2] == (39.74, -104.99)
        assert kwargs["elevation_m"] == 1609

        # A later change to the home location is picked up without a reload
        await hass.config.async_update(latitude=52.52, longitude=13.40, elevation=34)
        await coordinator.async_update_clear_sky_estimates()
        args, kwargs = compute.call_args
        assert args[:2] == (52.52, 13.40)
        assert kwargs["elevation_m"] == 34
