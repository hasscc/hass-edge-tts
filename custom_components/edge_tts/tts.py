"""The speech service."""
import logging
import voluptuous as vol
import homeassistant.helpers.config_validation as cv
from homeassistant.components.tts import CONF_LANG, PLATFORM_SCHEMA, Provider
from edgeTTS import Communicate

_LOGGER = logging.getLogger(__name__)

# https://speech.platform.bing.com/consumer/speech/synthesize/readaloud/voices/list?trustedclienttoken=6A5AA1D4EAFF4E9FB37E23D68491D6F4
SUPPORTED_LANGUAGES = {
    'zh-CN': 'zh-CN-XiaoxiaoNeural',
    'zh-HK': 'zh-HK-HiuMaanNeural',
    'zh-TW': 'zh-TW-HsiaoChenNeural',
    'ar-EG': 'ar-EG-SalmaNeural',
    'ar-SA': 'ar-SA-ZariyahNeural',
    'bg-BG': 'bg-BG-KalinaNeural',
    'ca-ES': 'ca-ES-JoanaNeural',
    'cs-CZ': 'cs-CZ-VlastaNeural',
    'cy-GB': 'cy-GB-NiaNeural',
    'da-DK': 'da-DK-ChristelNeural',
    'de-AT': 'de-AT-IngridNeural',
    'de-CH': 'de-CH-LeniNeural',
    'de-DE': 'de-DE-KatjaNeural',
    'el-GR': 'el-GR-AthinaNeural',
    'en-AU': 'en-AU-NatashaNeural',
    'en-CA': 'en-CA-ClaraNeural',
    'en-GB': 'en-GB-MiaNeural',
    'en-IE': 'en-IE-EmilyNeural',
    'en-IN': 'en-IN-NeerjaNeural',
    'en-PH': 'en-PH-RosaNeural',
    'en-US': 'en-US-AriaNeural',
    'en-ZA': 'en-ZA-LeahNeural',
    'es-AR': 'es-AR-ElenaNeural',
    'es-CO': 'es-CO-SalomeNeural',
    'es-ES': 'es-ES-ElviraNeural',
    'es-MX': 'es-MX-DaliaNeural',
    'et-EE': 'et-EE-AnuNeural',
    'fi-FI': 'fi-FI-NooraNeural',
    'fr-BE': 'fr-BE-CharlineNeural',
    'fr-CA': 'fr-CA-SylvieNeural',
    'fr-CH': 'fr-CH-ArianeNeural',
    'fr-FR': 'fr-FR-DeniseNeural',
    'ga-IE': 'ga-IE-OrlaNeural',
    'gu-IN': 'gu-IN-DhwaniNeural',
    'he-IL': 'he-IL-HilaNeural',
    'hi-IN': 'hi-IN-SwaraNeural',
    'hr-HR': 'hr-HR-GabrijelaNeural',
    'hu-HU': 'hu-HU-NoemiNeural',
    'id-ID': 'id-ID-GadisNeural',
    'it-IT': 'it-IT-ElsaNeural',
    'ja-JP': 'ja-JP-NanamiNeural',
    'ko-KR': 'ko-KR-SunHiNeural',
    'lt-LT': 'lt-LT-OnaNeural',
    'lv-LV': 'lv-LV-EveritaNeural',
    'mr-IN': 'mr-IN-AarohiNeural',
    'ms-MY': 'ms-MY-YasminNeural',
    'mt-MT': 'mt-MT-GraceNeural',
    'nb-NO': 'nb-NO-PernilleNeural',
    'nl-BE': 'nl-BE-DenaNeural',
    'nl-NL': 'nl-NL-ColetteNeural',
    'pl-PL': 'pl-PL-ZofiaNeural',
    'pt-BR': 'pt-BR-FranciscaNeural',
    'pt-PT': 'pt-PT-RaquelNeural',
    'ro-RO': 'ro-RO-AlinaNeural',
    'ru-RU': 'ru-RU-SvetlanaNeural',
    'sk-SK': 'sk-SK-ViktoriaNeural',
    'sl-SI': 'sl-SI-PetraNeural',
    'sv-SE': 'sv-SE-SofieNeural',
    'sw-KE': 'sw-KE-ZuriNeural',
    'ta-IN': 'ta-IN-PallaviNeural',
    'te-IN': 'te-IN-ShrutiNeural',
    'th-TH': 'th-TH-PremwadeeNeural',
    'tr-TR': 'tr-TR-EmelNeural',
    'uk-UA': 'uk-UA-PolinaNeural',
    'ur-PK': 'ur-PK-UzmaNeural',
    'vi-VN': 'vi-VN-HoaiMyNeural',
}

