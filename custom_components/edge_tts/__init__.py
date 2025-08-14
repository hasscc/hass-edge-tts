"""The Edge TTS integration."""
import logging
import voluptuous as vol
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant, ServiceCall
import homeassistant.helpers.config_validation as cv
from homeassistant.components.tts import (
    ATTR_MESSAGE,
    DOMAIN as TTS_DOMAIN,
    ATTR_VOICE
)
from homeassistant.components.media_player import (
    DOMAIN as MEDIA_PLAYER_DOMAIN,
    SERVICE_PLAY_MEDIA,
    ATTR_MEDIA_CONTENT_ID,
    ATTR_MEDIA_CONTENT_TYPE,
)
from .const import DOMAIN

_LOGGER = logging.getLogger(__name__)

async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up Edge TTS from a config entry."""
    await hass.config_entries.async_forward_entry_setups(entry, [TTS_DOMAIN])

    entry.async_on_unload(entry.add_update_listener(options_update_listener))

    return True

async def options_update_listener(hass: HomeAssistant, entry: ConfigEntry) -> None:
    """Handle options update."""
    await hass.config_entries.async_reload(entry.entry_id)

async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a config entry."""
    hass.services.async_remove(DOMAIN, SERVICE_EDGE_SAY)
    return await hass.config_entries.async_forward_entry_unload(entry, TTS_DOMAIN)
