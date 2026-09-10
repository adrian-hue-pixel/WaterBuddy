from __future__ import annotations

import streamlit as st

from core.session_manager import safe_rerun

from components.cards import render_hero_banner, render_stat_card
from components.hydrate_visual import render_progress_visual
from components.mascot_v2 import render_mascot
from services.mascot_service import get_mascot_service
from services.ai import get_hydration_autopilot
from services.hydration_twin import get_hydration_twin
from services.goal_optimizer import get_goal_optimizer_summary
from services.context_engine import get_context_snapshot
from services.hydration import (
    calculate_progress,
    get_hydration_prediction,
    get_hydration_records,
    get_milestone_message,
    get_tip,
    sync_today_total,
    update_daily_intake,
)
from services.personalization import get_age_aesthetic


def render_dashboard_page() -> None:
    profile_name = st.session_state.get("profile_name", "").strip() or "Friend"

    st.markdown(
        f"""
        <div style="
            margin: 4px 0 18px 0;
            font-size: 1.55rem;
            font-weight: 800;
            letter-spacing: -0.02em;
        ">
            Welcome, {profile_name} 👋
        </div>
        """,
        unsafe_allow_html=True,
    )

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
        st.markdown(
        '<div class="wb-section-kicker">DAILY HYDRATION</div>'
        '<h2 class="wb-section-title">Quick log</h2>',
        unsafe_allow_html=True,
    )
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
    # Achievement unlocks are collected before rendering the mascot,
    # so every newly unlocked achievement can trigger its celebration.
    new_achievements = st.session_state.pop("_new_achievements", [])
    achievement_celebrate = bool(new_achievements)

    if achievement_celebrate:
        ms.trigger_event(
            "achievement_unlocked",
            hydration_percentage=int(percent),
        )

    force_celebrate = bool(
        st.session_state.pop("_force_mascot_celebrate", False)
    )

    with right:
        render_progress_visual(
            percent,
            intake_ml,
            goal_ml,
            celebrate=hit_milestone or achievement_celebrate,
        )
        st.progress(percent / 100)
        st.caption(f"{percent}% of your {goal_ml} ml goal")

        # Goal reached banner
        if percent >= 100:
            st.markdown(
                """
                <div style="
                    margin: 18px 0 12px 0;
                    padding: 18px 22px;
                    border-radius: 18px;
                    border: 1px solid rgba(34, 197, 94, 0.28);
                    background: rgba(34, 197, 94, 0.08);
                    text-align: center;
                ">
                    <div style="font-size: 1.35rem; font-weight: 800; letter-spacing: 0.02em;">
                        🎉 TARGET REACHED!
                    </div>
                    <div style="margin-top: 6px; font-size: 0.98rem; opacity: 0.82;">
                        You’ve reached today’s hydration goal. Keep sipping normally throughout the rest of your day.
                    </div>
                </div>
                """,
                unsafe_allow_html=True,
            )

        render_mascot(
            snd_on=st.session_state.get("sound_on", True),
            last_logged=st.session_state.get("last_logged_amount", 0),
            celebrate=(
                hit_milestone
                or achievement_celebrate
                or force_celebrate
            ),
            show_animations=st.session_state.get("show_animations", True),
        )


    # Achievement unlock celebration
    if achievement_celebrate:
        names = {
            "first_sip": "First Sip",
            "500ml": "Getting Started",
            "1000ml": "Hydration Rookie",
            "halfway": "Halfway There",
            "75percent": "Hydration Hero",
            "goal": "Goal Crusher",
            "125percent": "Overachiever",
            "2day": "Two-Day Flow",
            "3day": "Three-Day Sprout",
            "7day": "One Week Strong",
            "14day": "Two Week Flow",
            "30day": "30-Day Wave",
            "50day": "50-Day Splash",
            "75day": "Hydration Veteran",
            "100day": "100-Day Legend",
            "150day": "Hydration Dragon",
            "182day": "Half-Year Hero",
            "250day": "Water Warrior",
            "365day": "365-Day Water Legend",
            "early_bird": "Early Bird",
            "night_owl": "Night Owl",
            "comeback": "Comeback Kid",
            "perfect_week": "Perfect Week",
            "perfect_month": "Perfect Month",
        }

        unlocked_names = [names.get(a, a) for a in new_achievements]

        st.success(
            "🏆 Achievement unlocked!  "
            + ", ".join(unlocked_names)
        )

        st.markdown(
            """
            <div class="achievement-confetti">
                <span>💧</span><span>✨</span><span>🎉</span>
                <span>💧</span><span>🏆</span><span>✨</span>
                <span>💧</span><span>🎉</span><span>💧</span>
            </div>
            <style>
            .achievement-confetti {
                position: fixed;
                inset: 0;
                pointer-events: none;
                z-index: 999999;
                overflow: hidden;
            }
            .achievement-confetti span {
                position: absolute;
                top: -40px;
                font-size: 24px;
                animation: wb-confetti-fall 2.5s linear forwards;
            }
            .achievement-confetti span:nth-child(1) { left: 8%; animation-delay: .0s; }
            .achievement-confetti span:nth-child(2) { left: 18%; animation-delay: .2s; }
            .achievement-confetti span:nth-child(3) { left: 30%; animation-delay: .1s; }
            .achievement-confetti span:nth-child(4) { left: 42%; animation-delay: .35s; }
            .achievement-confetti span:nth-child(5) { left: 54%; animation-delay: .05s; }
            .achievement-confetti span:nth-child(6) { left: 66%; animation-delay: .25s; }
            .achievement-confetti span:nth-child(7) { left: 75%; animation-delay: .15s; }
            .achievement-confetti span:nth-child(8) { left: 86%; animation-delay: .4s; }
            .achievement-confetti span:nth-child(9) { left: 94%; animation-delay: .3s; }

            @keyframes wb-confetti-fall {
                0% {
                    transform: translateY(0) rotate(0deg);
                    opacity: 1;
                }
                100% {
                    transform: translateY(105vh) rotate(720deg);
                    opacity: 0;
                }
            }
            </style>
            """,
            unsafe_allow_html=True,
        )


    # Hydration prediction
    prediction = get_hydration_prediction()
    records = get_hydration_records()
    profile_name = st.session_state.get("profile_name", "friend")

    st.markdown(
        """
        <div class="wb-prediction-header">
            <div>
                <div class="wb-section-kicker">INTELLIGENCE</div>
                <h2 class="wb-section-title">Hydration prediction</h2>
                <p class="wb-section-subtitle">
                    A live look at where your hydration rhythm is heading.
                </p>
            </div>
            <div class="wb-live-pill">● LIVE</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    forecast_html = f"""
    <div class="wb-forecast-panel">
        <div class="wb-forecast-topline">
            <div>
                <div class="wb-forecast-label">LIVE FORECAST</div>
                <div class="wb-forecast-title">Your hydration trajectory</div>
            </div>
            <div class="wb-forecast-status">
                {prediction["status_icon"]} {prediction["status"]}
            </div>
        </div>

        <div class="wb-forecast-grid">
            <div class="wb-forecast-item">
                <span>Current pace</span>
                <strong>{prediction["pace_ml_per_hour"]:,} <small>ml/hr</small></strong>
            </div>

            <div class="wb-forecast-item">
                <span>Projected intake</span>
                <strong>{prediction["projected_intake_ml"]:,} <small>ml</small></strong>
            </div>

            <div class="wb-forecast-item">
                <span>Today's target</span>
                <strong>{prediction["goal_ml"]:,} <small>ml</small></strong>
            </div>
        </div>
    </div>
    """

    st.html(forecast_html)

    if prediction["hours_to_goal"] is not None:
        hours = prediction["hours_to_goal"]
        st.caption(f"Estimated time to goal at your current pace: {hours:.1f} hours")


    st.markdown(
        '<div class="wb-section-kicker">TODAY</div>'
        '<h2 class="wb-section-title">Your day so far</h2>',
        unsafe_allow_html=True,
    )
    stat_cols = st.columns(3)
    with stat_cols[0]:
        render_stat_card("Intake", f"{intake_ml} ml", "primary")
    with stat_cols[1]:
        render_stat_card("Remaining", f"{remaining} ml", "accent")
    with stat_cols[2]:
        render_stat_card("Goal", f"{percent}%", "primary")

    st.markdown(
        '<div class="wb-section-kicker">A LITTLE NUDGE</div>'
        '<h3 class="wb-tip-title">Gentle tip</h3>',
        unsafe_allow_html=True,
    )
    st.info(get_tip(st.session_state.get("age_group", "19–50")))
