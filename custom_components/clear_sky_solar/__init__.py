"""The Clear-Sky Solar component."""

from dataclasses import dataclass

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import Platform
from homeassistant.core import HomeAssistant

from .coordinator import ClearSkyCoordinator

PLATFORMS = [Platform.SENSOR]


@dataclass
class ClearSkyData:
    """Runtime data."""

    coordinator: ClearSkyCoordinator


type ClearSkyConfigEntry = ConfigEntry[ClearSkyData]


async def async_setup_entry(hass: HomeAssistant, entry: ClearSkyConfigEntry) -> bool:
    """Set up Clear-Sky Solar from a config entry."""
    coordinator = ClearSkyCoordinator(hass, entry)
    await coordinator.async_config_entry_first_refresh()
    entry.runtime_data = ClearSkyData(coordinator=coordinator)
    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)
    return True
