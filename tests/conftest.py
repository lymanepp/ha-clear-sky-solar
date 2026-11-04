"""Shared test fixtures."""

from unittest.mock import patch

import pytest
from pytest_homeassistant_custom_component.common import MockConfigEntry

from custom_components.clear_sky_solar.const import DOMAIN
from custom_components.clear_sky_solar.model import ClearSkyResult


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
def mock_model():
    """Replace the irradiance model with fixed values; the coordinator still runs."""
    with patch(
        "custom_components.clear_sky_solar.coordinator.compute_clear_sky",
        return_value=ClearSkyResult(ghi=111.0, dni=222.0, dhi=33.0),
    ) as compute:
        yield compute
