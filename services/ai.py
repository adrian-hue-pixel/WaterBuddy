from __future__ import annotations

from core.config import get_setting

import streamlit as st


class ApiRateLimitError(Exception):
    def __init__(self, message: str, retry_seconds: int | None = None) -> None:
        super().__init__(message)
        self.retry_seconds = retry_seconds


@st.cache_resource
def _get_genai_model(api_key: str):
    """Return a cached configured Gemini generative model for the provided API key.

    Caching the model avoids repeated configuration and network setup on each
    Streamlit rerun. The cache is keyed by api_key so different keys produce
    separate cached resources.
    """
    import google.generativeai as genai

    genai.configure(api_key=api_key)
    return genai.GenerativeModel("models/gemini-flash-latest")


def get_ai_coaching(profile_name: str, intake_ml: int, goal_ml: int, weather_summary: str) -> str:
    api_key = get_setting("GEMINI_API_KEY", "")
    if not api_key:
        return "AI coaching is ready when you add a GEMINI_API_KEY in your .env file. Until then, a simple reminder: keep sipping a little at a time."

    try:
        model = _get_genai_model(api_key)
        prompt = (
            f"You are WaterBuddy, a warm hydration coach. The user {profile_name or 'friend'} has consumed {intake_ml} ml out of {goal_ml} ml today. "
            f"Weather summary: {weather_summary}. Give a concise encouraging coaching note with one practical tip."
        )
        response = model.generate_content(prompt)
        return response.text.strip()
    except Exception as exc:  # pragma: no cover - runtime fallback path
        # Detect rate limit and propagate as ApiRateLimitError so callers can handle fallbacks
        msg = str(exc)
        import re

        retry_seconds = None
        m = re.search(r"Please retry in (\d+(?:\.\d+)?)s", msg)
        if m:
            try:
                retry_seconds = int(float(m.group(1)))
            except Exception:
                retry_seconds = None
        else:
            m2 = re.search(r"retry_delay\s*\{\s*seconds:\s*(\d+)", msg)
            if m2:
                try:
                    retry_seconds = int(m2.group(1))
                except Exception:
                    retry_seconds = None

        if "429" in msg or "quota" in msg.lower() or retry_seconds is not None:
            raise ApiRateLimitError("AI provider rate limit reached", retry_seconds)

        return f"AI coaching is temporarily unavailable: {exc}"


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
            history_prompt = "Conversation history:\n" + "\n".join(history_lines) + "\n\n"

    return (
        f"You are WaterBuddy, a warm hydration coach. The user {profile_name or 'friend'} has consumed {intake_ml} ml out of {goal_ml} ml today. "
        f"Weather summary: {weather_summary}. "
        f"Respond to the user's latest question clearly and kindly, offering hydration support, empathy, and an encouraging next step. "
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
        return "AI coaching is ready when you add a GEMINI_API_KEY in your .env file. Until then, a simple reminder: keep sipping a little at a time."

    if not user_message or not user_message.strip():
        return "I did not hear a question. Please type or speak again so WaterBuddy can help."

    try:
        model = _get_genai_model(api_key)
        prompt = _build_chat_prompt(
            user_message,
            profile_name,
            intake_ml,
            goal_ml,
            weather_summary,
            conversation_history,
        )
        response = model.generate_content(prompt)
        return response.text.strip()
    except Exception as exc:  # pragma: no cover - runtime fallback path
        # Detect rate limit and propagate as ApiRateLimitError so callers can handle fallbacks
        msg = str(exc)
        import re

        retry_seconds = None
        m = re.search(r"Please retry in (\d+(?:\.\d+)?)s", msg)
        if m:
            try:
                retry_seconds = int(float(m.group(1)))
            except Exception:
                retry_seconds = None
        else:
            m2 = re.search(r"retry_delay\s*\{\s*seconds:\s*(\d+)", msg)
            if m2:
                try:
                    retry_seconds = int(m2.group(1))
                except Exception:
                    retry_seconds = None

        if "429" in msg or "quota" in msg.lower() or retry_seconds is not None:
            raise ApiRateLimitError("AI provider rate limit reached", retry_seconds)

        return f"AI coaching is temporarily unavailable: {exc}"
