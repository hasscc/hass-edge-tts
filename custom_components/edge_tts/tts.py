"""The speech service."""
import logging
from typing import Any

import homeassistant.helpers.config_validation as cv
import voluptuous as vol
from homeassistant.components.tts import (
    CONF_LANG,
    PLATFORM_SCHEMA,
    Provider,
    TextToSpeechEntity,
    TtsAudioType,
)
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.typing import ConfigType, DiscoveryInfoType

from . import DOMAIN

EDGE_TTS_VERSION = '7.0.2'
try:
    import edge_tts
    if '__version__' not in dir(edge_tts) or edge_tts.__version__ != EDGE_TTS_VERSION:
        raise Exception(f"edge_tts version is not {EDGE_TTS_VERSION}. Please install edge_tts {EDGE_TTS_VERSION}.")
    import edge_tts.exceptions
except ImportError:
    try:
        import edgeTTS
        raise Exception(f'Please uninstall edgeTTS and install edge_tts {EDGE_TTS_VERSION} instead.')
    except ImportError:
        raise Exception(f'edge_tts is required. Please install edge_tts {EDGE_TTS_VERSION}.')

_LOGGER = logging.getLogger(__name__)

# https://speech.platform.bing.com/consumer/speech/synthesize/readaloud/voices/list?trustedclienttoken=6A5AA1D4EAFF4E9FB37E23D68491D6F4
SUPPORTED_VOICES = {
    'zh-CN-XiaoxiaoNeural': 'zh-CN',
    'zh-CN-XiaoyiNeural': 'zh-CN',
    'zh-CN-YunjianNeural': 'zh-CN',
    'zh-CN-YunxiNeural': 'zh-CN',
    'zh-CN-YunxiaNeural': 'zh-CN',
    'zh-CN-YunyangNeural': 'zh-CN',
    'zh-HK-HiuGaaiNeural': 'zh-HK',
    'zh-HK-HiuMaanNeural': 'zh-HK',
    'zh-HK-WanLungNeural': 'zh-HK',
    'zh-TW-HsiaoChenNeural': 'zh-TW',
    'zh-TW-YunJheNeural': 'zh-TW',
    'zh-TW-HsiaoYuNeural': 'zh-TW',
    'af-ZA-AdriNeural': 'af-ZA',
    'af-ZA-WillemNeural': 'af-ZA',
    'am-ET-AmehaNeural': 'am-ET',
    'am-ET-MekdesNeural': 'am-ET',
    'ar-AE-FatimaNeural': 'ar-AE',
    'ar-AE-HamdanNeural': 'ar-AE',
    'ar-BH-AliNeural': 'ar-BH',
    'ar-BH-LailaNeural': 'ar-BH',
    'ar-DZ-AminaNeural': 'ar-DZ',
    'ar-DZ-IsmaelNeural': 'ar-DZ',
    'ar-EG-SalmaNeural': 'ar-EG',
    'ar-EG-ShakirNeural': 'ar-EG',
    'ar-IQ-BasselNeural': 'ar-IQ',
    'ar-IQ-RanaNeural': 'ar-IQ',
    'ar-JO-SanaNeural': 'ar-JO',
    'ar-JO-TaimNeural': 'ar-JO',
    'ar-KW-FahedNeural': 'ar-KW',
    'ar-KW-NouraNeural': 'ar-KW',
    'ar-LB-LaylaNeural': 'ar-LB',
    'ar-LB-RamiNeural': 'ar-LB',
    'ar-LY-ImanNeural': 'ar-LY',
    'ar-LY-OmarNeural': 'ar-LY',
    'ar-MA-JamalNeural': 'ar-MA',
    'ar-MA-MounaNeural': 'ar-MA',
    'ar-OM-AbdullahNeural': 'ar-OM',
    'ar-OM-AyshaNeural': 'ar-OM',
    'ar-QA-AmalNeural': 'ar-QA',
    'ar-QA-MoazNeural': 'ar-QA',
    'ar-SA-HamedNeural': 'ar-SA',
    'ar-SA-ZariyahNeural': 'ar-SA',
    'ar-SY-AmanyNeural': 'ar-SY',
    'ar-SY-LaithNeural': 'ar-SY',
    'ar-TN-HediNeural': 'ar-TN',
    'ar-TN-ReemNeural': 'ar-TN',
    'ar-YE-MaryamNeural': 'ar-YE',
    'ar-YE-SalehNeural': 'ar-YE',
    'az-AZ-BabekNeural': 'az-AZ',
    'az-AZ-BanuNeural': 'az-AZ',
    'bg-BG-BorislavNeural': 'bg-BG',
    'bg-BG-KalinaNeural': 'bg-BG',
    'bn-BD-NabanitaNeural': 'bn-BD',
    'bn-BD-PradeepNeural': 'bn-BD',
    'bn-IN-BashkarNeural': 'bn-IN',
    'bn-IN-TanishaaNeural': 'bn-IN',
    'bs-BA-GoranNeural': 'bs-BA',
    'bs-BA-VesnaNeural': 'bs-BA',
    'ca-ES-EnricNeural': 'ca-ES',
    'ca-ES-JoanaNeural': 'ca-ES',
    'cs-CZ-AntoninNeural': 'cs-CZ',
    'cs-CZ-VlastaNeural': 'cs-CZ',
    'cy-GB-AledNeural': 'cy-GB',
    'cy-GB-NiaNeural': 'cy-GB',
    'da-DK-ChristelNeural': 'da-DK',
    'da-DK-JeppeNeural': 'da-DK',
    'de-AT-IngridNeural': 'de-AT',
    'de-AT-JonasNeural': 'de-AT',
    'de-CH-JanNeural': 'de-CH',
    'de-CH-LeniNeural': 'de-CH',
    'de-DE-AmalaNeural': 'de-DE',
    'de-DE-ConradNeural': 'de-DE',
    'de-DE-KatjaNeural': 'de-DE',
    'de-DE-SeraphinaMultilingualNeural': 'de-DE',
    'de-DE-KillianNeural': 'de-DE',
    'el-GR-AthinaNeural': 'el-GR',
    'el-GR-NestorasNeural': 'el-GR',
    'en-AU-NatashaNeural': 'en-AU',
    'en-AU-WilliamNeural': 'en-AU',
    'en-CA-ClaraNeural': 'en-CA',
    'en-CA-LiamNeural': 'en-CA',
    'en-GB-LibbyNeural': 'en-GB',
    'en-GB-MaisieNeural': 'en-GB',
    'en-GB-RyanNeural': 'en-GB',
    'en-GB-SoniaNeural': 'en-GB',
    'en-GB-ThomasNeural': 'en-GB',
    'en-HK-SamNeural': 'en-HK',
    'en-HK-YanNeural': 'en-HK',
    'en-IE-ConnorNeural': 'en-IE',
    'en-IE-EmilyNeural': 'en-IE',
    'en-IN-NeerjaNeural': 'en-IN',
    'en-IN-PrabhatNeural': 'en-IN',
    'en-KE-AsiliaNeural': 'en-KE',
    'en-KE-ChilembaNeural': 'en-KE',
    'en-NG-AbeoNeural': 'en-NG',
    'en-NG-EzinneNeural': 'en-NG',
    'en-NZ-MitchellNeural': 'en-NZ',
    'en-NZ-MollyNeural': 'en-NZ',
    'en-PH-JamesNeural': 'en-PH',
    'en-PH-RosaNeural': 'en-PH',
    'en-SG-LunaNeural': 'en-SG',
    'en-SG-WayneNeural': 'en-SG',
    'en-TZ-ElimuNeural': 'en-TZ',
    'en-TZ-ImaniNeural': 'en-TZ',
    'en-US-AnaNeural': 'en-US',
    'en-US-AriaNeural': 'en-US',
    'en-US-ChristopherNeural': 'en-US',
    'en-US-EricNeural': 'en-US',
    'en-US-GuyNeural': 'en-US',
    'en-US-JennyNeural': 'en-US',
    'en-US-MichelleNeural': 'en-US',
    'en-ZA-LeahNeural': 'en-ZA',
    'en-ZA-LukeNeural': 'en-ZA',
    'es-AR-ElenaNeural': 'es-AR',
    'es-AR-TomasNeural': 'es-AR',
    'es-BO-MarceloNeural': 'es-BO',
    'es-BO-SofiaNeural': 'es-BO',
    'es-CL-CatalinaNeural': 'es-CL',
    'es-CL-LorenzoNeural': 'es-CL',
    'es-CO-GonzaloNeural': 'es-CO',
    'es-CO-SalomeNeural': 'es-CO',
    'es-CR-JuanNeural': 'es-CR',
    'es-CR-MariaNeural': 'es-CR',
    'es-CU-BelkysNeural': 'es-CU',
    'es-CU-ManuelNeural': 'es-CU',
    'es-DO-EmilioNeural': 'es-DO',
    'es-DO-RamonaNeural': 'es-DO',
    'es-EC-AndreaNeural': 'es-EC',
    'es-EC-LuisNeural': 'es-EC',
    'es-ES-AlvaroNeural': 'es-ES',
    'es-ES-ElviraNeural': 'es-ES',
    'es-ES-ManuelEsCUNeural': 'es-ES',
    'es-GQ-JavierNeural': 'es-GQ',
    'es-GQ-TeresaNeural': 'es-GQ',
    'es-GT-AndresNeural': 'es-GT',
    'es-GT-MartaNeural': 'es-GT',
    'es-HN-CarlosNeural': 'es-HN',
    'es-HN-KarlaNeural': 'es-HN',
    'es-MX-DaliaNeural': 'es-MX',
    'es-MX-JorgeNeural': 'es-MX',
    'es-MX-LorenzoEsCLNeural': 'es-MX',
    'es-NI-FedericoNeural': 'es-NI',
    'es-NI-YolandaNeural': 'es-NI',
    'es-PA-MargaritaNeural': 'es-PA',
    'es-PA-RobertoNeural': 'es-PA',
    'es-PE-AlexNeural': 'es-PE',
    'es-PE-CamilaNeural': 'es-PE',
    'es-PR-KarinaNeural': 'es-PR',
    'es-PR-VictorNeural': 'es-PR',
    'es-PY-MarioNeural': 'es-PY',
    'es-PY-TaniaNeural': 'es-PY',
    'es-SV-LorenaNeural': 'es-SV',
    'es-SV-RodrigoNeural': 'es-SV',
    'es-US-AlonsoNeural': 'es-US',
    'es-US-PalomaNeural': 'es-US',
    'es-UY-MateoNeural': 'es-UY',
    'es-UY-ValentinaNeural': 'es-UY',
    'es-VE-PaolaNeural': 'es-VE',
    'es-VE-SebastianNeural': 'es-VE',
    'et-EE-AnuNeural': 'et-EE',
    'et-EE-KertNeural': 'et-EE',
    'fa-IR-DilaraNeural': 'fa-IR',
    'fa-IR-FaridNeural': 'fa-IR',
    'fi-FI-HarriNeural': 'fi-FI',
    'fi-FI-NooraNeural': 'fi-FI',
    'fil-PH-AngeloNeural': 'fil-PH',
    'fil-PH-BlessicaNeural': 'fil-PH',
    'fr-BE-CharlineNeural': 'fr-BE',
    'fr-BE-GerardNeural': 'fr-BE',
    'fr-CA-AntoineNeural': 'fr-CA',
    'fr-CA-JeanNeural': 'fr-CA',
    'fr-CA-SylvieNeural': 'fr-CA',
    'fr-CH-ArianeNeural': 'fr-CH',
    'fr-CH-FabriceNeural': 'fr-CH',
    'fr-FR-DeniseNeural': 'fr-FR',
    'fr-FR-EloiseNeural': 'fr-FR',
    'fr-FR-HenriNeural': 'fr-FR',
    'ga-IE-ColmNeural': 'ga-IE',
    'ga-IE-OrlaNeural': 'ga-IE',
    'gl-ES-RoiNeural': 'gl-ES',
    'gl-ES-SabelaNeural': 'gl-ES',
    'gu-IN-DhwaniNeural': 'gu-IN',
    'gu-IN-NiranjanNeural': 'gu-IN',
    'he-IL-AvriNeural': 'he-IL',
    'he-IL-HilaNeural': 'he-IL',
    'hi-IN-MadhurNeural': 'hi-IN',
    'hi-IN-SwaraNeural': 'hi-IN',
    'hr-HR-GabrijelaNeural': 'hr-HR',
    'hr-HR-SreckoNeural': 'hr-HR',
    'hu-HU-NoemiNeural': 'hu-HU',
    'hu-HU-TamasNeural': 'hu-HU',
    'id-ID-ArdiNeural': 'id-ID',
    'id-ID-GadisNeural': 'id-ID',
    'is-IS-GudrunNeural': 'is-IS',
    'is-IS-GunnarNeural': 'is-IS',
    'it-IT-DiegoNeural': 'it-IT',
    'it-IT-ElsaNeural': 'it-IT',
    'it-IT-IsabellaNeural': 'it-IT',
    'ja-JP-KeitaNeural': 'ja-JP',
    'ja-JP-NanamiNeural': 'ja-JP',
    'jv-ID-DimasNeural': 'jv-ID',
    'jv-ID-SitiNeural': 'jv-ID',
    'ka-GE-EkaNeural': 'ka-GE',
    'ka-GE-GiorgiNeural': 'ka-GE',
    'kk-KZ-AigulNeural': 'kk-KZ',
    'kk-KZ-DauletNeural': 'kk-KZ',
    'km-KH-PisethNeural': 'km-KH',
    'km-KH-SreymomNeural': 'km-KH',
    'kn-IN-GaganNeural': 'kn-IN',
    'kn-IN-SapnaNeural': 'kn-IN',
    'ko-KR-InJoonNeural': 'ko-KR',
    'ko-KR-SunHiNeural': 'ko-KR',
    'lo-LA-ChanthavongNeural': 'lo-LA',
    'lo-LA-KeomanyNeural': 'lo-LA',
    'lt-LT-LeonasNeural': 'lt-LT',
    'lt-LT-OnaNeural': 'lt-LT',
    'lv-LV-EveritaNeural': 'lv-LV',
    'lv-LV-NilsNeural': 'lv-LV',
    'mk-MK-AleksandarNeural': 'mk-MK',
    'mk-MK-MarijaNeural': 'mk-MK',
    'ml-IN-MidhunNeural': 'ml-IN',
    'ml-IN-SobhanaNeural': 'ml-IN',
    'mn-MN-BataaNeural': 'mn-MN',
    'mn-MN-YesuiNeural': 'mn-MN',
    'mr-IN-AarohiNeural': 'mr-IN',
    'mr-IN-ManoharNeural': 'mr-IN',
    'ms-MY-OsmanNeural': 'ms-MY',
    'ms-MY-YasminNeural': 'ms-MY',
    'mt-MT-GraceNeural': 'mt-MT',
    'mt-MT-JosephNeural': 'mt-MT',
    'my-MM-NilarNeural': 'my-MM',
    'my-MM-ThihaNeural': 'my-MM',
    'nb-NO-FinnNeural': 'nb-NO',
    'nb-NO-PernilleNeural': 'nb-NO',
    'ne-NP-HemkalaNeural': 'ne-NP',
    'ne-NP-SagarNeural': 'ne-NP',
    'nl-BE-ArnaudNeural': 'nl-BE',
    'nl-BE-DenaNeural': 'nl-BE',
    'nl-NL-ColetteNeural': 'nl-NL',
    'nl-NL-FennaNeural': 'nl-NL',
    'nl-NL-MaartenNeural': 'nl-NL',
    'pl-PL-MarekNeural': 'pl-PL',
    'pl-PL-ZofiaNeural': 'pl-PL',
    'ps-AF-GulNawazNeural': 'ps-AF',
    'ps-AF-LatifaNeural': 'ps-AF',
    'pt-BR-AntonioNeural': 'pt-BR',
    'pt-BR-FranciscaNeural': 'pt-BR',
    'pt-PT-DuarteNeural': 'pt-PT',
    'pt-PT-RaquelNeural': 'pt-PT',
    'ro-RO-AlinaNeural': 'ro-RO',
    'ro-RO-EmilNeural': 'ro-RO',
    'ru-RU-DmitryNeural': 'ru-RU',
    'ru-RU-SvetlanaNeural': 'ru-RU',
    'si-LK-SameeraNeural': 'si-LK',
    'si-LK-ThiliniNeural': 'si-LK',
    'sk-SK-LukasNeural': 'sk-SK',
    'sk-SK-ViktoriaNeural': 'sk-SK',
    'sl-SI-PetraNeural': 'sl-SI',
    'sl-SI-RokNeural': 'sl-SI',
    'so-SO-MuuseNeural': 'so-SO',
    'so-SO-UbaxNeural': 'so-SO',
    'sq-AL-AnilaNeural': 'sq-AL',
    'sq-AL-IlirNeural': 'sq-AL',
    'sr-RS-NicholasNeural': 'sr-RS',
    'sr-RS-SophieNeural': 'sr-RS',
    'su-ID-JajangNeural': 'su-ID',
    'su-ID-TutiNeural': 'su-ID',
    'sv-SE-MattiasNeural': 'sv-SE',
    'sv-SE-SofieNeural': 'sv-SE',
    'sw-KE-RafikiNeural': 'sw-KE',
    'sw-KE-ZuriNeural': 'sw-KE',
    'sw-TZ-DaudiNeural': 'sw-TZ',
    'sw-TZ-RehemaNeural': 'sw-TZ',
    'ta-IN-PallaviNeural': 'ta-IN',
    'ta-IN-ValluvarNeural': 'ta-IN',
    'ta-LK-KumarNeural': 'ta-LK',
    'ta-LK-SaranyaNeural': 'ta-LK',
    'ta-MY-KaniNeural': 'ta-MY',
    'ta-MY-SuryaNeural': 'ta-MY',
    'ta-SG-AnbuNeural': 'ta-SG',
    'ta-SG-VenbaNeural': 'ta-SG',
    'te-IN-MohanNeural': 'te-IN',
    'te-IN-ShrutiNeural': 'te-IN',
    'th-TH-NiwatNeural': 'th-TH',
    'th-TH-PremwadeeNeural': 'th-TH',
    'tr-TR-AhmetNeural': 'tr-TR',
    'tr-TR-EmelNeural': 'tr-TR',
    'uk-UA-OstapNeural': 'uk-UA',
    'uk-UA-PolinaNeural': 'uk-UA',
    'ur-IN-GulNeural': 'ur-IN',
    'ur-IN-SalmanNeural': 'ur-IN',
    'ur-PK-AsadNeural': 'ur-PK',
    'ur-PK-UzmaNeural': 'ur-PK',
    'uz-UZ-MadinaNeural': 'uz-UZ',
    'uz-UZ-SardorNeural': 'uz-UZ',
    'vi-VN-HoaiMyNeural': 'vi-VN',
    'vi-VN-NamMinhNeural': 'vi-VN',
    'zu-ZA-ThandoNeural': 'zu-ZA',
    'zu-ZA-ThembaNeural': 'zu-ZA',
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
    """Set up both the legacy provider and new entity for Edge TTS."""
    # Try to create the entity for tts.speak support
    # This is a workaround since async_setup_platform might not be called automatically
    from homeassistant.helpers import entity_platform
    from homeassistant.helpers.entity_component import EntityComponent
    
    try:
        # Check if we already created the entity
        if DOMAIN not in hass.data:
            hass.data[DOMAIN] = {}
        
        if not hass.data[DOMAIN].get("entity_created", False):
            # Create the TTS entity
            entity = EdgeTTSEntity(hass, config)
            
            # Try to get the TTS component
            component = hass.data.get("component_tts")
            if component is None:
                # Create a minimal component if it doesn't exist
                component = EntityComponent(_LOGGER, "tts", hass)
                hass.data["component_tts"] = component
            
            # Add the entity
            await component.async_add_entities([entity])
            hass.data[DOMAIN]["entity_created"] = True
            _LOGGER.info("Edge TTS entity created successfully")
    except Exception as e:
        _LOGGER.warning("Could not create Edge TTS entity: %s", e)
    
    # Always return the provider for backward compatibility
    return SpeechProvider(hass, config)


class SpeechProvider(Provider):
    """The provider."""

    def __init__(self, hass, config):
        """Init service."""
        self.name = 'Edge TTS'
        self.hass = hass
        self._config = config or {}
        self._style_options = ['style', 'styledegree', 'role']  # issues/8
        self._prosody_options = ['pitch', 'rate', 'volume']     # issues/24

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
        for f in self._style_options:
            v = opt.get(f)
            if v is not None:
                _LOGGER.warning(
                    'Edge TTS options style/styledegree/role are no longer supported, '
                    'please remove them from your automation or script. '
                    'See: https://github.com/hasscc/hass-edge-tts/issues/8'
                )
                break

        _LOGGER.debug('%s: %s', self.name, [message, opt])
        mp3 = b''
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
                    _LOGGER.debug('%s: audio.metadata: %s', self.name, chunk)
        except edge_tts.exceptions.NoAudioReceived:
            _LOGGER.warning('%s: failed: %s', self.name, [message, opt])
            return None, None
        return 'mp3', mp3

    def get_tts_audio(self, message, language, options=None):
        """Load tts audio file from provider."""
        return None, None


class EdgeCommunicate(edge_tts.Communicate):
    """ Edge TTS """


class EdgeTTSEntity(TextToSpeechEntity):
    """The Edge TTS entity."""

    _attr_name = "Edge TTS"
    _attr_unique_id = "edge_tts_entity"

    def __init__(self, hass: HomeAssistant, config: dict) -> None:
        """Initialize Edge TTS entity."""
        self.hass = hass
        self._config = config
        self._style_options = ['style', 'styledegree', 'role']  # issues/8
        self._prosody_options = ['pitch', 'rate', 'volume']     # issues/24
        
        # Set entity ID
        self.entity_id = f"tts.{DOMAIN}"
        
        # Set default language
        self._attr_default_language = config.get(CONF_LANG, DEFAULT_LANG)
        
        # Set supported languages
        self._attr_supported_languages = list([*SUPPORTED_LANGUAGES.keys(), *SUPPORTED_VOICES.keys()])
        
        # Set supported options
        self._attr_supported_options = ['voice'] + self._prosody_options

    async def async_get_tts_audio(
        self, message: str, language: str, options: dict[str, Any] | None = None
    ) -> TtsAudioType:
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
        for f in self._style_options:
            v = opt.get(f)
            if v is not None:
                _LOGGER.warning(
                    'Edge TTS options style/styledegree/role are no longer supported, '
                    'please remove them from your automation or script. '
                    'See: https://github.com/hasscc/hass-edge-tts/issues/8'
                )
                break

        _LOGGER.debug('Edge TTS: %s', [message, opt])
        mp3 = b''
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
                    _LOGGER.debug('Edge TTS: audio.metadata: %s', chunk)
        except edge_tts.exceptions.NoAudioReceived:
            _LOGGER.warning('Edge TTS: failed: %s', [message, opt])
            return None, None
        return 'mp3', mp3


async def async_setup_platform(
    hass: HomeAssistant,
    config: ConfigType,
    async_add_entities: AddEntitiesCallback,
    discovery_info: dict | None = None,
) -> None:
    """Set up Edge TTS entity from YAML configuration.
    
    This creates the new TTS entity that supports tts.speak action.
    The legacy provider (for tts.edge_tts_say) is set up via async_get_engine.
    """
    # Create the TTS entity for tts.speak support
    entity = EdgeTTSEntity(hass, config)
    async_add_entities([entity], True)
