from __future__ import annotations

from core.config import get_setting


def test_get_setting_reads_env_values(monkeypatch):
    monkeypatch.setenv("GEMINI_API_KEY", "test-gemini-key")
    monkeypatch.setenv("OPENWEATHER_API_KEY", "test-openweather-key")
    assert get_setting("GEMINI_API_KEY", "") == "test-gemini-key"
    assert get_setting("OPENWEATHER_API_KEY", "") == "test-openweather-key"


def test_missing_setting_falls_back_to_default():
    assert get_setting("MISSING_SETTING", "fallback") == "fallback"


def test_settings_file_keeps_secrets_out_of_source_control():
    with open(".gitignore", "r", encoding="utf-8") as handle:
        gitignore_text = handle.read()
    assert ".env" in gitignore_text
    with open(".env.example", "r", encoding="utf-8") as handle:
        example = handle.read()
    assert "your_" in example.lower()
