"""Clear-Sky Solar support."""

from homeassistant.helpers.device_registry import DeviceEntryType, DeviceInfo
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN
from .coordinator import ClearSkyCoordinator


class ClearSkySolarEntity(CoordinatorEntity[ClearSkyCoordinator]):
    """Base entity for Clear-Sky Solar sensors."""

    _attr_has_entity_name = True

    def __init__(self, coordinator: ClearSkyCoordinator) -> None:
        """Initialize the base entity."""
        super().__init__(coordinator)
        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, coordinator.config_entry.entry_id)},
            name="Clear-Sky Solar",
            model="Ineichen-Perez clear-sky model",
            entry_type=DeviceEntryType.SERVICE,
        )
