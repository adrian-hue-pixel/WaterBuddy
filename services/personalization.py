from __future__ import annotations

from services.hydration import get_age_goal


def get_age_aesthetic(age_group: str) -> dict[str, str]:
    return {
        "6–12": {"tone": "playful", "emoji": "🧸", "copy": "You have a bright, energetic day ahead — let’s make hydration feel easy and fun."},
        "13–18": {"tone": "energetic", "emoji": "⚡", "copy": "Stay sharp and refreshed — a few steady sips can carry you through the day."},
        "19–50": {"tone": "balanced", "emoji": "☀️", "copy": "Your routine matters — small consistent sips keep your energy steady."},
        "65+": {"tone": "comforting", "emoji": "🌿", "copy": "Gentle consistency matters — keep your hydration steady and comfortable."},
    }.get(age_group, {"tone": "balanced", "emoji": "☀️", "copy": "Keep it calm and consistent."})


def compute_goal_ml(age_group: str, climate: str, activity: str) -> int:
    """Compute a recommended daily goal (ml) based on age group, climate, and activity.

    climate: one of 'temperate', 'hot', 'cold'
    activity: one of 'low', 'moderate', 'high'
    """
    base = get_age_goal(age_group)
    # climate modifiers
    climate_map = {
        "temperate": 1.0,
        "hot": 1.15,
        "cold": 0.95,
    }
    activity_map = {
        "low": 0.9,
        "moderate": 1.0,
        "high": 1.2,
    }
    climate_mod = climate_map.get(climate, 1.0)
    activity_mod = activity_map.get(activity, 1.0)
    goal = int(round(base * climate_mod * activity_mod))
    # clamp to sensible bounds
    goal = max(1000, min(5000, goal))
    return goal
