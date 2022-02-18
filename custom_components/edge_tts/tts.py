"""The speech service."""
import logging
import voluptuous as vol
import homeassistant.helpers.config_validation as cv
from homeassistant.components.tts import CONF_LANG, PLATFORM_SCHEMA, Provider
from edge_tts import Communicate

_LOGGER = logging.getLogger(__name__)

# https://speech.platform.bing.com/consumer/speech/synthesize/readaloud/voices/list?trustedclienttoken=6A5AA1D4EAFF4E9FB37E23D68491D6F4
SUPPORTED_VOICES = {
    'zh-CN-XiaoxiaoNeural': 'zh-CN',
    'zh-CN-YunyangNeural': 'zh-CN',
    'zh-CN-YunyeNeural': 'zh-CN',
    'zh-CN-YunxiNeural': 'zh-CN',
    'zh-CN-XiaohanNeural': 'zh-CN',
    'zh-CN-XiaomoNeural': 'zh-CN',
    'zh-CN-XiaoxuanNeural': 'zh-CN',
    'zh-CN-XiaoruiNeural': 'zh-CN',
    'zh-HK-HiuMaanNeural': 'zh-HK',
    'zh-TW-HsiaoChenNeural': 'zh-TW',
    'ar-EG-SalmaNeural': 'ar-EG',
    'ar-SA-ZariyahNeural': 'ar-SA',
    'bg-BG-KalinaNeural': 'bg-BG',
    'ca-ES-JoanaNeural': 'ca-ES',
    'cs-CZ-VlastaNeural': 'cs-CZ',
    'cy-GB-NiaNeural': 'cy-GB',
    'da-DK-ChristelNeural': 'da-DK',
    'de-AT-IngridNeural': 'de-AT',
    'de-CH-LeniNeural': 'de-CH',
    'de-DE-KatjaNeural': 'de-DE',
    'el-GR-AthinaNeural': 'el-GR',
    'en-AU-NatashaNeural': 'en-AU',
    'en-CA-ClaraNeural': 'en-CA',
    'en-GB-MiaNeural': 'en-GB',
    'en-IE-EmilyNeural': 'en-IE',
    'en-IN-NeerjaNeural': 'en-IN',
    'en-PH-RosaNeural': 'en-PH',
    'en-US-AriaNeural': 'en-US',
    'en-US-GuyNeural': 'en-US',
    'en-US-JennyNeural': 'en-US',
    'en-ZA-LeahNeural': 'en-ZA',
    'es-AR-ElenaNeural': 'es-AR',
    'es-CO-SalomeNeural': 'es-CO',
    'es-ES-ElviraNeural': 'es-ES',
    'es-MX-DaliaNeural': 'es-MX',
    'et-EE-AnuNeural': 'et-EE',
    'fi-FI-NooraNeural': 'fi-FI',
    'fr-BE-CharlineNeural': 'fr-BE',
    'fr-CA-SylvieNeural': 'fr-CA',
    'fr-CH-ArianeNeural': 'fr-CH',
    'fr-FR-DeniseNeural': 'fr-FR',
    'ga-IE-OrlaNeural': 'ga-IE',
    'gu-IN-DhwaniNeural': 'gu-IN',
    'he-IL-HilaNeural': 'he-IL',
    'hi-IN-SwaraNeural': 'hi-IN',
    'hr-HR-GabrijelaNeural': 'hr-HR',
    'hu-HU-NoemiNeural': 'hu-HU',
    'id-ID-GadisNeural': 'id-ID',
    'it-IT-ElsaNeural': 'it-IT',
    'ja-JP-NanamiNeural': 'ja-JP',
    'ko-KR-SunHiNeural': 'ko-KR',
    'lt-LT-OnaNeural': 'lt-LT',
    'lv-LV-EveritaNeural': 'lv-LV',
    'mr-IN-AarohiNeural': 'mr-IN',
    'ms-MY-YasminNeural': 'ms-MY',
    'mt-MT-GraceNeural': 'mt-MT',
    'nb-NO-PernilleNeural': 'nb-NO',
    'nl-BE-DenaNeural': 'nl-BE',
    'nl-NL-ColetteNeural': 'nl-NL',
    'pl-PL-ZofiaNeural': 'pl-PL',
    'pt-BR-FranciscaNeural': 'pt-BR',
    'pt-PT-RaquelNeural': 'pt-PT',
    'ro-RO-AlinaNeural': 'ro-RO',
    'ru-RU-SvetlanaNeural': 'ru-RU',
    'sk-SK-ViktoriaNeural': 'sk-SK',
    'sl-SI-PetraNeural': 'sl-SI',
    'sv-SE-SofieNeural': 'sv-SE',
    'sw-KE-ZuriNeural': 'sw-KE',
    'ta-IN-PallaviNeural': 'ta-IN',
    'te-IN-ShrutiNeural': 'te-IN',
    'th-TH-PremwadeeNeural': 'th-TH',
    'tr-TR-EmelNeural': 'tr-TR',
    'uk-UA-PolinaNeural': 'uk-UA',
    'ur-PK-UzmaNeural': 'ur-PK',
    'vi-VN-HoaiMyNeural': 'vi-VN',
}
SUPPORTED_LANGUAGES = {
    **dict(zip(SUPPORTED_VOICES.values(), SUPPORTED_VOICES.keys())),
    'zh-CN': 'zh-CN-XiaoxiaoNeural',
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
        self._style_options = ['style', 'styledegree', 'role']
        self._prosody_options = ['pitch', 'contour', 'range', 'rate', 'duration', 'volume']

    @property
    def default_language(self):
        """Return the default language."""
        return self._config.get(CONF_LANG)

    @property
    def supported_languages(self):
        """Return list of supported languages."""
        return list([*SUPPORTED_LANGUAGES.keys(), *SUPPORTED_VOICES.keys()])

    @property
    def supported_options(self):
        """Return a list of supported options like voice, emotionen."""
        lst = [CONF_LANG, 'voice']
        lst.extend(self._style_options)
        lst.extend(self._prosody_options)
        return lst

    async def async_get_tts_audio(self, message, language, options=None):
        """Load TTS audio."""
        opt = {CONF_LANG: language}
        if language in SUPPORTED_VOICES:
            opt[CONF_LANG] = SUPPORTED_VOICES[language]
            opt['voice'] = language
        opt = {**self._config, **opt, **(options or {})}

        # https://docs.microsoft.com/zh-CN/azure/cognitive-services/speech-service/speech-synthesis-markup?tabs=csharp#adjust-speaking-languages
        lang = opt.get(CONF_LANG) or language

        # https://docs.microsoft.com/zh-CN/azure/cognitive-services/speech-service/speech-synthesis-markup?tabs=csharp#use-multiple-voices
        voice = opt.get('voice') or SUPPORTED_LANGUAGES.get(lang) or 'zh-CN-XiaoxiaoNeural'

        # https://docs.microsoft.com/zh-CN/azure/cognitive-services/speech-service/speech-synthesis-markup?tabs=csharp#adjust-speaking-styles
        express = []
        for f in self._style_options:
            v = opt.get(f)
            if v is not None:
                express.append(f'{f}="{v}"')
        if express:
            express = ' '.join(express)
            message = f'<mstts:express-as {express}>{message}</mstts:express-as>'

        # https://docs.microsoft.com/zh-CN/azure/cognitive-services/speech-service/speech-synthesis-markup?tabs=csharp#adjust-prosody
        prosodies = []
        for f in self._prosody_options:
            v = opt.get(f)
            if v is not None:
                prosodies.append(f'{f}="{v}"')
        if prosodies:
            prosodies = ' '.join(prosodies)
            message = f'<prosody {prosodies}>{message}</prosody>'

        xml = '<speak version="1.0"' \
              ' xmlns="http://www.w3.org/2001/10/synthesis"' \
              ' xmlns:mstts="https://www.w3.org/2001/mstts"' \
              f' xml:lang="{lang}">' \
              f'<voice name="{voice}">' \
              f'{message}</voice></speak>'
        _LOGGER.debug('%s: %s', self.name, xml)
        mp3 = b''
        tts = EdgeCommunicate()
        async for i in tts.run(
            xml,
            customspeak=True,
        ):
            # [offset, text, binary]
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
