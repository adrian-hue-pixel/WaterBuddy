from __future__ import annotations

import pytest

from services.speech import SpeechService
from services.tts import TextToSpeechService
from services.voice import VoiceService


def test_voice_pipeline_with_mocked_speech_and_tts(monkeypatch):
    monkeypatch.setattr(SpeechService, "transcribe", lambda self, audio_bytes: "Drink a glass of water")
    monkeypatch.setattr(TextToSpeechService, "synthesize", lambda self, text: (b"audio-bytes", "audio/mpeg"))
    monkeypatch.setattr("services.voice.get_ai_response", lambda *args, **kwargs: "Keep sipping.")

    service = VoiceService()
    transcript, ai_response, audio_bytes, mime = service.process_voice_input(
        b"audio-bytes",
        "Ava",
        1200,
        2500,
        "Sunny",
    )
    assert transcript == "Drink a glass of water"
    assert ai_response == "Keep sipping."
    assert audio_bytes == b"audio-bytes"
    assert mime == "audio/mpeg"


def test_voice_rejects_missing_or_invalid_audio():
    with pytest.raises(ValueError):
        SpeechService().transcribe(b"")


def test_tts_rejects_empty_text(monkeypatch):
    def fake_gtts(*args, **kwargs):
        return None

    monkeypatch.setattr("services.tts.gTTS", fake_gtts)
    with pytest.raises(ValueError):
        TextToSpeechService().synthesize("   ")


def test_tts_failure_is_raised_cleanly(monkeypatch):
    class BrokenTTS:
        def __init__(self, *args, **kwargs):
            raise RuntimeError("tts unavailable")

    monkeypatch.setattr("services.tts.gTTS", BrokenTTS)
    with pytest.raises(RuntimeError):
        TextToSpeechService().synthesize("Please stay hydrated.")
