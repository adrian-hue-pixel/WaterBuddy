from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import Any

from services.hydration import get_hydration_prediction


@dataclass
class GoalPlan:
    current_goal_ml: int
    optimized_goal_ml: int
    adjustment_ml: int
    progress_percent: float
    pace_ml_per_hour: int
    projected_intake_ml: int
    required_pace_ml_per_hour: int
    difficulty: str
    confidence: float
    reason: str
    next_action: str


def _clamp(value: int, low: int, high: int) -> int:
    return max(low, min(value, high))


def optimize_goal(
    *,
    age_group: str | None = None,
    activity_level: str | None = None,
    climate_factor: float = 1.0,
) -> dict[str, Any]:
    """
    Generate a personalized hydration-goal plan.

    This is the optimization layer: it combines the user's current
    hydration trajectory with contextual modifiers instead of simply
    returning a static goal.
    """

    prediction = get_hydration_prediction()

    current_goal = int(prediction["goal_ml"])
    intake = int(prediction["intake_ml"])
    projected = int(prediction["projected_intake_ml"])
    pace = int(prediction["pace_ml_per_hour"])

    age_group = age_group or "19–50"
    activity_level = (activity_level or "moderate").lower()

    activity_modifiers = {
        "low": 0.90,
        "moderate": 1.00,
        "high": 1.10,
        "very high": 1.15,
    }

    age_modifiers = {
        "13–18": 0.95,
        "19–50": 1.00,
        "51–70": 0.98,
        "71+": 0.95,
    }

    activity_factor = activity_modifiers.get(activity_level, 1.0)
    age_factor = age_modifiers.get(age_group, 1.0)

    climate_factor = max(0.90, min(float(climate_factor), 1.20))

    raw_target = current_goal * activity_factor * age_factor * climate_factor

    # Keep optimization gradual rather than suddenly changing the goal.
    max_increase = 500
    max_decrease = 300

    optimized_goal = round(raw_target / 250) * 250
    optimized_goal = _clamp(
        optimized_goal,
        current_goal - max_decrease,
        current_goal + max_increase,
    )

    adjustment = optimized_goal - current_goal

    progress = round(
        min(100, (intake / max(current_goal, 1)) * 100),
        1,
    )

    remaining = max(optimized_goal - intake, 0)

    now = datetime.now()
    minutes_left = max(
        ((23 * 60) - (now.hour * 60 + now.minute)),
        60,
    )

    required_pace = round(remaining / (minutes_left / 60))

    if projected >= optimized_goal:
        difficulty = "Easy"
        confidence = 0.91
        reason = (
            "Your current hydration trajectory already supports "
            "the optimized target."
        )
        next_action = "Maintain your current rhythm."
    elif projected >= optimized_goal * 0.8:
        difficulty = "Moderate"
        confidence = 0.82
        reason = (
            "You're reasonably close to the optimized trajectory, "
            "but a little more consistency would help."
        )
        next_action = (
            f"Aim for roughly {required_pace:,} ml/hr from here."
        )
    else:
        difficulty = "Challenging"
        confidence = 0.76
        reason = (
            "Your current projected intake is below the optimized "
            "target, so the plan needs a stronger hydration rhythm."
        )
        next_action = (
            f"Build toward roughly {required_pace:,} ml/hr from here."
        )

    if adjustment > 0:
        reason += f" The optimizer recommends increasing your goal by {adjustment:,} ml."
    elif adjustment < 0:
        reason += f" The optimizer recommends reducing your goal by {abs(adjustment):,} ml."
    else:
        reason += " Your existing goal is already well aligned."

    return {
        "current_goal_ml": current_goal,
        "optimized_goal_ml": optimized_goal,
        "adjustment_ml": adjustment,
        "intake_ml": intake,
        "progress_percent": progress,
        "pace_ml_per_hour": pace,
        "projected_intake_ml": projected,
        "required_pace_ml_per_hour": required_pace,
        "difficulty": difficulty,
        "confidence": confidence,
        "reason": reason,
        "next_action": next_action,
        "age_group": age_group,
        "activity_level": activity_level,
        "climate_factor": climate_factor,
        "generated_at": now.isoformat(),
    }


def get_goal_optimizer_summary() -> dict[str, Any]:
    """Return an optimizer plan using the current session context."""

    import streamlit as st

    return optimize_goal(
        age_group=st.session_state.get("age_group", "19–50"),
        activity_level=st.session_state.get(
            "activity_level",
            "moderate",
        ),
        climate_factor=st.session_state.get(
            "climate_factor",
            1.0,
        ),
    )
