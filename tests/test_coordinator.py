"""Coordinator tests."""

from homeassistant.core import HomeAssistant
import pytest
from pytest_homeassistant_custom_component.common import MockConfigEntry

from custom_components.clear_sky_solar.const import DHI, DNI, GHI
from custom_components.clear_sky_solar.coordinator import ClearSkyCoordinator


async def test_refresh_publishes_model_output(
    hass: HomeAssistant, config_entry: MockConfigEntry, mock_model
) -> None:
    coordinator = ClearSkyCoordinator(hass, config_entry)
    await coordinator.async_refresh()

    assert coordinator.last_update_success
    assert coordinator.data == {
        GHI: pytest.approx(111.0),
        DNI: pytest.approx(222.0),
        DHI: pytest.approx(33.0),
    }
    when = mock_model.call_args.args[2]
    assert when.tzinfo is not None


async def test_update_uses_current_home_location(
    hass: HomeAssistant, config_entry: MockConfigEntry, mock_model
) -> None:
    """Location and elevation are read from hass.config on every update."""
    coordinator = ClearSkyCoordinator(hass, config_entry)

    await hass.config.async_update(latitude=39.74, longitude=-104.99, elevation=1609)
    await coordinator.async_refresh()
    assert mock_model.call_args.args[:2] == (39.74, -104.99)
    assert mock_model.call_args.kwargs["elevation_m"] == 1609

    # A later change to the home location is picked up without a reload
    await hass.config.async_update(latitude=52.52, longitude=13.40, elevation=34)
    await coordinator.async_refresh()
    assert mock_model.call_args.args[:2] == (52.52, 13.40)
    assert mock_model.call_args.kwargs["elevation_m"] == 34
