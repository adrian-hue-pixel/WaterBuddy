from __future__ import annotations

import io
import logging
import time
import warnings

warnings.filterwarnings("ignore", category=DeprecationWarning, module="speech_recognition")

try:
    import speech_recognition as sr
except Exception:  # pragma: no cover - environment-specific fallback
    sr = None

logger = logging.getLogger(__name__)


class SpeechService:
    def __init__(self, language: str = "en-US") -> None:
        self.language = language
        self.recognizer = None if sr is None else sr.Recognizer()

    def transcribe(self, audio_bytes: bytes) -> str:
        if not audio_bytes:
            raise ValueError("No audio data was provided for transcription.")
        if sr is None or self.recognizer is None:
            raise RuntimeError("Speech recognition is unavailable in this environment.")

        logger.info("Recording received for transcription; size=%d bytes", len(audio_bytes))
        start = time.perf_counter()

        try:
            with sr.AudioFile(io.BytesIO(audio_bytes)) as source:
                audio_data = self.recognizer.record(source)
            transcript = self.recognizer.recognize_google(audio_data, language=self.language)
        except sr.UnknownValueError as exc:
            duration = time.perf_counter() - start
            logger.warning(
                "Speech transcription failed after %.2fs: audio not understood.", duration,
            )
            raise RuntimeError(
                "WaterBuddy could not understand the recording. Please speak clearly and try again."
            ) from exc
        except sr.RequestError as exc:
            duration = time.perf_counter() - start
            logger.error(
                "Speech transcription request failed after %.2fs: %s",
                duration,
                exc,
            )
            raise RuntimeError(
                "Speech recognition service is unavailable. Please try again later."
            ) from exc
        except Exception as exc:
            duration = time.perf_counter() - start
            logger.error(
                "Speech transcription error after %.2fs: %s",
                duration,
                exc,
            )
            raise RuntimeError(
                "There was a problem processing your recording. Please try again."
            ) from exc

        duration = time.perf_counter() - start
        logger.info("Speech transcription succeeded in %.2fs", duration)
        return transcript.strip()
