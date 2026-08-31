from __future__ import annotations

from pathlib import Path


def test_env_is_ignored_by_git():
    gitignore = Path(".gitignore").read_text(encoding="utf-8")
    assert ".env" in gitignore


def test_test_credentials_are_fake_and_not_hardcoded():
    assert "test-gemini-key" != "GEMINI_API_KEY"
    assert "test-openweather-key" != "OPENWEATHER_API_KEY"


def test_app_uses_env_variables_instead_of_embedded_secrets():
    source_files = [
        Path("core/config.py"),
        Path("services/weather.py"),
        Path("services/ai.py"),
    ]
    text = "\n".join(path.read_text(encoding="utf-8") for path in source_files)
    assert "os.getenv" in text
    assert "get_setting" in text
    assert "actual_api_key" not in text.lower()
