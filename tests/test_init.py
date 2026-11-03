"""Set up the integration through Home Assistant."""

from homeassistant.config_entries import ConfigEntryState
from homeassistant.core import HomeAssistant
from homeassistant.helpers import entity_registry as er
import pytest
from pytest_homeassistant_custom_component.common import MockConfigEntry

from custom_components.clear_sky_solar.const import DOMAIN


async def test_setup_creates_sensors(
    hass: HomeAssistant, config_entry: MockConfigEntry, patch_third_party
) -> None:
    assert await hass.config_entries.async_setup(config_entry.entry_id)
    await hass.async_block_till_done()

    assert config_entry.state is ConfigEntryState.LOADED

    registry = er.async_get(hass)
    expected = {"ghi": 111.0, "dni": 222.0, "dhi": 33.0}
    for key, value in expected.items():
        entity_id = registry.async_get_entity_id("sensor", DOMAIN, f"{DOMAIN}_{key}")
        assert entity_id is not None, key
        state = hass.states.get(entity_id)
        assert state is not None
        assert float(state.state) == pytest.approx(value)
        assert state.attributes["unit_of_measurement"] == "W/m²"


async def test_setup_with_real_model(
    hass: HomeAssistant, config_entry: MockConfigEntry
) -> None:
    """The unpatched model runs inside Home Assistant and yields numbers."""
    assert await hass.config_entries.async_setup(config_entry.entry_id)
    await hass.async_block_till_done()

    data = config_entry.runtime_data.coordinator.data
    assert set(data) == {"ghi", "dni", "dhi"}
    assert all(value >= 0.0 for value in data.values())
