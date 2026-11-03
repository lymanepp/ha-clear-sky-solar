# tests/conftest.py
from unittest.mock import AsyncMock, patch

import pytest
from pytest_homeassistant_custom_component.common import MockConfigEntry

# Use the same keys the integration exports
from custom_components.clear_sky_solar.const import DHI, DNI, DOMAIN, GHI


@pytest.fixture(autouse=True)
def auto_enable_custom_integrations(enable_custom_integrations):
    """Let Home Assistant load the integration from custom_components."""


@pytest.fixture
def config_entry(hass) -> MockConfigEntry:
    """A Clear-Sky Solar config entry added to hass (not set up)."""
    entry = MockConfigEntry(domain=DOMAIN, title="Clear-Sky Solar", unique_id=DOMAIN)
    entry.add_to_hass(hass)
    return entry


@pytest.fixture
def patch_third_party():
    """Stub out any third-party math so tests are deterministic."""
    payload = {GHI: 111.0, DNI: 222.0, DHI: 33.0}

    with (
        patch(
            "custom_components.clear_sky_solar.coordinator.ClearSkyCoordinator.async_update_clear_sky_estimates",
            new=AsyncMock(return_value=payload),
        ),
        patch(
            "custom_components.clear_sky_solar.coordinator.ClearSkyCoordinator._async_update_data",
            new=AsyncMock(return_value=payload),
        ),
    ):
        yield
