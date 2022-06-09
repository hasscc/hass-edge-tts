# Microsoft Edge TTS for Home Assistant

This component is based on the TTS service of Microsoft Edge browser, no need to apply for `app_key`.


## Install

> Download and copy `custom_components/edge_tts` folder to `custom_components` folder in your HomeAssistant config folder

```shell
# Auto install via terminal shell
wget -q -O - https://cdn.jsdelivr.net/gh/al-one/hass-xiaomi-miot/install.sh | DOMAIN=edge_tts REPO_PATH=hasscc/hass-edge-tts ARCHIVE_TAG=main bash -
```


## Config

```yaml
# configuration.yaml
tts:
  - platform: edge_tts
    language: zh-CN # Default language or voice (Optional)
```

#### Configure default options:
```yaml
tts:
  - platform: edge_tts
    service_name: xiaomo_say
    language: zh-CN-XiaomoNeural
    style: cheerful
    styledegree: 2
    role: Girl
    volume: 100.0
```

#### Supported languages

- [speaking languages](https://docs.microsoft.com/zh-CN/azure/cognitive-services/speech-service/speech-synthesis-markup?tabs=csharp#adjust-speaking-languages)
- [list of voices](https://github.com/hasscc/hass-edge-tts/blob/fb49c92435eb79a9e51435a0063c8470fd8da0cd/custom_components/edge_tts/tts.py#L15-L95)


## Using

- [![Call service: tts.edge_tts_say](https://my.home-assistant.io/badges/developer_call_service.svg)](https://my.home-assistant.io/redirect/developer_call_service/?service=tts.edge_tts_say)
- [REST API: /api/tts_get_url](https://www.home-assistant.io/integrations/tts#post-apitts_get_url)

### Options

- [`voice`](https://docs.microsoft.com/zh-CN/azure/cognitive-services/speech-service/speech-synthesis-markup?tabs=csharp#use-multiple-voices)
- [`style`](https://docs.microsoft.com/zh-CN/azure/cognitive-services/speech-service/speech-synthesis-markup?tabs=csharp#adjust-speaking-styles)
  - [Voice styles and roles](https://docs.microsoft.com/zh-CN/azure/cognitive-services/speech-service/language-support?tabs=speechtotext#voice-styles-and-roles)
- [`styledegree`](https://docs.microsoft.com/zh-CN/azure/cognitive-services/speech-service/speech-synthesis-markup?tabs=csharp#style-degree): 0.01 - 2, only for `zh-CN`
- [`role`](https://docs.microsoft.com/zh-CN/azure/cognitive-services/speech-service/speech-synthesis-markup?tabs=csharp#role): only for `zh-CN-XiaomoNeural` / `zh-CN-XiaoxuanNeural` / `zh-CN-YunxiNeural` / `zh-CN-YunyeNeural`
  - Girl
  - Boy
  - YoungAdultFemale
  - YoungAdultMale
  - OlderAdultFemale
  - OlderAdultMale
  - SeniorFemale
  - SeniorMale
- [`pitch` / `rate` / `volume` / `contour`](https://docs.microsoft.com/zh-CN/azure/cognitive-services/speech-service/speech-synthesis-markup?tabs=csharp#adjust-prosody)

### Basic example

```yaml
service: tts.edge_tts_say
data:
  entity_id: media_player.your_player_entity_id
  message: Hello
  language: zh-CN-XiaoxiaoNeural # Language or voice (Optional)

```

### Full example

```yaml
service: tts.edge_tts_say
data:
  entity_id: media_player.your_player_entity_id
  message: 吃葡萄不吐葡萄皮，不吃葡萄倒吐葡萄皮
  language: zh-CN
  cache: true
  options:
    voice: zh-CN-XiaomoNeural
    style: cheerful
    styledegree: 2
    role: Girl
    pitch: +0Hz
    rate: +0%
    volume: +10%
    contour: (60%,-60%) (100%,+80%)
    
```

### Curl example

```shell
curl -X POST -H "Authorization: Bearer <ACCESS TOKEN>" \
     -H "Content-Type: application/json" \
     -d '{"platform": "edge_tts", "message": "欢迎回家", "language": "zh-CN-XiaoxuanNeural", "cache": false, "options": {"style": "cheerful", "role": "Boy"}}' \
     http://home-assistant.local:8123/api/tts_get_url
```


## Thanks

- https://github.com/rany2/edge-tts
- https://github.com/ag2s20150909/TTS
