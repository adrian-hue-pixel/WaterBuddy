from __future__ import annotations

from datetime import datetime

from services.hydration import get_hydration_prediction


def get_hydration_twin() -> dict:
    """Build a live hydration model from the user's current state."""

    prediction = get_hydration_prediction()
    now = datetime.now()

    intake = prediction["intake_ml"]
    goal = prediction["goal_ml"]
    remaining = prediction["remaining_ml"]
    pace = prediction["pace_ml_per_hour"]
    projected = prediction["projected_intake_ml"]

    progress = min(100, round((intake / max(goal, 1)) * 100, 1))

    if pace <= 0:
        trajectory = "waiting"
        confidence = 0.35
    elif projected >= goal:
        trajectory = "on_track"
        confidence = 0.90
    elif projected >= goal * 0.8:
        trajectory = "at_risk"
        confidence = 0.75
    else:
        trajectory = "behind"
        confidence = 0.85

    end_of_day = now.replace(hour=23, minute=0, second=0, microsecond=0)
    minutes_remaining = max(
        0,
        int((end_of_day - now).total_seconds() // 60),
    )

    if remaining <= 0:
        required_pace = 0
    elif minutes_remaining > 0:
        required_pace = round(remaining / (minutes_remaining / 60))
    else:
        required_pace = remaining

    if trajectory == "on_track":
        recommendation = "Maintain your current hydration rhythm."
    elif trajectory == "at_risk":
        recommendation = "A little more consistency now would help you reach your goal."
    elif trajectory == "behind":
        recommendation = "Your current pace is below today's target trajectory."
    else:
        recommendation = "Log a drink to establish your hydration trajectory."

    return {
        "timestamp": now.isoformat(),
        "intake_ml": intake,
        "goal_ml": goal,
        "remaining_ml": remaining,
        "progress_percent": progress,
        "pace_ml_per_hour": pace,
        "required_pace_ml_per_hour": required_pace,
        "projected_intake_ml": projected,
        "trajectory": trajectory,
        "confidence": confidence,
        "hours_remaining": round(minutes_remaining / 60, 2),
        "recommendation": recommendation,
    }
