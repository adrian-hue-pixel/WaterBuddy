from __future__ import annotations

from types import SimpleNamespace

import requests

from services import weather as weather_service


def test_fetch_weather_missing_key_returns_error(monkeypatch):
    monkeypatch.delenv("OPENWEATHER_API_KEY", raising=False)
    weather_service._fetch_weather_cached.clear()
    result = weather_service.fetch_weather("London")
    assert "error" in result
    assert "OPENWEATHER_API_KEY" in result["error"]


def test_fetch_weather_success(monkeypatch):
    monkeypatch.setenv("OPENWEATHER_API_KEY", "test-openweather-key")
    weather_service._fetch_weather_cached.clear()

    def fake_get(url, params=None, timeout=None):
        return SimpleNamespace(
            raise_for_status=lambda: None,
            json=lambda: {
                "name": "Paris",
                "main": {"temp": 22.5, "humidity": 61},
                "weather": [{"description": "clear sky", "icon": "01d"}],
            },
        )

    monkeypatch.setattr(requests, "get", fake_get)
    result = weather_service.fetch_weather("Paris", "metric")
    assert result["city"] == "Paris"
    assert result["temperature"] == 22.5
    assert result["description"] == "clear sky"


def test_fetch_weather_cache_avoids_repeated_calls(monkeypatch):
    monkeypatch.setenv("OPENWEATHER_API_KEY", "test-openweather-key")
    weather_service._fetch_weather_cached.clear()
    calls = {"count": 0}

    def fake_get(url, params=None, timeout=None):
        calls["count"] += 1
        return SimpleNamespace(
            raise_for_status=lambda: None,
            json=lambda: {"name": "Tokyo", "main": {"temp": 28, "humidity": 70}, "weather": [{"description": "sunny", "icon": "01n"}]},
        )

    monkeypatch.setattr(requests, "get", fake_get)
    weather_service.fetch_weather("Tokyo", "metric")
    weather_service.fetch_weather("Tokyo", "metric")
    assert calls["count"] == 1


def test_fetch_weather_handles_timeout_and_malformed_payload(monkeypatch):
    monkeypatch.setenv("OPENWEATHER_API_KEY", "test-openweather-key")
    weather_service._fetch_weather_cached.clear()

    def fake_timeout(*args, **kwargs):
        raise requests.Timeout("slow")

    def fake_malformed(*args, **kwargs):
        return SimpleNamespace(raise_for_status=lambda: None, json=lambda: {"broken": True})

    monkeypatch.setattr(requests, "get", fake_timeout)
    result = weather_service.fetch_weather("Seoul", "metric")
    assert "error" in result

    monkeypatch.setattr(requests, "get", fake_malformed)
    result = weather_service.fetch_weather("Berlin", "metric")
    assert "error" in result
