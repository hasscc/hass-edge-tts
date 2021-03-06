# Microsoft Edge TTS for Home Assistant

This component is based on the TTS service of Microsoft Edge browser, no need to apply for `app_key`.


## Install

> Download and copy `custom_components/edge_tts` folder to `custom_components` folder in your HomeAssistant config folder

```shell
# Auto install via terminal shell
wget -O - https://raw.githubusercontent.com/hasscc/get/main/get | DOMAIN=edge_tts REPO_PATH=hasscc/hass-edge-tts ARCHIVE_TAG=main bash -

# Or
wget -O - https://ghproxy.com/raw.githubusercontent.com/hasscc/get/main/get | HUB_DOMAIN=ghproxy.com/github.com DOMAIN=edge_tts REPO_PATH=hasscc/hass-edge-tts ARCHIVE_TAG=main bash -
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
    service_name: xiaomo_say # service: tts.xiaomo_say
    language: zh-CN-XiaomoNeural
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
- [`pitch` / `rate` / `volume`](https://docs.microsoft.com/zh-CN/azure/cognitive-services/speech-service/speech-synthesis-markup?tabs=csharp#adjust-prosody)

> `style` / `styledegree` / `role` / `contour` are no longer supported ([#8](https://github.com/hasscc/hass-edge-tts/issues/8)).

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
  message: ??????????????????????????????????????????????????????
  language: zh-CN
  cache: true
  options:
    voice: zh-CN-XiaomoNeural
    pitch: +0Hz
    rate: +0%
    volume: +10%
    
```

### Curl example

```shell
curl -X POST -H "Authorization: Bearer <ACCESS TOKEN>" \
     -H "Content-Type: application/json" \
     -d '{"platform": "edge_tts", "message": "????????????", "language": "zh-CN-XiaoxuanNeural", "cache": true, "options": {"volume": "+10%"}}' \
     http://home-assistant.local:8123/api/tts_get_url
```


## Thanks

- https://github.com/rany2/edge-tts
- https://github.com/ag2s20150909/TTS
