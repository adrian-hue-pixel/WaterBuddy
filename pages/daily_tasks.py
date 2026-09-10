from __future__ import annotations

from datetime import date

import streamlit as st

from components.cards import render_hero_banner
from services.hydration import calculate_progress, get_hydration_records, sync_today_total


def _task_state(task_id: str, completed: bool) -> bool:
    key = f"daily_task_{date.today().isoformat()}_{task_id}"

    if completed:
        st.session_state[key] = True

    return bool(st.session_state.get(key, False))


def _build_tasks(intake_ml: int, goal_ml: int, has_scan: bool, has_autopilot: bool) -> list[dict]:
    percent, _, _ = calculate_progress(intake_ml, goal_ml)
    records = get_hydration_records()

    return [
        {
            "id": "first_drink",
            "title": "Log your first drink",
            "detail": "Start today's hydration streak with your first drink.",
            "icon": "💧",
            "completed": intake_ml > 0,
        },
        {
            "id": "scan",
            "title": "Complete a Water Scan",
            "detail": "Use AI Vision to estimate your bottle's current water level.",
            "icon": "📸",
            "completed": has_scan,
        },
        {
            "id": "quarter",
            "title": "Reach 25% of your goal",
            "detail": "Build some early momentum.",
            "icon": "🌊",
            "completed": percent >= 25,
        },
        {
            "id": "half",
            "title": "Reach 50% of your goal",
            "detail": "You're halfway through today's target.",
            "icon": "💦",
            "completed": percent >= 50,
        },
        {
            "id": "three_quarters",
            "title": "Reach 75% of your goal",
            "detail": "You're getting close.",
            "icon": "🚀",
            "completed": percent >= 75,
        },
        {
            "id": "goal",
            "title": "Complete today's goal",
            "detail": f"Reach {goal_ml:,} ml today.",
            "icon": "🏆",
            "completed": percent >= 100,
        },
        {
            "id": "streak",
            "title": "Protect your streak",
            "detail": "Keep building consistent hydration days.",
            "icon": "🔥",
            "completed": records["current_streak"] >= 1,
        },
        {
            "id": "autopilot",
            "title": "Run AI Hydration Autopilot",
            "detail": "Get a personalized next-step hydration plan.",
            "icon": "🤖",
            "completed": has_autopilot,
        },
    ]


def render_daily_tasks_page() -> None:
    render_hero_banner(
        "Daily Tasks",
        "Small hydration actions that automatically update as you progress.",
        badge="Today",
    )

    intake_ml, goal_ml = sync_today_total()

    has_scan = bool(st.session_state.get("water_scan_result"))
    has_autopilot = bool(st.session_state.get("hydration_autopilot"))

    tasks = _build_tasks(
        intake_ml,
        goal_ml,
        has_scan,
        has_autopilot,
    )

    completed_count = 0

    for task in tasks:
        completed = _task_state(task["id"], task["completed"])

        if completed:
            completed_count += 1

    total = len(tasks)
    percent_complete = int(round((completed_count / total) * 100)) if total else 0

    st.subheader("📋 Today's checklist")
    st.progress(percent_complete / 100)

    col1, col2, col3 = st.columns(3)

    col1.metric("Tasks complete", f"{completed_count}/{total}")
    col2.metric("Completion", f"{percent_complete}%")
    col3.metric("Today's intake", f"{intake_ml:,} ml")

    st.divider()

    for task in tasks:
        completed = _task_state(task["id"], task["completed"])

        if completed:
            st.success(
                f"{task['icon']} **{task['title']}** — Complete ✓\n\n"
                f"{task['detail']}"
            )
        else:
            st.info(
                f"{task['icon']} **{task['title']}**\n\n"
                f"{task['detail']}"
            )

    if completed_count == total:
        st.balloons()
        st.success("🎉 Daily checklist complete. Amazing consistency!")
    elif completed_count >= total * 0.75:
        st.success("🔥 You're nearly done with today's checklist!")
