from __future__ import annotations

import streamlit as st

from components.cards import render_badge, render_hero_banner
from services.hydration import calculate_progress


def render_achievements_page() -> None:
    render_hero_banner(
        "Achievements",
        "Small victories add up. Celebrate the milestones you reach as your routine grows stronger.",
        badge="Milestones",
    )
    intake_ml = int(st.session_state.get("daily_intake_ml", 0))
    goal_ml = int(st.session_state.get("goal_ml", 2500))
    percent, _, _ = calculate_progress(intake_ml, goal_ml)
    milestones = [
        (25, "First sip streak", "A strong beginning is worth celebrating.", "sparkle"),
        (50, "Halfway hero", "You have built real momentum.", "drop"),
        (75, "Almost there", "You are so close to your goal.", "trophy"),
        (100, "Goal reached", "What a great day of hydration.", "trophy"),
    ]
    for target, title, detail, icon in milestones:
        unlocked = percent >= target
        render_badge(
            title if unlocked else f"{title} (locked)",
            detail if unlocked else "Keep going to unlock this milestone.",
            icon if unlocked else "lock",
        )
