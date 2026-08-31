from __future__ import annotations

from datetime import date, datetime, timedelta, timezone

import streamlit as st

from database.manager import clear_today_intake, get_recent_history, get_today_total, save_intake
from services.mascot_service import get_mascot_service

DEFAULT_GOALS = {
    "6–12": 1600,
    "13–18": 2200,
    "19–50": 2500,
    "65+": 2000,
}


def get_age_goal(age_group: str) -> int:
    return DEFAULT_GOALS.get(age_group, 2500)


def calculate_progress(intake_ml: int, goal_ml: int) -> tuple[int, int, bool]:
    intake = max(int(intake_ml), 0)
    goal = max(int(goal_ml), 1)
    percent = min(100, int(round((intake / goal) * 100))) if goal else 0
    remaining = max(0, goal - intake)
    return percent, remaining, intake >= goal


def get_milestone_message(percent: int) -> tuple[str, str]:
    if percent >= 100:
        return "Goal reached — beautiful consistency.", "🏆"
    if percent >= 75:
        return "You are almost there — one more glass and the day is yours.", "💧"
    if percent >= 50:
        return "Momentum is building. Keep the rhythm steady.", "✨"
    if percent >= 25:
        return "You are off to a strong start — keep sipping.", "🌊"
    return "A fresh start awaits. Let’s make hydration feel easy.", "☀️"


def get_tip(age_group: str) -> str:
    tips = {
        "6–12": "Pick a bottle you love and keep it on your desk so hydration feels fun.",
        "13–18": "Pair one water break with a class change or a playlist cue.",
        "19–50": "Build a habit with a glass at each meal and a top-up after every meeting.",
        "65+": "Keep water within reach and sip slowly through the day.",
    }
    return tips.get(age_group, "Keep it gentle and consistent — a few sips at a time still count.")


def sync_today_total() -> tuple[int, int]:
    today = date.today().strftime("%Y-%m-%d")
    user_id = st.session_state.get("user_id")
    age_group = st.session_state.get("age_group", "19–50")
    suggested_goal = get_age_goal(age_group)
    if not st.session_state.get("goal_override", False):
        st.session_state["goal_ml"] = suggested_goal
    goal = int(st.session_state.get("goal_ml", suggested_goal))
    intake = get_today_total(today, user_id=user_id)
    st.session_state["daily_intake_ml"] = intake
    percent, _, _ = calculate_progress(intake, goal)
    if "last_milestone" not in st.session_state or st.session_state.get("last_milestone") != percent:
        message, _ = get_milestone_message(percent)
        st.session_state["last_message"] = message
        st.session_state["last_milestone"] = percent
    return intake, goal


def update_daily_intake(amount_ml: int, source: str) -> tuple[int, int]:
    today = date.today().strftime("%Y-%m-%d")
    user_id = st.session_state.get("user_id")
    save_intake(today, int(amount_ml), source, user_id=user_id)
    intake = get_today_total(today, user_id=user_id)
    goal = int(st.session_state.get("goal_ml", get_age_goal(st.session_state.get("age_group", "19–50"))))
    st.session_state["daily_intake_ml"] = intake
    st.session_state["last_logged_amount"] = int(amount_ml)
    st.session_state["last_water_at"] = datetime.now(timezone.utc).isoformat()
    percent, _, _ = calculate_progress(intake, goal)
    message, _ = get_milestone_message(percent)
    prev_milestone = st.session_state.get("last_milestone")
    st.session_state["last_message"] = message
    st.session_state["last_milestone"] = percent

    # Notify mascot service about the new hydration percentage so visuals react
    try:
        ms = get_mascot_service()
        ms.trigger_event('water_logged', hydration_percentage=percent)
        # If the user reached or exceeded goal, trigger achievement
        if percent >= 100:
            ms.trigger_event('achievement_unlocked', hydration_percentage=percent)
    except Exception:
        # Mascot service is non-critical; never let mascot errors block hydration logging
        pass

    return intake, goal


def reset_daily_intake() -> tuple[int, int]:
    today = date.today().strftime("%Y-%m-%d")
    user_id = st.session_state.get("user_id")
    clear_today_intake(today, user_id=user_id)
    goal = int(st.session_state.get("goal_ml", get_age_goal(st.session_state.get("age_group", "19–50"))))
    st.session_state["daily_intake_ml"] = 0
    st.session_state["last_logged_amount"] = 0
    st.session_state["last_water_at"] = None
    st.session_state["last_message"] = "A fresh start awaits. Let’s make hydration feel easy."
    st.session_state["last_milestone"] = 0

    # Inform mascot service that hydration was reset
    try:
        ms = get_mascot_service()
        ms.trigger_event('water_logged', hydration_percentage=0)
    except Exception:
        pass

    return 0, goal


def get_streak(days: int = 7) -> int:
    user_id = st.session_state.get("user_id")
    history = get_recent_history(days=days + 14, user_id=user_id)
    if not history:
        return 0
    seen_dates = {item.get("intake_date") for item in history if int(item.get("total_ml", 0)) > 0}
    current = date.today()
    streak = 0
    for _ in range(days + 14):
        day_key = current.strftime("%Y-%m-%d")
        if day_key not in seen_dates:
            break
        streak += 1
        current -= timedelta(days=1)
    return streak
