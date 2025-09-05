"""The Clear-Sky Solar component."""

from dataclasses import dataclass

from homeassistant.components.sensor.const import DOMAIN as SENSOR_DOMAIN
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant

from .coordinator import ClearSkyCoordinator

PLATFORMS = [SENSOR_DOMAIN]


@dataclass
class ClearSkyData:
    """Runtime data."""

    coordinator: ClearSkyCoordinator


async def async_setup_entry(
    hass: HomeAssistant, entry: ConfigEntry[ClearSkyData]
) -> bool:
    """Set up Clear-Sky Solar from a config entry."""
    coordinator = ClearSkyCoordinator(hass)
    entry.runtime_data = ClearSkyData(coordinator=coordinator)
    await coordinator.async_refresh()
    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)
    return True
