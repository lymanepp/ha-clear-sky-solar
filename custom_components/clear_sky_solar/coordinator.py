"""The Clear-Sky Solar data coordinator."""

from datetime import UTC, datetime
import logging

from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator

from .const import DHI, DNI, GHI, UPDATE_INTERVAL
from .model import compute_clear_sky

_LOGGER = logging.getLogger(__name__)


class ClearSkyCoordinator(DataUpdateCoordinator[dict[str, float]]):
    """Clear-Sky Solar data coordinator."""

    def __init__(self, hass: HomeAssistant):
        self._lat = float(hass.config.latitude or 0.0)
        self._lon = float(hass.config.longitude or 0.0)
        super().__init__(
            hass,
            _LOGGER,
            name="clear_sky_solar_data",
            update_method=self.async_update_clear_sky_estimates,
            update_interval=UPDATE_INTERVAL,
        )

    async def async_update_clear_sky_estimates(self) -> dict[str, float]:
        """Recalculate Clear-Sky Solar estimates."""
        now = datetime.now(tz=UTC)
        r = compute_clear_sky(self._lat, self._lon, now)
        return {GHI: r.ghi, DNI: r.dni, DHI: r.dhi}
