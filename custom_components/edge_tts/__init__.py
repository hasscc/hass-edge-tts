"""The Edge TTS integration."""
import logging
from aiohttp import web
from homeassistant.core import HomeAssistant
from homeassistant.const import Platform
from homeassistant.config_entries import ConfigEntry
from homeassistant.components.tts import async_create_stream
from homeassistant.components.http import HomeAssistantView, KEY_HASS, KEY_AUTHENTICATED
from .const import DOMAIN

_LOGGER = logging.getLogger(__name__)
PLATFORMS = [Platform.TTS]

async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up Edge TTS from a config entry."""
    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)

    entry.async_on_unload(entry.add_update_listener(options_update_listener))

    hass.http.register_view(EdgeTtsProxyView)
    hass.http.register_view(EdgeTtsProxyView(url="/api/tts_proxy/edge/{filename:.*}"))
    return True

async def options_update_listener(hass: HomeAssistant, entry: ConfigEntry) -> None:
    """Handle options update."""
    await hass.config_entries.async_reload(entry.entry_id)

async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a config entry."""
    return await hass.config_entries.async_unload_platforms(entry, PLATFORMS)


class EdgeTtsProxyView(HomeAssistantView):
    requires_auth = False
    cors_allowed = True
    url = "/api/tts_proxy/edge"
    name = "api:tts_proxy_edge"

    def __init__(self, url=None):
        if url:
            self.url = url

    async def get(self, request: web.Request, **kwargs) -> web.StreamResponse:
        hass = request.app[KEY_HASS]
        domain_data = hass.data.setdefault(DOMAIN, {})
        access_token = request.query.get("token")
        authenticated = request.get(KEY_AUTHENTICATED)
        if not authenticated and access_token:
            authenticated = access_token in domain_data.get("access_tokens", {}).values()
        if not authenticated:
            raise web.HTTPUnauthorized
        if not (message := request.query.get("message")):
            return self.json({"error": "message empty"}, 400)

        try:
            stream = async_create_stream(
                hass, domain_data.get("tts_entity_id", "tts.edge_tts"),
                language=request.query.get("language"),
                options={
                    "rate": request.query.get("rate", "+0%").replace(" ", "+"),
                    "volume": request.query.get("volume", "+10%").replace(" ", "+"),
                },
            )
        except Exception as err:
            return self.json({"error": err}, 400)

        stream.async_set_message(message)
        response: web.StreamResponse | None = None
        try:
            async for data in stream.async_stream_result():
                if response is None:
                    response = web.StreamResponse()
                    response.content_type = stream.content_type
                    await response.prepare(request)
                await response.write(data)
        except Exception as err:
            _LOGGER.error("Error streaming tts: %s", err)
        if response is None:
            return web.Response(status=500)
        await response.write_eof()
        return response
