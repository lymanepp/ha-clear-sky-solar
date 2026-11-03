"""Config flow for Clear-Sky Solar integration."""

from typing import Any

from homeassistant.config_entries import ConfigFlow, ConfigFlowResult

from .const import DOMAIN


class ClearSkySolarConfigFlow(ConfigFlow, domain=DOMAIN):
    """Handle a config flow for Clear-Sky Solar."""

    VERSION = 1

    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> ConfigFlowResult:
        """Handle the initial step."""
        if user_input is None:
            return self.async_show_form(step_id="user")

        return self.async_create_entry(title="Clear-Sky Solar", data={})
