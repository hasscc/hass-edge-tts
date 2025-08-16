# Microsoft Edge TTS for Home Assistant

This component is based on the TTS service of Microsoft Edge browser, no need to apply for `app_key`.


## Install

[![Install repository](https://my.home-assistant.io/badges/hacs_repository.svg)](https://my.home-assistant.io/redirect/hacs_repository/?owner=hasscc&repository=hass-edge-tts&category=integration)

> Download and copy `custom_components/edge_tts` folder to `custom_components` folder in your HomeAssistant config folder

```shell
# Auto install via terminal shell
wget -O - https://hacs.vip/get | DOMAIN=edge_tts REPO_PATH=hasscc/hass-edge-tts ARCHIVE_TAG=main bash -
```


## Config

[UI: config - integrations - add integration - Microsoft Edge TTS ]

[![Add Integration](https://my.home-assistant.io/badges/config_flow_start.svg)](https://my.home-assistant.io/redirect/config_flow_start?domain=edge_tts)

add integration \
<img width="500" height="300" alt="add integration" src="https://github.com/user-attachments/assets/3a4f3a30-bcd1-447e-8044-36c2bc3f78b0" /> 
 \
config option \
<img width="500" height="300" alt="config option" src="https://github.com/user-attachments/assets/0cadaf9e-d316-49b9-b28d-f1a8f7e7551c" /> 
 \
entity \
<img width="500" height="300" alt="entity" src="https://github.com/user-attachments/assets/42e8a6d7-c5e7-4f8f-9093-d93ca678ce87" /> 
 \
call service \
<img width="500" height="300" alt="call service" src="https://github.com/user-attachments/assets/fa353f2d-623b-460b-8fa4-0cbbc233f073" /> 


#### Supported languages

- [speaking languages](https://docs.microsoft.com/zh-CN/azure/cognitive-services/speech-service/speech-synthesis-markup?tabs=csharp#adjust-speaking-languages)
- [list of voices](https://github.com/hasscc/hass-edge-tts/blob/29587ecf05ecd9d40269e13d7bd37f7f7f70c874/custom_components/edge_tts/tts.py#L14-L314)


## Using

- [![Call service: tts.speak](https://my.home-assistant.io/badges/developer_call_service.svg)](https://my.home-assistant.io/redirect/developer_call_service/?service=tts.speak)
- [REST API: /api/tts_get_url](https://www.home-assistant.io/integrations/tts#post-apitts_get_url)


### Options

- [`voice`](https://docs.microsoft.com/zh-CN/azure/cognitive-services/speech-service/speech-synthesis-markup?tabs=csharp#use-multiple-voices)
- [`pitch` / `rate` / `volume`](https://docs.microsoft.com/zh-CN/azure/cognitive-services/speech-service/speech-synthesis-markup?tabs=csharp#adjust-prosody)

> `style` / `styledegree` / `role` / `contour` are no longer supported ([#8](https://github.com/hasscc/hass-edge-tts/issues/8)).

### Basic example

```yaml
action: tts.speak
target:
  entity_id: tts.edge_tts
data:
  media_player_entity_id: media_player.your_player_entity_id
  message: Hello
  language: zh-CN-XiaoyiNeural # Language or voice (Optional)
```

### Full example

```yaml
action: tts.speak
target:
  entity_id: tts.edge_tts
data:
  media_player_entity_id: media_player.your_player_entity_id
  message: 吃葡萄不吐葡萄皮，不吃葡萄倒吐葡萄皮
  language: zh-CN
  cache: true
  options:
    voice: zh-CN-XiaoyiNeural
    rate: +0%
    volume: +10%
    preferred_format: mp3  # value is a file extension like wav, mp3, ogg, etc
```

### Curl example

```shell
curl -X POST -H "Authorization: Bearer <ACCESS TOKEN>" \
     -H "Content-Type: application/json" \
     -d '{"engine_id": "tts.edge_tts", "message": "欢迎回家", "language": "zh-CN-XiaoyiNeural", "cache": true, "options": {"volume": "+10%"}}' \
     http://home-assistant.local:8123/api/tts_get_url
```

## Thanks

- https://github.com/rany2/edge-tts
- https://github.com/ag2s20150909/TTS
