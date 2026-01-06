"""Config flow for Edge TTS integration.

Minimal config flow that collects an optional voice setting and creates a config entry.
"""
from __future__ import annotations

import voluptuous as vol
from homeassistant import config_entries

from .const import DOMAIN, CONF_VOICE, DEFAULT_VOICE


class EdgeTTSConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for Edge TTS."""

    VERSION = 1

    async def async_step_user(self, user_input=None):
        """Handle the initial step."""
        errors = {}

        if user_input is not None:
            return self.async_create_entry(title="Edge TTS", data=user_input)

        data_schema = vol.Schema(
            {vol.Optional(CONF_VOICE, default=DEFAULT_VOICE): str}
        )

        return self.async_show_form(step_id="user", data_schema=data_schema, errors=errors)
