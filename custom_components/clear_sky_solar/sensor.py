from __future__ import annotations

from homeassistant.components.sensor import SensorEntity, SensorEntityDescription
from homeassistant.components.sensor.const import SensorDeviceClass, SensorStateClass
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import UnitOfIrradiance
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from . import ClearSkyData
from .const import DHI, DNI, DOMAIN, GHI
from .coordinator import ClearSkyCoordinator
from .entity import ClearSkySolarEntity


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry[ClearSkyData],
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up the Clear-Sky Solar sensors from config entry."""
    coordinator = entry.runtime_data.coordinator
    async_add_entities(
        [ClearSkySolarSensor(coordinator, desc) for desc in SENSOR_DESCRIPTIONS]
    )


class ClearSkySolarSensor(ClearSkySolarEntity, SensorEntity):
    """Representation of Clear-Sky Solar Irradiance sensor (GHI, DNI, etc.)."""

    def __init__(self, coordinator: ClearSkyCoordinator, desc: SensorEntityDescription):
        """
        Initialize the sensor with the DataUpdateCoordinator and sensor description.
        """
        super().__init__(coordinator)
        self.entity_description = desc
        self._attr_unique_id = f"{DOMAIN}_{desc.key}"

    @property
    def native_value(self) -> float | None:  # type: ignore[override]
        """Return the current value from the coordinator data."""
        if self.coordinator.data:
            return self.coordinator.data.get(self.entity_description.key)
        return None


SENSOR_DESCRIPTIONS: list[SensorEntityDescription] = [
    SensorEntityDescription(
        key=GHI,
        name="Clear-Sky GHI",
        device_class=SensorDeviceClass.IRRADIANCE,
        state_class=SensorStateClass.MEASUREMENT,
        native_unit_of_measurement=UnitOfIrradiance.WATTS_PER_SQUARE_METER,
        suggested_display_precision=1,
    ),
    SensorEntityDescription(
        key=DNI,
        name="Clear-Sky DNI",
        device_class=SensorDeviceClass.IRRADIANCE,
        state_class=SensorStateClass.MEASUREMENT,
        native_unit_of_measurement=UnitOfIrradiance.WATTS_PER_SQUARE_METER,
        suggested_display_precision=1,
    ),
    SensorEntityDescription(
        key=DHI,
        name="Clear-Sky DHI",
        device_class=SensorDeviceClass.IRRADIANCE,
        state_class=SensorStateClass.MEASUREMENT,
        native_unit_of_measurement=UnitOfIrradiance.WATTS_PER_SQUARE_METER,
        suggested_display_precision=1,
    ),
]
