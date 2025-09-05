from __future__ import annotations

from homeassistant.const import UnitOfIrradiance
import pytest

from custom_components.clear_sky_solar.const import DHI, DNI, GHI
from custom_components.clear_sky_solar.coordinator import ClearSkyCoordinator
from custom_components.clear_sky_solar.sensor import (
    SENSOR_DESCRIPTIONS,
    ClearSkySolarSensor,
)

pytestmark = pytest.mark.asyncio


async def test_entities_created_and_metadata(hass, patch_third_party):
    coordinator = ClearSkyCoordinator(hass)
    # Seed coordinator data so sensors have values
    _ = await coordinator.async_update_clear_sky_estimates()

    sensors = [ClearSkySolarSensor(coordinator, d) for d in SENSOR_DESCRIPTIONS]
    assert len(sensors) == 3  # noqa: PLR2004

    # Unique IDs and units are correct
    for s in sensors:
        assert s.unique_id.endswith(s.entity_description.key)
        assert (
            s.entity_description.native_unit_of_measurement
            == UnitOfIrradiance.WATTS_PER_SQUARE_METER
        )


async def test_native_values_surface_from_coordinator_direct(hass, patch_third_party):
    coordinator = ClearSkyCoordinator(hass)
    data = await coordinator.async_update_clear_sky_estimates()
    coordinator.data = data

    sensors = {d.key: ClearSkySolarSensor(coordinator, d) for d in SENSOR_DESCRIPTIONS}

    assert sensors[GHI].native_value == pytest.approx(111.0)
    assert sensors[DNI].native_value == pytest.approx(222.0)
    assert sensors[DHI].native_value == pytest.approx(33.0)


async def test_no_data_returns_none_direct(hass, patch_third_party):
    coordinator = ClearSkyCoordinator(hass)
    coordinator.data = None

    sensors = [ClearSkySolarSensor(coordinator, d) for d in SENSOR_DESCRIPTIONS]
    for s in sensors:
        assert s.native_value is None
