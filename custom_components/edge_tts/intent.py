import logging
import voluptuous as vol

from homeassistant.core import HomeAssistant
from homeassistant.const import Platform
from homeassistant.helpers import intent
from homeassistant.helpers.network import get_url
from homeassistant.components.tts.const import DATA_TTS_MANAGER
from homeassistant.exceptions import HomeAssistantError

from .const import DOMAIN


_LOGGER = logging.getLogger(__name__)


async def async_setup_intents(hass: HomeAssistant):
    """Set up the intents."""
    intent.async_register(hass, ConvertTextToSound())
    intents = hass.data.get("intent") or {}
    _LOGGER.info("Setup intents: %s", intents.keys())


class ConvertTextToSound(intent.IntentHandler):
    intent_type = "ConvertTextToSound"
    description = "Convert text to sound url"
    slot_schema = {
        vol.Required("message", description="The text to speak"): intent.non_empty_string,
        vol.Optional("engine", description=f"TTS engine, default: `{DOMAIN}`"): str,
    }

    async def async_handle(self, intent_obj: intent.Intent):
        """Handle the intent."""
        hass = intent_obj.hass
        slots = self.async_validate_slots(intent_obj.slots)
        message = slots.get("message", {}).get("value")
        engine = slots.get("engine", {}).get("value") or DOMAIN
        response = intent_obj.create_response()

        if not (state := hass.states.get(f"tts.{engine}")):
            for sta in hass.states.all(Platform.TTS):
                if sta.entity_id.startswith(f"tts.{engine}"):
                    state = sta
                    break
                name = sta.attributes.get("friendly_name")
                if name and engine in name:
                    state = sta
                    break
        if not state:
            response.response_type = intent.IntentResponseType.ERROR
            response.async_set_error(
                code=intent.IntentResponseErrorCode.NO_VALID_TARGETS,
                message=f"TTS engine '{engine}' not found",
            )
            return response

        manager = hass.data[DATA_TTS_MANAGER]
        try:
            stream = manager.async_create_result_stream(state.entity_id)
        except HomeAssistantError as err:
            _LOGGER.error("Error on create result stream: %s", err)
            response.response_type = intent.IntentResponseType.ERROR
            response.async_set_error(
                code=intent.IntentResponseErrorCode.NO_VALID_TARGETS,
                message=str(err),
            )
            return response

        stream.async_set_message(message)
        url = get_url(manager.hass, prefer_external=True) + stream.url

        response.response_type = intent.IntentResponseType.ACTION_DONE
        response.async_set_speech_slots({
            "tts_url": url,
        })
        return response
