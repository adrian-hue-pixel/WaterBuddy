from __future__ import annotations

from datetime import datetime
from typing import Any

from services.hydration_twin import get_hydration_twin
from services.goal_optimizer import get_goal_optimizer_summary


def build_context() -> dict[str, Any]:
    """Build a live context snapshot for WaterBuddy's AI layer."""

    import streamlit as st

    twin = get_hydration_twin()
    optimizer = get_goal_optimizer_summary()

    hour = datetime.now().hour

    if hour < 10:
        time_phase = "morning"
    elif hour < 13:
        time_phase = "late morning"
    elif hour < 17:
        time_phase = "afternoon"
    elif hour < 21:
        time_phase = "evening"
    else:
        time_phase = "night"

    progress = twin["progress_percent"]
    trajectory = twin["trajectory"]

    if progress >= 75:
        hydration_state = "strong"
    elif progress >= 50:
        hydration_state = "steady"
    elif progress >= 25:
        hydration_state = "developing"
    else:
        hydration_state = "low"

    signals = []

    if twin["pace_ml_per_hour"] == 0:
        signals.append("no_intake_logged")

    if trajectory == "behind":
        signals.append("behind_projection")

    if trajectory == "at_risk":
        signals.append("at_risk_projection")

    if progress >= 75:
        signals.append("high_daily_progress")

    if optimizer["adjustment_ml"] > 0:
        signals.append("goal_increase_recommended")

    if optimizer["adjustment_ml"] < 0:
        signals.append("goal_decrease_recommended")

    return {
        "timestamp": datetime.now().isoformat(),
        "time_phase": time_phase,
        "hydration_state": hydration_state,
        "trajectory": trajectory,
        "progress_percent": progress,
        "intake_ml": twin["intake_ml"],
        "goal_ml": twin["goal_ml"],
        "remaining_ml": twin["remaining_ml"],
        "pace_ml_per_hour": twin["pace_ml_per_hour"],
        "required_pace_ml_per_hour": twin["required_pace_ml_per_hour"],
        "projected_intake_ml": twin["projected_intake_ml"],
        "goal_optimizer": optimizer,
        "age_group": st.session_state.get("age_group", "19–50"),
        "activity_level": st.session_state.get(
            "activity_level",
            "moderate",
        ),
        "signals": signals,
    }


def get_context_message() -> str:
    """Generate a concise human-readable context decision."""

    context = build_context()

    signals = context["signals"]

    if "no_intake_logged" in signals:
        return "You haven't logged water yet today. Start with a small drink."

    if "behind_projection" in signals:
        return "Your hydration pace is currently behind today's target."

    if "at_risk_projection" in signals:
        return "You're still within reach, but your hydration pace needs attention."

    if "high_daily_progress" in signals:
        return "You're making strong progress toward today's hydration goal."

    return "Your hydration rhythm is currently stable."


def get_context_snapshot() -> dict[str, Any]:
    """Public API for dashboard and future AI integrations."""

    return build_context()
