"""Config flow for Clear-Sky Solar integration."""

from typing import Any

from homeassistant.config_entries import ConfigFlow, ConfigFlowResult

from .const import DOMAIN


class ClearSkySolarConfigFlow(ConfigFlow, domain=DOMAIN):  # pylint: disable=abstract-method
    """Handle a config flow for Clear-Sky Solar."""

    VERSION = 1

    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> ConfigFlowResult:
        """Handle the initial step."""

        await self.async_set_unique_id(DOMAIN)
        self._abort_if_unique_id_configured()

        if user_input is None:
            return self.async_show_form(step_id="user")

        return self.async_create_entry(title="Clear-Sky Solar", data={})
