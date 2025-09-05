# tests/conftest.py
from __future__ import annotations

from unittest.mock import AsyncMock, patch

import pytest

# Use the same keys the integration exports
from custom_components.clear_sky_solar.const import DHI, DNI, GHI


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
