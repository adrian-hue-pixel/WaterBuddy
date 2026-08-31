from __future__ import annotations

import types

from services.ai import _build_chat_prompt, get_ai_response


def test_ai_response_without_api_key_returns_friendly_fallback(monkeypatch):
    monkeypatch.delenv("GEMINI_API_KEY", raising=False)
    response = get_ai_response("How much water should I drink?", "Ava", 1500, 2500, "Sunny")
    assert "GEMINI_API_KEY" in response
    assert "keep sipping" in response.lower()


def test_ai_response_with_mocked_model(monkeypatch):
    class FakeModel:
        def generate_content(self, prompt):
            return types.SimpleNamespace(text="Stay consistent and keep sipping.")

    monkeypatch.setenv("GEMINI_API_KEY", "test-gemini-key")
    monkeypatch.setattr("services.ai._get_genai_model", lambda api_key: FakeModel())
    response = get_ai_response("How am I doing?", "Ava", 1800, 2500, "Warm and sunny")
    assert response == "Stay consistent and keep sipping."


def test_ai_prompt_includes_context_and_history():
    prompt = _build_chat_prompt(
        "I feel tired.",
        "Ava",
        1200,
        2500,
        "Windy but mild",
        [{"role": "user", "message": "Hi"}, {"role": "assistant", "message": "Hello"}],
    )
    assert "Ava" in prompt
    assert "1200" in prompt
    assert "Windy but mild" in prompt
    assert "User: I feel tired." in prompt
    assert "WaterBuddy: Hello" in prompt


def test_ai_response_rejects_empty_message(monkeypatch):
    monkeypatch.setenv("GEMINI_API_KEY", "test-gemini-key")
    response = get_ai_response("   ", "Ava", 0, 2500, "Sunny")
    assert "did not hear a question" in response.lower()


def test_ai_context_only_contains_correct_user_data(monkeypatch):
    captured = {}

    class FakeModel:
        def generate_content(self, prompt):
            captured["prompt"] = prompt
            return types.SimpleNamespace(text="Noted.")

    monkeypatch.setenv("GEMINI_API_KEY", "test-gemini-key")
    monkeypatch.setattr("services.ai._get_genai_model", lambda api_key: FakeModel())
    get_ai_response("Need encouragement.", "Alice", 2200, 2500, "Clear")
    assert "Alice" in captured["prompt"]
    assert "Bob" not in captured["prompt"]
