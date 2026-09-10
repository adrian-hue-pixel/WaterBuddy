from __future__ import annotations

import streamlit as st

from services.context_engine import get_context_snapshot
from services.goal_optimizer import get_goal_optimizer_summary
from services.hydration_twin import get_hydration_twin


def render_ai_hydration_page() -> None:
    st.markdown("# 🤖 AI Hydration")
    st.caption(
        "WaterBuddy's intelligence layer — predictions, planning, context, and autopilot."
    )

    # ---------------------------------------------------------
    # Smart Hydration Autopilot
    # ---------------------------------------------------------
    st.markdown("## ⚡ Smart Hydration Autopilot")
    st.caption("Let WaterBuddy turn your current hydration data into an actionable plan.")

    if "hydration_autopilot" not in st.session_state:
        st.session_state["hydration_autopilot"] = None

    if st.button("Run Hydration Autopilot", use_container_width=True):
        twin = get_hydration_twin()
        context = get_context_snapshot()

        if twin["remaining_ml"] <= 0:
            autopilot = (
                "🎉 You've reached today's hydration target. "
                "Keep your normal rhythm and stay consistent."
            )
        elif twin["pace_ml_per_hour"] == 0:
            autopilot = (
                "💧 No water has been logged yet today. "
                "Start with a drink, then WaterBuddy can build a better trajectory."
            )
        elif context["trajectory"] == "behind":
            autopilot = (
                f"🧭 You're currently behind trajectory. "
                f"Aim for roughly {twin['required_pace_ml_per_hour']:,} ml/hr "
                "for the remaining part of the day."
            )
        elif context["trajectory"] == "at_risk":
            autopilot = (
                "⚠️ You're still within reach of today's target, "
                "but consistency matters from here."
            )
        else:
            autopilot = (
                "✨ You're on track. Maintain your current hydration rhythm "
                "and avoid trying to catch up all at once."
            )

        st.session_state["hydration_autopilot"] = autopilot

    if st.session_state.get("hydration_autopilot"):
        st.info(st.session_state["hydration_autopilot"])

    st.divider()

    # ---------------------------------------------------------
    # Digital Twin
    # ---------------------------------------------------------
    st.markdown("## 🧬 Hydration Digital Twin")
    st.caption("A live model of your current hydration trajectory.")

    twin = get_hydration_twin()

    twin_cols = st.columns(4)

    with twin_cols[0]:
        st.metric(
            "Hydration state",
            twin["trajectory"].replace("_", " ").title(),
        )

    with twin_cols[1]:
        st.metric(
            "Current pace",
            f'{twin["pace_ml_per_hour"]:,} ml/hr',
        )

    with twin_cols[2]:
        st.metric(
            "Projected finish",
            f'{twin["projected_intake_ml"]:,} ml',
        )

    with twin_cols[3]:
        st.metric(
            "Model confidence",
            f'{twin["confidence"] * 100:.0f}%',
        )

    st.progress(twin["progress_percent"] / 100)

    st.info(
        f'🧠 {twin["recommendation"]} '
        f'Required pace from here: '
        f'{twin["required_pace_ml_per_hour"]:,} ml/hr.'
    )

    st.divider()

    # ---------------------------------------------------------
    # Goal Optimizer
    # ---------------------------------------------------------
    st.markdown("## 🎯 AI Goal Optimizer")
    st.caption(
        "A personalized target calculated from your current hydration context."
    )

    optimizer = get_goal_optimizer_summary()

    goal_cols = st.columns(4)

    with goal_cols[0]:
        st.metric(
            "Optimized goal",
            f'{optimizer["optimized_goal_ml"]:,} ml',
            delta=f'{optimizer["adjustment_ml"]:+,} ml',
        )

    with goal_cols[1]:
        st.metric(
            "Projected intake",
            f'{optimizer["projected_intake_ml"]:,} ml',
        )

    with goal_cols[2]:
        st.metric(
            "Difficulty",
            optimizer["difficulty"],
        )

    with goal_cols[3]:
        st.metric(
            "Confidence",
            f'{optimizer["confidence"] * 100:.0f}%',
        )

    st.progress(optimizer["progress_percent"] / 100)

    st.info(
        f'🧠 {optimizer["reason"]} '
        f'{optimizer["next_action"]}'
    )

    st.divider()

    # ---------------------------------------------------------
    # Context Engine
    # ---------------------------------------------------------
    st.markdown("## 🧠 WaterBuddy Context Engine")
    st.caption(
        "The context layer interprets your hydration state and decides "
        "what matters right now."
    )

    context = get_context_snapshot()

    context_cols = st.columns(3)

    with context_cols[0]:
        st.metric(
            "Current phase",
            context["time_phase"].title(),
        )

    with context_cols[1]:
        st.metric(
            "Hydration state",
            context["hydration_state"].title(),
        )

    with context_cols[2]:
        st.metric(
            "Active signals",
            len(context["signals"]),
        )

    if context["signals"]:
        signals = ", ".join(
            signal.replace("_", " ")
            for signal in context["signals"]
        )
        st.info(
            f'🤖 {context["time_phase"].title()} context: {signals}'
        )
    else:
        st.success(
            "🤖 No active alerts. Your hydration context is currently stable."
        )
