from __future__ import annotations

import streamlit as st

from components.cards import render_hero_banner
from core.session_manager import safe_rerun
from services.ai import AI_TRIAL_LIMIT, _get_trial_usage, get_ai_response
from services.mascot_service import get_mascot_service


def _render_chat_history() -> None:
    history = st.session_state.setdefault("ai_chat_history", [])
    if not history:
        st.info(
            "Start a conversation with WaterBuddy. Ask about hydration, motivation, or how to stay consistent today."
        )
        return

    if hasattr(st, "chat_message"):
        for message in history:
            with st.chat_message(message["role"]):
                st.write(message["message"])
    else:
        for message in history:
            style = "background-color: rgba(45, 212, 232, 0.12); padding: 0.9rem; border-radius: 16px;"
            if message["role"] == "assistant":
                style = "background-color: rgba(37, 99, 235, 0.12); padding: 0.9rem; border-radius: 16px;"
            st.markdown(f"<div style='{style}'><strong>{message['role'].title()}:</strong> {message['message']}</div>", unsafe_allow_html=True)


def render_ai_coach_page() -> None:
    render_hero_banner(
        "AI Coach",
        "A thoughtful wellness companion that responds to your progress and the day’s conditions.",
        badge="Smart coaching",
    )
    used = _get_trial_usage()
    st.caption(f"Free AI trial: {used}/{AI_TRIAL_LIMIT} uses")

    # Weather integration removed — provide a neutral placeholder for prompts.
    weather_summary = "Weather data disabled"

    st.markdown("### Chat with WaterBuddy")
    _render_chat_history()

    if hasattr(st, "chat_input"):
        user_prompt = st.chat_input("Ask WaterBuddy anything about hydration")
        send_request = bool(user_prompt and user_prompt.strip())
    else:
        user_prompt = st.text_input("Ask WaterBuddy anything about hydration", key="ai_chat_input")
        send_request = st.button("Send") and bool(user_prompt and user_prompt.strip())

    if send_request:
        ms = get_mascot_service()
        ms.trigger_event('ai_thinking')
        with st.spinner("WaterBuddy is thinking..."):
            response = get_ai_response(
                user_prompt,
                st.session_state.get("profile_name", "friend"),
                int(st.session_state.get("daily_intake_ml", 0)),
                int(st.session_state.get("goal_ml", 2500)),
                weather_summary,
                st.session_state.get("ai_chat_history", []),
            )
            # AI response arrived — mascot speaks
            ms.trigger_event('ai_speaking')
            ms.show_message(response, context='ai_coach')
            st.session_state.setdefault("ai_chat_history", []).append(
                {"role": "user", "message": user_prompt.strip()}
            )
            st.session_state.setdefault("ai_chat_history", []).append(
                {"role": "assistant", "message": response}
            )
        st.experimental_rerun()
