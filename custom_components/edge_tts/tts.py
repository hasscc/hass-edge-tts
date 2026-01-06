"""Edge TTS provider with streaming support.

Примечание: подгоните импорты/путь к модулю под структуру репозитория.
"""
from __future__ import annotations

import asyncio
import base64
from typing import AsyncGenerator, Optional

from homeassistant.components.tts import Provider, TtsAudioType
from homeassistant.core import HomeAssistant

# Пакет edge-tts — убедитесь, что версия в manifest поддерживает stream API.
import edge_tts


class EdgeTTSProvider(Provider):
    """Edge TTS provider supporting streaming."""

    def __init__(self, hass: HomeAssistant, voice: str = "en-US-SaraNeural"):
        super().__init__(
            hass,
            "edge-tts",
            "Edge TTS",
            "mp3",
            supports_synthesize_streaming=True,  # ключ к включению streaming в HA
        )
        self._voice = voice

    # Существующий batch-метод (не удаляем, чтобы не ломать обратную совместимость)
    async def async_get_tts_audio(
        self, message: str, language: Optional[str] = None, options: dict | None = None
    ) -> TtsAudioType:
        """Возвращает полный MP3 буфер (batch fallback)."""
        communicator = edge_tts.Communicate(voice=self._voice)

        # Пример: если библиотека предоставляет synthesize или similar для полного ответа.
        # Здесь мы собираем все чанки в память — это fallback, не streaming.
        output = bytearray()
        async for chunk in communicator.stream(message, fmt="mp3"):
            # Если chunks приходят как base64-строки — декодируем
            if isinstance(chunk, str):
                try:
                    output.extend(base64.b64decode(chunk))
                except Exception:
                    # Если не base64 — предполагаем, что уже bytes
                    output.extend(chunk.encode() if isinstance(chunk, str) else chunk)
            else:
                output.extend(chunk)
        return ("mp3", bytes(output))

    # Новый метод: async-генератор для стриминга
    async def async_get_tts_stream(
        self, message: str, language: Optional[str] = None, options: dict | None = None
    ) -> AsyncGenerator[bytes, None]:
        """
        Возвращает async-генератор, отдающий чанки bytes для Home Assistant.
        Home Assistant будет отправлять события SynthesizeStart / SynthesizeChunk / SynthesizeStop.
        ВАЖНО: имя метода может отличаться между версиями HA — при необходимости замените
        на async_get_speech_stream / async_synthesize_stream в соответствии с целевой версией.
        """
        communicator = edge_tts.Communicate(voice=self._voice)

        # Пример с API edge-tts, которое предоставляет async-генератор .stream(...)
        # Поддерживаем несколько вариантов формата chunk'ов: bytes или base64 strings.
        try:
            async for chunk in communicator.stream(message, fmt="mp3"):
                if isinstance(chunk, str):
                    # Многие реализации возвращают base64-строки
                    try:
                        yield base64.b64decode(chunk)
                    except Exception:
                        # Если это не base64, вернём как utf-8 bytes (на всякий случай)
                        yield chunk.encode("utf-8")
                else:
                    # Ожидаем bytes
                    yield chunk
        except Exception as err:
            # Логирование/обработка ошибок: если поток упал — выбрасываем дальше
            # HA обработает завершение/ошибку стрима.
            raise

    # Альтернативное имя метода (некоторые версии HA ожидают другой метод)
    # Оборачиваем вызов, чтобы покрыть варианты
    async def async_get_speech_stream(
        self, message: str, language: Optional[str] = None, options: dict | None = None
    ) -> AsyncGenerator[bytes, None]:
        """Compat wrapper — перенаправляет на async_get_tts_stream."""
        async for chunk in self.async_get_tts_stream(message, language, options):
            yield chunk