DEFAULT_LANG = 'zh-CN'

PLATFORM_SCHEMA = PLATFORM_SCHEMA.extend(
    {
        vol.Optional(CONF_LANG, default=DEFAULT_LANG): cv.string,
    },
    extra=vol.ALLOW_EXTRA,
)


async def async_get_engine(hass, config, discovery_info=None):
    """"Set up the component."""
    return SpeechProvider(hass, config)


class SpeechProvider(Provider):
    """The provider."""

    def __init__(self, hass, config):
        """Init service."""
        self.name = 'Edge TTS'
        self.hass = hass
        self._config = config or {}

    @property
    def default_language(self):
        """Return the default language."""
        return self._config.get(CONF_LANG)

    @property
    def supported_languages(self):
        """Return list of supported languages."""
        return SUPPORTED_LANGUAGES

    @property
    def supported_options(self):
        """Return a list of supported options like voice, emotionen."""
        return [CONF_LANG, 'voice', 'style', 'styledegree', 'role', 'pitch', 'rate', 'volume']

    async def async_get_tts_audio(self, message, language, options=None):
        """Load TTS audio."""
        opt = {**self._config, **{CONF_LANG: language}, **(options or {})}

        # https://docs.microsoft.com/zh-CN/azure/cognitive-services/speech-service/speech-synthesis-markup?tabs=csharp#adjust-speaking-languages
        lang = opt.get(CONF_LANG) or language

        # https://docs.microsoft.com/zh-CN/azure/cognitive-services/speech-service/speech-synthesis-markup?tabs=csharp#use-multiple-voices
        voice = opt.get('voice') or SUPPORTED_LANGUAGES.get(lang) or 'zh-CN-XiaoxiaoNeural'

        # https://docs.microsoft.com/zh-CN/azure/cognitive-services/speech-service/speech-synthesis-markup?tabs=csharp#adjust-speaking-styles
        express = []
        for f in ['style', 'styledegree', 'role']:
            v = opt.get(f)
            if v is not None:
                express.append(f'{f}="{v}"')
        if express:
            express = ' '.join(express)
            message = f'<mstts:express-as {express}>{message}</mstts:express-as>'

        # https://docs.microsoft.com/zh-CN/azure/cognitive-services/speech-service/speech-synthesis-markup?tabs=csharp#adjust-prosody
        pitch = opt.get('pitch') or '+0Hz'
        rate = opt.get('rate') or '+0%'
        volume = opt.get('volume') or '+0%'

        xml = '<speak version="1.0"' \
              ' xmlns="http://www.w3.org/2001/10/synthesis"' \
              ' xmlns:mstts="https://www.w3.org/2001/mstts"' \
              f' xml:lang="{lang}">' \
              f'<voice name="{voice}">' \
              f'<prosody pitch="{pitch}" rate="{rate}" volume="{volume}">' \
              f'{message}</prosody></voice></speak>'
        _LOGGER.debug('%s: %s', self.name, xml)
        mp3 = b''
        tts = EdgeCommunicate()
        async for i in tts.run(
            xml,
            customspeak=True,
        ):
            # 0 - offset
            # 1 - text
            # 2 - binary
            if i[2] is not None:
                mp3 += i[2]
            elif i[0] is not None:
                _LOGGER.debug('%s: audio.metadata: %s', self.name, i)
        if not mp3:
            _LOGGER.warning('%s: failed: %s', self.name, xml)
            return None, None
        return 'mp3', mp3

    def get_tts_audio(self, message, language, options=None):
        """Load tts audio file from provider."""
        return None, None


class EdgeCommunicate(Communicate):
    """ Edge TTS """
