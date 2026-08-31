from __future__ import annotations

import io
import logging
import time

from gtts import gTTS

logger = logging.getLogger(__name__)


class TextToSpeechService:
    def __init__(self, language: str = "en") -> None:
        self.language = language

    def synthesize(self, text: str) -> tuple[bytes, str]:
        if not text or not text.strip():
            raise ValueError("Empty text cannot be converted to speech.")

        logger.info("Text-to-speech request received; text length=%d", len(text))
        start = time.perf_counter()
        try:
            mp3_output = io.BytesIO()
            tts = gTTS(text=text, lang=self.language)
            tts.write_to_fp(mp3_output)
            audio_bytes = mp3_output.getvalue()
            if not audio_bytes:
                raise RuntimeError("Text-to-speech generated no audio data.")
        except Exception as exc:
            duration = time.perf_counter() - start
            logger.error("Text-to-speech failed after %.2fs: %s", duration, exc)
            raise RuntimeError(
                "WaterBuddy could not generate spoken audio. Please try again later."
            ) from exc

        duration = time.perf_counter() - start
        logger.info(
            "Text-to-speech succeeded in %.2fs; output size=%d bytes",
            duration,
            len(audio_bytes),
        )
        return audio_bytes, "audio/mpeg"
