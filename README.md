# Microsoft Edge TTS for Home Assistant

This component is based on the TTS service of Microsoft Edge browser, no need to apply for `app_key`.


## Install

> Download and copy `custom_components/edge_tts` folder to `custom_components` folder in your HomeAssistant config folder

```shell
# Auto install via terminal shell
wget -O - https://hacs.vip/get | DOMAIN=edge_tts REPO_PATH=hasscc/hass-edge-tts ARCHIVE_TAG=main bash -
```


## Config

[UI: config - integrations - add integration - Microsoft Edge TTS ]

<img width="500" height="300" alt="add integration" src="https://github.com/user-attachments/assets/24eacc80-fe2c-4b1f-8434-3cea472c503b" />

<img width="500" height="300" alt="config option" src="https://github.com/user-attachments/assets/97e02a2f-6005-460d-ab61-4f31bcca97f5" />


<img width="500" height="300" alt="entity" src="https://github.com/user-attachments/assets/ef8bfcf0-54b1-4225-902f-46cb61aca43f" />


<img width="500" height="300" alt="call service" src="https://github.com/user-attachments/assets/6fc089d1-aa3a-4bc9-86cf-82adeb2b3ed3" />


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
```

### Curl example

```shell
curl -X POST -H "Authorization: Bearer <ACCESS TOKEN>" \
     -H "Content-Type: application/json" \
     -d '{"platform": "edge_tts", "message": "欢迎回家", "language": "zh-CN-XiaoyiNeural", "cache": true, "options": {"volume": "+10%"}}' \
     http://home-assistant.local:8123/api/tts_get_url
```

## Thanks

- https://github.com/rany2/edge-tts
- https://github.com/ag2s20150909/TTS
