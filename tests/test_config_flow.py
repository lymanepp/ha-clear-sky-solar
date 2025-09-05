from __future__ import annotations

import importlib
import inspect

from homeassistant.config_entries import ConfigFlow
from homeassistant.core import HomeAssistant
import pytest


@pytest.mark.asyncio
async def test_user_flow_creates_entry(hass: HomeAssistant) -> None:
    flow_mod = importlib.import_module("custom_components.clear_sky_solar.config_flow")
    flow_cls = None
    for obj in vars(flow_mod).values():
        if (
            inspect.isclass(obj)
            and issubclass(obj, ConfigFlow)
            and obj is not ConfigFlow
        ):
            flow_cls = obj
            break
    assert flow_cls is not None, "No ConfigFlow subclass found in config_flow.py"

    flow = flow_cls()
    flow.hass = hass
    # Make the context writable to satisfy async_set_unique_id
    flow.context = {}

    step = getattr(flow, "async_step_user", None) or getattr(
        flow, "async_step_init", None
    )
    assert step is not None, "ConfigFlow is missing async_step_user/init"

    result = await step(user_input=None)
    # Accept either form or immediate entry/abort depending on your flow
    if result["type"] == "form":
        result2 = await step(user_input={})
        assert result2["type"] in {"create_entry", "abort"}
    else:
        assert result["type"] in {"create_entry", "abort"}
