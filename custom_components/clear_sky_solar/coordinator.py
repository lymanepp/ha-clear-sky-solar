"""The Clear-Sky Solar data coordinator."""

from datetime import UTC, datetime
import logging

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator

from .const import DHI, DNI, GHI, UPDATE_INTERVAL
from .model import compute_clear_sky

_LOGGER = logging.getLogger(__name__)


class ClearSkyCoordinator(DataUpdateCoordinator[dict[str, float]]):
    """Clear-Sky Solar data coordinator."""

    def __init__(self, hass: HomeAssistant, config_entry: ConfigEntry) -> None:
        """Initialize the coordinator."""
        super().__init__(
            hass,
            _LOGGER,
            config_entry=config_entry,
            name="clear_sky_solar_data",
            update_method=self.async_update_clear_sky_estimates,
            update_interval=UPDATE_INTERVAL,
        )

    async def async_update_clear_sky_estimates(self) -> dict[str, float]:
        """Recalculate Clear-Sky Solar estimates."""
        # Read the home location on every update so changes in Home Assistant's
        # settings take effect without reloading the integration.
        config = self.hass.config
        r = compute_clear_sky(
            config.latitude,
            config.longitude,
            datetime.now(tz=UTC),
            elevation_m=config.elevation,
        )
        return {GHI: r.ghi, DNI: r.dni, DHI: r.dhi}
