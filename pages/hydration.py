from __future__ import annotations

import streamlit as st

from components.cards import render_hero_banner, render_stat_card
from components.hydrate_visual import render_progress_visual
from components.mascot_v2 import render_mascot
from services.hydration import calculate_progress, get_milestone_message, get_tip, sync_today_total, update_daily_intake


def render_hydration_page() -> None:
    render_hero_banner(
        "Hydration",
        "Log water quickly, track your momentum, and keep the sparkle of the day alive.",
        badge="Water logging",
    )
    sync_today_total()
    intake_ml = int(st.session_state.get("daily_intake_ml", 0))
    goal_ml = int(st.session_state.get("goal_ml", 2500))
    percent, remaining, _ = calculate_progress(intake_ml, goal_ml)
    message, emoji = get_milestone_message(percent)
    previous_milestone = int(st.session_state.get("last_milestone", 0))
    hit_milestone = any(level <= percent and level > previous_milestone for level in (25, 50, 75, 100))
    st.session_state["last_message"] = message
    st.markdown(
        f"<div class='glass-card'><h3>{emoji} {message}</h3><p>{get_tip(st.session_state.get('age_group', '19–50'))}</p></div>",
        unsafe_allow_html=True,
    )
    left, right = st.columns([1, 1])
    with left:
        st.markdown("### Quick choices")
        quick = st.columns([1, 1, 1])
        if quick[0].button("+250 ml", use_container_width=True):
            update_daily_intake(250, "quick")
            st.rerun() if hasattr(st, "rerun") else st.experimental_rerun()
        if quick[1].button("+500 ml", use_container_width=True):
            update_daily_intake(500, "quick")
            st.rerun() if hasattr(st, "rerun") else st.experimental_rerun()
        if quick[2].button("Reset", use_container_width=True):
            from services.hydration import reset_daily_intake

            reset_daily_intake()
            st.rerun() if hasattr(st, "rerun") else st.experimental_rerun()
        custom = st.number_input("Add a custom amount", min_value=50, max_value=2000, step=50, key="custom_amount_ml")
        if st.button("Log custom amount", use_container_width=True):
            update_daily_intake(int(custom), "custom")
            st.rerun() if hasattr(st, "rerun") else st.experimental_rerun()
    with right:
        render_progress_visual(percent, intake_ml, goal_ml, celebrate=hit_milestone)
        st.progress(percent / 100)
        # Mascot on Hydration page too
        render_mascot(
            snd_on=st.session_state.get('sound_on', True),
            last_logged=st.session_state.get('last_logged_amount', 0),
            celebrate=hit_milestone,
            show_animations=st.session_state.get('show_animations', True),
        )
    st.markdown("### Snapshot")
    snap = st.columns(3)
    with snap[0]:
        render_stat_card("Intake", f"{intake_ml} ml", "primary")
    with snap[1]:
        render_stat_card("Remaining", f"{remaining} ml", "accent")
    with snap[2]:
        render_stat_card("Progress", f"{percent}%", "primary")
