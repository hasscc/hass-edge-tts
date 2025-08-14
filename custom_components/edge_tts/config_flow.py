import voluptuous as vol
from homeassistant import config_entries
from homeassistant.core import callback
from homeassistant.components.tts import CONF_LANG
from .const import DOMAIN, CONF_VOICE, SUPPORTED_VOICES
from homeassistant.helpers.selector import SelectSelector, SelectSelectorConfig, SelectSelectorMode

SUPPORTED_LANGUAGES_LIST = {
    **dict(zip(SUPPORTED_VOICES.values(), SUPPORTED_VOICES.keys())),
    'zh-CN': 'zh-CN-XiaoxiaoNeural',
}

SUPPORTED_LANGUAGES = list([*SUPPORTED_LANGUAGES_LIST.keys(), *SUPPORTED_VOICES.keys()])

DEFAULT_LANG = 'zh-CN'


class EdgeTTSConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Edge TTS config flow."""

    async def async_step_user(self, user_input=None):
        """Handle a flow initiated by the user."""
        # 检查是否已经有配置条目
        if self._async_current_entries():
            return self.async_abort(reason="single_instance_allowed")

        # 创建一个空的配置条目
        return self.async_create_entry(title="Edge TTS", data={})

    @staticmethod
    @callback
    def async_get_options_flow(config_entry):
        """Get the options flow for this handler."""
        return EdgeTTSOptionsFlowHandler(config_entry)

class EdgeTTSOptionsFlowHandler(config_entries.OptionsFlow):
    """Handle an options flow for Edge TTS."""

    def __init__(self, config_entry):
        """Initialize options flow."""
        self._config_entry = config_entry

    async def async_step_init(self, user_input=None):
        """Manage the options."""
        if user_input is not None:
            # 更新配置到 hass.data
            self.hass.data[DOMAIN] = user_input
            return self.async_create_entry(title="Edge TTS Options", data=user_input)

        # 默认值从现有配置中读取，如果不存在则使用默认值
        default_language = self._config_entry.options.get(CONF_LANG, "zh-CN")

        return self.async_show_form(
            step_id="init",
            data_schema=vol.Schema({
                vol.Required(
                    CONF_LANG, 
                    default=default_language): SelectSelector(
                    SelectSelectorConfig(
                        options=SUPPORTED_LANGUAGES,
                        multiple=False,translation_key=CONF_LANG
                    )
                ),
            })
        )
