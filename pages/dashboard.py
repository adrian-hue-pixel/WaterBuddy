from __future__ import annotations

import streamlit as st

from core.session_manager import safe_rerun

from components.cards import render_hero_banner, render_stat_card
from components.hydrate_visual import render_progress_visual
from components.mascot_v2 import render_mascot
from services.mascot_service import get_mascot_service
from services.hydration import calculate_progress, get_milestone_message, get_tip, sync_today_total, update_daily_intake
from services.personalization import get_age_aesthetic


def render_dashboard_page() -> None:
    from core.session_manager import safe_rerun
    render_hero_banner(
        "Your hydration rhythm",
        "A calm command center for progress, coaching, and steady momentum.",
        badge="Live Dashboard",
    )
    sync_today_total()
    intake_ml = int(st.session_state.get("daily_intake_ml", 0))
    goal_ml = int(st.session_state.get("goal_ml", 2500))
    percent, remaining, _ = calculate_progress(intake_ml, goal_ml)
    message, emoji = get_milestone_message(percent)
    age_aesthetic = get_age_aesthetic(st.session_state.get("age_group", "19–50"))
    previous_milestone = int(st.session_state.get("last_milestone", 0))
    hit_milestone = any(level <= percent and level > previous_milestone for level in (25, 50, 75, 100))
    st.session_state["last_message"] = message
    st.session_state["last_milestone"] = percent

    st.markdown(
        f"<div class='glass-card'><h3>{emoji} {age_aesthetic['copy']}</h3><p>{message}</p></div>",
        unsafe_allow_html=True,
    )

    left, right = st.columns([1.2, 0.9], gap="large")
    with left:
        st.markdown("### Quick log")
        controls = st.columns([1, 1, 1])
        ms = get_mascot_service()
        if controls[0].button("+250 ml", use_container_width=True):
            update_daily_intake(250, "quick")
            if hasattr(st, "rerun"):
                st.rerun()
            else:
                st.rerun_func()
        if controls[1].button("+500 ml", use_container_width=True):
            update_daily_intake(500, "quick")
            if hasattr(st, "rerun"):
                st.rerun()
            else:
                st.rerun_func()
        if controls[2].button("Reset", use_container_width=True):
            from services.hydration import reset_daily_intake

            reset_daily_intake()
            if hasattr(st, "rerun"):
                st.rerun()
            else:
                st.rerun_func()
        amount = st.number_input("Custom amount (ml)", min_value=50, max_value=2000, step=50, key="custom_amount_ml")
        if st.button("Log custom amount", use_container_width=True):
            update_daily_intake(int(amount), "custom")
            if hasattr(st, "rerun"):
                st.rerun()
            else:
                st.rerun_func()
    with right:
        render_progress_visual(percent, intake_ml, goal_ml, celebrate=hit_milestone)
        st.progress(percent / 100)
        st.caption(f"{percent}% of your {goal_ml} ml goal")
        # Mascot: reacts to logs and celebrations
        if hit_milestone:
            ms.trigger_event('achievement_unlocked', hydration_percentage=percent)
        render_mascot(snd_on=st.session_state.get('sound_on', True), last_logged=st.session_state.get('last_logged_amount', 0), celebrate=hit_milestone)

        # Dev helper: trigger a celebration manually for testing (visible while debugging)
        if st.button("Trigger celebration (dev)", key="dev_trigger_celebrate"):
            # Trigger the mascot service event and force a one-shot celebrate flag
            ms.trigger_event('achievement_unlocked', hydration_percentage=100)
            st.session_state['_force_mascot_celebrate'] = True
            if hasattr(st, "rerun"):
                st.rerun()
            else:
                st.rerun_func()

        # Allow forcing celebration via session_state key (cleared after render)
        force_celebrate = False
        if st.session_state.get('_force_mascot_celebrate'):
            force_celebrate = bool(st.session_state.pop('_force_mascot_celebrate', False))

    st.markdown("### Your day so far")
    stat_cols = st.columns(3)
    with stat_cols[0]:
        render_stat_card("Intake", f"{intake_ml} ml", "primary")
    with stat_cols[1]:
        render_stat_card("Remaining", f"{remaining} ml", "accent")
    with stat_cols[2]:
        render_stat_card("Goal", f"{percent}%", "primary")

    st.markdown("#### Gentle tip")
    st.info(get_tip(st.session_state.get("age_group", "19–50")))
