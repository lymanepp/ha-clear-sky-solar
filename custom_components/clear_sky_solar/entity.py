"""Clear-Sky Solar support."""

from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .coordinator import ClearSkyCoordinator


class ClearSkySolarEntity(CoordinatorEntity[ClearSkyCoordinator]):
    """Base entity for Clear-Sky Solar sensors."""

    def __init__(self, coordinator: ClearSkyCoordinator):
        """Initialize the base entity."""
        super().__init__(coordinator)
        self._attr_should_poll = False
