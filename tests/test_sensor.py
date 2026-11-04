"""Sensor tests."""

from homeassistant.components.sensor import SensorDeviceClass, SensorStateClass
from homeassistant.core import HomeAssistant
from homeassistant.helpers import entity_registry as er
from pytest_homeassistant_custom_component.common import MockConfigEntry

from custom_components.clear_sky_solar.const import DOMAIN
from custom_components.clear_sky_solar.coordinator import ClearSkyCoordinator
from custom_components.clear_sky_solar.sensor import (
    SENSOR_DESCRIPTIONS,
    ClearSkySolarSensor,
)


async def test_sensor_metadata(
    hass: HomeAssistant, config_entry: MockConfigEntry, mock_model
) -> None:
    assert await hass.config_entries.async_setup(config_entry.entry_id)
    await hass.async_block_till_done()

    registry = er.async_get(hass)
    for desc in SENSOR_DESCRIPTIONS:
        entity_id = registry.async_get_entity_id(
            "sensor", DOMAIN, f"{DOMAIN}_{desc.key}"
        )
        assert entity_id is not None
        state = hass.states.get(entity_id)
        assert state is not None
        assert state.attributes["device_class"] == SensorDeviceClass.IRRADIANCE
        assert state.attributes["state_class"] == SensorStateClass.MEASUREMENT


async def test_no_data_returns_none(
    hass: HomeAssistant, config_entry: MockConfigEntry
) -> None:
    coordinator = ClearSkyCoordinator(hass, config_entry)
    assert coordinator.data is None

    for desc in SENSOR_DESCRIPTIONS:
        assert ClearSkySolarSensor(coordinator, desc).native_value is None
