from __future__ import annotations

from services.ai import get_ai_response
from services.speech import SpeechService
from services.tts import TextToSpeechService


class VoiceService:
    def __init__(self) -> None:
        self.speech_service = SpeechService()
        self.tts_service = TextToSpeechService()

    def transcribe_audio(self, audio_bytes: bytes) -> str:
        return self.speech_service.transcribe(audio_bytes)

    def create_audio_response(
        self,
        user_message: str,
        profile_name: str,
        intake_ml: int,
        goal_ml: int,
        weather_summary: str,
    ) -> tuple[str, bytes, str]:
        ai_response = get_ai_response(
            user_message,
            profile_name,
            intake_ml,
            goal_ml,
            weather_summary,
        )
        audio_bytes_out, mime_type = self.tts_service.synthesize(ai_response)
        return ai_response, audio_bytes_out, mime_type

    def process_voice_input(
        self,
        audio_bytes: bytes,
        profile_name: str,
        intake_ml: int,
        goal_ml: int,
        weather_summary: str,
    ) -> tuple[str, str, bytes, str]:
        transcript = self.transcribe_audio(audio_bytes)
        ai_response, audio_bytes_out, mime_type = self.create_audio_response(
            transcript,
            profile_name,
            intake_ml,
            goal_ml,
            weather_summary,
        )
        return transcript, ai_response, audio_bytes_out, mime_type
