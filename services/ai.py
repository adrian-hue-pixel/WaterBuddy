from __future__ import annotations

from core.config import get_setting
import streamlit as st


class ApiRateLimitError(Exception):
    def __init__(self, message: str, retry_seconds: int | None = None) -> None:
        super().__init__(message)
        self.retry_seconds = retry_seconds


@st.cache_resource
def _get_genai_client(api_key: str):
    from google import genai
    return genai.Client(api_key=api_key)


def _get_genai_model(api_key: str):
    """Backward-compatible model adapter used by tests."""
    client = _get_genai_client(api_key)

    class _ModelAdapter:
        def generate_content(self, prompt):
            return client.models.generate_content(
                model="gemini-2.5-flash",
                contents=prompt,
            )

    return _ModelAdapter()


def _generate(api_key: str, prompt: str) -> str:
    model = _get_genai_model(api_key)

    response = model.generate_content(prompt)

    text = getattr(response, "text", None)
    if not text:
        return "I couldn't generate a response right now. Please try again."
    return text.strip()


def _handle_error(exc: Exception) -> str:
    msg = str(exc)

    import re

    retry_seconds = None

    match = re.search(r"Please retry in (\d+(?:\.\d+)?)s", msg)
    if match:
        retry_seconds = int(float(match.group(1)))
    else:
        match = re.search(r"retry_delay\s*\{\s*seconds:\s*(\d+)", msg)
        if match:
            retry_seconds = int(match.group(1))

    if "429" in msg or "quota" in msg.lower() or retry_seconds is not None:
        raise ApiRateLimitError(
            "AI provider rate limit reached",
            retry_seconds,
        )

    return f"AI coaching is temporarily unavailable: {exc}"


def get_ai_coaching(
    profile_name: str,
    intake_ml: int,
    goal_ml: int,
    weather_summary: str,
) -> str:
    api_key = get_setting("GEMINI_API_KEY", "")

    if not api_key:
        return (
            "AI coaching is ready when you add a GEMINI_API_KEY "
            "in your .env file. Until then, keep sipping water!"
        )

    prompt = (
        f"You are WaterBuddy, a warm hydration coach. "
        f"The user {profile_name or 'friend'} has consumed "
        f"{intake_ml} ml out of {goal_ml} ml today. "
        f"Weather summary: {weather_summary}. "
        "Give a concise encouraging coaching note with one practical tip."
    )

    try:
        return _generate(api_key, prompt)
    except Exception as exc:
        return _handle_error(exc)


def _build_chat_prompt(
    user_message: str,
    profile_name: str,
    intake_ml: int,
    goal_ml: int,
    weather_summary: str,
    conversation_history: list[dict[str, str]] | None = None,
) -> str:
    history_prompt = ""

    if conversation_history:
        history_lines = []

        for message in conversation_history:
            role = message.get("role")
            text = message.get("message", "").strip()

            if not text:
                continue

            if role == "assistant":
                history_lines.append(f"WaterBuddy: {text}")
            else:
                history_lines.append(f"User: {text}")

        if history_lines:
            history_prompt = (
                "Conversation history:\n"
                + "\n".join(history_lines)
                + "\n\n"
            )

    return (
        f"You are WaterBuddy, a warm hydration coach. "
        f"The user {profile_name or 'friend'} has consumed "
        f"{intake_ml} ml out of {goal_ml} ml today. "
        f"Weather summary: {weather_summary}. "
        "Respond to the user's latest question clearly and kindly, "
        "offering hydration support, empathy, and an encouraging next step. "
        f"{history_prompt}"
        f"User: {user_message.strip()}"
    )


def get_ai_response(
    user_message: str,
    profile_name: str,
    intake_ml: int,
    goal_ml: int,
    weather_summary: str,
    conversation_history: list[dict[str, str]] | None = None,
) -> str:
    api_key = get_setting("GEMINI_API_KEY", "")

    if not api_key:
        return (
            "AI coaching is ready when you add a GEMINI_API_KEY "
            "in your .env file. Until then, keep sipping water!"
        )

    if not user_message or not user_message.strip():
        return (
            "I did not hear a question. "
            "Please type or speak again so WaterBuddy can help."
        )

    prompt = _build_chat_prompt(
        user_message,
        profile_name,
        intake_ml,
        goal_ml,
        weather_summary,
        conversation_history,
    )

    try:
        return _generate(api_key, prompt)
    except Exception as exc:
        return _handle_error(exc)
