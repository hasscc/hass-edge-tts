"""The speech service."""
import logging
import time
from typing import Any
from homeassistant.exceptions import HomeAssistantError
from homeassistant.components.tts import (
    CONF_LANG,
    TextToSpeechEntity,
    TtsAudioType,
)
from homeassistant.core import HomeAssistant
from homeassistant.config_entries import ConfigEntry
from homeassistant.util import ulid
from homeassistant.helpers.device_registry import DeviceEntryType
from homeassistant.helpers.entity_platform import AddEntitiesCallback

import edge_tts
from .const import DOMAIN, SUPPORTED_VOICES, DEFAULT_LANG


_LOGGER = logging.getLogger(__name__)

SUPPORTED_LANGUAGES = {
    **dict(zip(SUPPORTED_VOICES.values(), SUPPORTED_VOICES.keys())),
    'zh-CN': 'zh-CN-XiaoxiaoNeural',
}

async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up Edge TTS entity from a config entry."""
    entity = EdgeTTSEntity(hass, config_entry)
    async_add_entities([entity])


class EdgeTTSEntity(TextToSpeechEntity):
    """The Edge TTS entity."""

    _attr_name = "Edge TTS"
    
    def __init__(self, hass: HomeAssistant, config_entry: ConfigEntry) -> None:
        """Initialize Edge TTS entity."""
        self.hass = hass
        self._config_entry = config_entry
        self._attr_unique_id = f"{config_entry.entry_id}-tts"

        self._attr_device_info = {
            "identifiers": {(DOMAIN, self._config_entry.entry_id)},
            "name": "Edge TTS Service",
            "manufacturer": "Edge TTS Community",
            "model": "Cloud TTS",
            "sw_version": edge_tts.__version__,
            "entry_type": DeviceEntryType.SERVICE,
        }
        self._attr_extra_state_attributes = {}

        # Prosody and style options
        self._prosody_options = ['pitch', 'rate', 'volume']
        self._style_options = ['style', 'styledegree', 'role']

    async def async_added_to_hass(self) -> None:
        domain_data = self.hass.data.setdefault(DOMAIN, {})
        domain_data["tts_entity_id"] = self.entity_id
        access_tokens = domain_data.setdefault("access_tokens", {
            "temp": ulid.ulid_hex(),
            "long": self.hass.data["core.uuid"],
        })
        self._attr_extra_state_attributes["access_tokens"] = access_tokens.copy()

    @property
    def default_language(self) -> str:
        """Return the default language from options."""
        return self._config_entry.options.get(CONF_LANG, DEFAULT_LANG)

    @property
    def supported_languages(self) -> list[str]:
        """Return list of supported languages."""
        return list([*SUPPORTED_LANGUAGES.keys(), *SUPPORTED_VOICES.keys()])

    @property
    def supported_options(self) -> list[str]:
        """Return a list of supported options."""
        return ['voice'] + self._prosody_options

    async def async_get_tts_audio(
        self, message: str, language: str, options: dict[str, Any] | None = None
    ) -> TtsAudioType:
        """Load TTS audio."""
        config = self._config_entry.options
        return await _process_tts_audio(
            message,
            language,
            config,
            self._style_options,
            self.name,
            options
        )


async def _process_tts_audio(
    message: str,
    language: str, 
    config: dict,
    style_options: list,
    name: str,
    options: dict[str, Any] | None = None,
) -> TtsAudioType:
    """Shared TTS processing logic for both SpeechProvider and EdgeTTSEntity."""
    opt = {CONF_LANG: language}
    if language in SUPPORTED_VOICES:
        opt[CONF_LANG] = SUPPORTED_VOICES[language]
        opt['voice'] = language
    opt = {**config, **opt, **(options or {})}

    lang = opt.get(CONF_LANG) or language or DEFAULT_LANG
    voice = opt.get('voice') or SUPPORTED_LANGUAGES.get(lang) or 'zh-CN-XiaoxiaoNeural'

    # 检查已弃用的样式选项
    for f in style_options:
        v = opt.get(f)
        if v is not None:
            _LOGGER.warning(
                'Edge TTS options style/styledegree/role are no longer supported, '
                'please remove them from your automation or script. '
                'See: https://github.com/hasscc/hass-edge-tts/issues/8'
            )
            break

    _LOGGER.debug('%s: %s', name, [message, opt])
    mp3 = b''
    start_time = time.perf_counter()
    tts = EdgeCommunicate(
        message,
        voice=voice,
        pitch=opt.get('pitch', '+0Hz'),
        rate=opt.get('rate', '+0%'),
        volume=opt.get('volume', '+0%'),
    )
    try:
        async for chunk in tts.stream():
            if chunk["type"] == "audio":
                mp3 += chunk["data"]
            else:
                _LOGGER.debug('%s: audio.metadata: %s', name, chunk)
    except edge_tts.exceptions.NoAudioReceived:
        _LOGGER.warning('%s: failed: %s', name, [message, opt])
        raise HomeAssistantError(f"{name} failed {message}")
    end_time = time.perf_counter()
    elapsed_time = (end_time - start_time) * 1000
    _LOGGER.info('load tts elapsed_time: %sms', elapsed_time)
    return 'mp3', mp3


class EdgeCommunicate(edge_tts.Communicate):
    """ Edge TTS """
