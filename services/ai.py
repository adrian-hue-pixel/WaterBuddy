from __future__ import annotations

from core.config import get_setting
import streamlit as st


class ApiRateLimitError(Exception):
    def __init__(self, message: str, retry_seconds: int | None = None) -> None:
        super().__init__(message)
        self.retry_seconds = retry_seconds


@st.cache_resource
def _get_openrouter_client(api_key: str):
    from openai import OpenAI
    return OpenAI(
        api_key=api_key,
        base_url="https://openrouter.ai/api/v1",
    )


def _generate(api_key: str, prompt: str) -> str:
    client = _get_openrouter_client(api_key)

    response = client.chat.completions.create(
        model="openrouter/free",
        messages=[
            {"role": "user", "content": prompt},
        ],
    )

    text = response.choices[0].message.content
    if not text:
        return "I couldn't generate a response right now. Please try again."

    return text.strip()




def analyze_water_bottle_image(
    image_bytes: bytes,
    bottle_capacity_ml: int,
) -> dict:
    """Estimate the current water volume visible in a bottle/cup photo."""
    import base64
    import json
    import re

    api_key = get_setting("OPENROUTER_API_KEY", "")

    if not api_key:
        return {
            "error": "Add OPENROUTER_API_KEY to your environment first.",
        }

    encoded = base64.b64encode(image_bytes).decode("utf-8")

    prompt = f"""
You are WaterBuddy's visual water-volume estimator.

Analyze the supplied photo carefully.

The user says the container's capacity is approximately {int(bottle_capacity_ml)} ml.

Your job:
1. Decide whether a drink container containing water is clearly visible.
2. Estimate the percentage of the container currently filled with water.
3. Estimate the current water volume in ml using the supplied capacity.
4. Give a confidence level: High, Medium, or Low.
5. Never claim laboratory-level precision.
6. If the bottle/container or water level is not sufficiently visible, say so.

Return ONLY valid JSON in exactly this shape:
{{
  "container_detected": true,
  "water_visible": true,
  "fill_percent": 56,
  "current_water_ml": 420,
  "confidence": "Medium",
  "note": "Short explanation of what was visible."
}}

Use integers for fill_percent and current_water_ml.
"""

    client = _get_openrouter_client(api_key)

    response = client.chat.completions.create(
        model="openrouter/free",
        messages=[
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": prompt},
                    {
                        "type": "image_url",
                        "image_url": {
                            "url": f"data:image/jpeg;base64,{encoded}",
                        },
                    },
                ],
            }
        ],
    )

    text = response.choices[0].message.content or ""

    # Remove accidental markdown fences if the model adds them.
    text = re.sub(r"^```(?:json)?\s*", "", text.strip(), flags=re.I)
    text = re.sub(r"\s*```$", "", text.strip())

    try:
        result = json.loads(text)
    except json.JSONDecodeError:
        match = re.search(r"\{.*\}", text, flags=re.S)
        if not match:
            return {
                "error": "The AI returned an unreadable scan result. Please try another photo."
            }
        try:
            result = json.loads(match.group(0))
        except json.JSONDecodeError:
            return {
                "error": "The AI returned an unreadable scan result. Please try another photo."
            }

    try:
        result["fill_percent"] = max(
            0, min(100, int(result.get("fill_percent", 0)))
        )
        result["current_water_ml"] = max(
            0,
            min(
                int(bottle_capacity_ml),
                int(result.get("current_water_ml", 0)),
            ),
        )
    except (TypeError, ValueError):
        return {"error": "The AI could not estimate the water amount reliably."}

    return result


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
    api_key = get_setting("OPENROUTER_API_KEY", "")

    if not api_key:
        return (
            "AI coaching is ready when you add a OPENROUTER_API_KEY "
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
    api_key = get_setting("OPENROUTER_API_KEY", "")

    if not api_key:
        return (
            "AI coaching is ready when you add a OPENROUTER_API_KEY "
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
