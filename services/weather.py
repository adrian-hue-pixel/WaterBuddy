from __future__ import annotations

import os
from typing import Any

import requests

_fetch_weather_cached: dict[tuple[str, str], dict[str, Any]] = {}


def fetch_weather(city: str, units: str = "metric") -> dict[str, Any]:
    """Fetch current weather data from OpenWeatherMap with a small in-memory cache.

    Returns a dictionary with either weather data or a friendly error payload.
    """
    city_name = (city or "").strip()
    if not city_name:
        return {"error": "City name is required."}

    normalized_units = "metric" if units not in {"metric", "imperial", "standard"} else units
    cache_key = (city_name.lower(), normalized_units)
    if cache_key in _fetch_weather_cached:
        return dict(_fetch_weather_cached[cache_key])

    api_key = os.getenv("OPENWEATHER_API_KEY")
    if not api_key:
        result = {"error": "OPENWEATHER_API_KEY is missing. Set it in your environment or .env file."}
        _fetch_weather_cached[cache_key] = result
        return result

    url = "https://api.openweathermap.org/data/2.5/weather"
    params = {"q": city_name, "units": normalized_units, "appid": api_key}

    try:
        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()
        payload = response.json()
    except requests.Timeout:
        result = {"error": "Weather request timed out."}
    except requests.RequestException as exc:
        result = {"error": f"Weather request failed: {exc}"}
    except ValueError:
        result = {"error": "Weather service returned invalid JSON."}
    else:
        if not isinstance(payload, dict):
            result = {"error": "Weather service returned an invalid payload."}
        else:
            main = payload.get("main")
            weather = payload.get("weather")
            if not isinstance(main, dict) or not isinstance(weather, list) or not weather:
                result = {"error": "Weather payload was missing expected fields."}
            else:
                description = weather[0].get("description", "weather") if isinstance(weather[0], dict) else "weather"
                result = {
                    "city": payload.get("name", city_name),
                    "temperature": float(main.get("temp", 0.0)),
                    "humidity": float(main.get("humidity", 0.0)),
                    "description": str(description),
                    "icon": str(weather[0].get("icon", "")) if isinstance(weather[0], dict) else "",
                    "units": normalized_units,
                }
        _fetch_weather_cached[cache_key] = result
        return result

    _fetch_weather_cached[cache_key] = result
    return result
