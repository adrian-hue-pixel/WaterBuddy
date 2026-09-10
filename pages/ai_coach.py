from __future__ import annotations

import streamlit as st
from datetime import date

from components.cards import render_hero_banner
from core.session_manager import safe_rerun
from services.ai import get_ai_response
from services.mascot_service import get_mascot_service




def _render_chat_history() -> None:
    history = st.session_state.setdefault("ai_chat_history", [])

    if not history:
        st.html(
            """
            <div class="coach-empty">
                <div class="coach-empty-icon">✦</div>
                <div class="coach-empty-title">Start a conversation</div>
                <div class="coach-empty-text">
                    Ask WaterBuddy about hydration, motivation, or how to stay consistent today.
                </div>
            </div>
            """
        )
        return

    for message in history:
        role = message["role"]
        text = message["message"]

        if role == "assistant":
            st.html(
                f"""
                <div class="coach-message coach-message-ai">
                    <div class="coach-message-label">WATERBUDDY</div>
                    <div class="coach-message-text">{text}</div>
                </div>
                """
            )
        else:
            st.html(
                f"""
                <div class="coach-message coach-message-user">
                    <div class="coach-message-label">YOU</div>
                    <div class="coach-message-text">{text}</div>
                </div>
                """
            )


def render_ai_coach_page() -> None:
    render_hero_banner(
        "AI Coach",
        "A thoughtful wellness companion that responds to your progress and the day’s conditions.",
        badge="Smart coaching",
    )
    # Weather integration removed — provide a neutral placeholder for prompts.
    weather_summary = "Weather data disabled"

    st.html(
        """
        <style>
            .coach-intro {
                position: relative;
                overflow: hidden;
                margin: 2rem 0 2.5rem;
                padding: 24px 26px;

                border-radius: 22px;
                background:
                    linear-gradient(
                        145deg,
                        rgba(12, 43, 64, 0.78),
                        rgba(4, 16, 28, 0.84)
                    );
                border: 1px solid rgba(92, 225, 230, 0.14);

                box-shadow:
                    0 22px 65px rgba(0, 0, 0, 0.28),
                    0 0 55px rgba(44, 210, 230, 0.055),
                    inset 0 1px 0 rgba(255, 255, 255, 0.035);
            }

            .coach-intro::after {
                content: "";
                position: absolute;
                width: 180px;
                height: 180px;
                right: -70px;
                top: -95px;
                border-radius: 50%;
                background: rgba(92, 225, 230, 0.10);
                filter: blur(45px);
                pointer-events: none;
            }

            .coach-intro-label {
                color: #5ce1e6;
                font-size: 11px;
                font-weight: 800;
                letter-spacing: 0.16em;
                text-transform: uppercase;
                margin-bottom: 8px;
            }

            .coach-intro-title {
                color: #ffffff;
                font-size: 21px;
                font-weight: 800;
                margin-bottom: 7px;
            }

            .coach-intro-text {
                color: #8ea7b8;
                font-size: 14px;
                line-height: 1.55;
                max-width: 720px;
            }

            .coach-section-label {
                color: #5ce1e6;
                font-size: 11px;
                font-weight: 800;
                letter-spacing: 0.15em;
                text-transform: uppercase;
                margin-bottom: 9px;
            }

            .coach-section-title {
                color: #ffffff;
                font-size: 24px;
                font-weight: 800;
                margin-bottom: 20px;
            }

            .coach-status {
                display: flex;
                align-items: center;
                gap: 9px;
                margin: 20px 0 18px;
                padding: 11px 14px;
                border-radius: 13px;

                background: rgba(8, 26, 40, 0.62);
                border: 1px solid rgba(92, 225, 230, 0.08);

                color: #7f9bad;
                font-size: 12px;
            }

            .coach-status-dot {
                width: 7px;
                height: 7px;
                flex: 0 0 7px;
                border-radius: 50%;
                background: #5ce1e6;
                box-shadow: 0 0 12px rgba(92, 225, 230, 0.75);
            }

            .coach-message {
                position: relative;
                margin: 0 0 13px;
                padding: 17px 19px;
                border-radius: 17px;
                line-height: 1.55;
                overflow: hidden;
            }

            .coach-message-ai {
                margin-right: 8%;
                background:
                    linear-gradient(
                        145deg,
                        rgba(12, 43, 61, 0.78),
                        rgba(6, 22, 35, 0.78)
                    );
                border: 1px solid rgba(92, 225, 230, 0.11);
                box-shadow:
                    0 13px 38px rgba(0, 0, 0, 0.20),
                    0 0 28px rgba(92, 225, 230, 0.035);
            }

            .coach-message-user {
                margin-left: 14%;
                background: rgba(15, 26, 38, 0.66);
                border: 1px solid rgba(255, 255, 255, 0.055);
            }

            .coach-message-label {
                margin-bottom: 7px;
                font-size: 9px;
                font-weight: 800;
                letter-spacing: 0.15em;
                color: #5ce1e6;
            }

            .coach-message-user .coach-message-label {
                color: #718797;
            }

            .coach-message-text {
                color: #e8f7fc;
                font-size: 14px;
                white-space: pre-wrap;
            }

            .coach-message-user .coach-message-text {
                color: #b7c5ce;
            }

            .coach-empty {
                padding: 48px 24px;
                margin-bottom: 20px;
                text-align: center;
                border-radius: 22px;
                background:
                    linear-gradient(
                        145deg,
                        rgba(10, 34, 50, 0.68),
                        rgba(4, 15, 26, 0.72)
                    );
                border: 1px solid rgba(92, 225, 230, 0.09);
                box-shadow:
                    0 20px 55px rgba(0, 0, 0, 0.22),
                    0 0 45px rgba(92, 225, 230, 0.035);
            }

            .coach-empty-icon {
                margin-bottom: 12px;
                color: #5ce1e6;
                font-size: 23px;
                text-shadow: 0 0 20px rgba(92, 225, 230, 0.65);
            }

            .coach-empty-title {
                margin-bottom: 7px;
                color: #ffffff;
                font-size: 18px;
                font-weight: 750;
            }

            .coach-empty-text {
                max-width: 500px;
                margin: 0 auto;
                color: #768c9c;
                font-size: 13px;
                line-height: 1.55;
            }

            @media (max-width: 640px) {
                .coach-message-ai {
                    margin-right: 0;
                }

                .coach-message-user {
                    margin-left: 5%;
                }

                .coach-intro {
                    padding: 20px;
                }
            }
        </style>

        <div class="coach-intro">
            <div class="coach-intro-label">AI intelligence</div>
            <div class="coach-intro-title">Your hydration coach, whenever you need it.</div>
            <div class="coach-intro-text">
                WaterBuddy uses your progress and conversation history to give you thoughtful,
                personalized hydration guidance.
            </div>
        </div>

        <div class="coach-section-label">Conversation</div>
        <div class="coach-section-title">Chat with WaterBuddy</div>
        """
    )

    _render_chat_history()

    st.html(
        """
        <div class="coach-status">
            <span class="coach-status-dot"></span>
            <span>WaterBuddy AI is ready to help with hydration questions.</span>
        </div>
        """
    )


    st.html("""
    <style>
    /* WaterBuddy AI Coach composer */
    [data-testid="stChatInput"] {
        margin-top: 18px;
        margin-bottom: 10px;
    }

    [data-testid="stChatInput"] > div {
        background:
            linear-gradient(
                135deg,
                color-mix(in srgb, var(--surface) 96%, var(--primary) 4%),
                var(--surface)
            ) !important;
        border: 1px solid color-mix(in srgb, var(--primary) 18%, var(--border)) !important;
        border-radius: 22px !important;
        padding: 6px !important;
        box-shadow:
            var(--shadow-soft),
            0 0 0 1px color-mix(in srgb, var(--text) 3%, transparent) inset,
            0 0 28px color-mix(in srgb, var(--primary) 5%, transparent) !important;
        transition:
            border-color 0.2s ease,
            box-shadow 0.2s ease,
            transform 0.2s ease;
    }

    [data-testid="stChatInput"] > div:focus-within {
        border-color: var(--primary) !important;
        box-shadow:
            var(--shadow-soft),
            0 0 0 1px color-mix(in srgb, var(--primary) 10%, transparent) inset,
            0 0 30px color-mix(in srgb, var(--primary) 14%, transparent) !important;
        transform: translateY(-1px);
    }

    [data-testid="stChatInput"] textarea {
        color: var(--text) !important;
        background: transparent !important;
        font-family: "DM Sans", sans-serif !important;
        font-size: 15px !important;
        line-height: 1.5 !important;
        padding: 12px 14px !important;
    }

    [data-testid="stChatInput"] textarea::placeholder {
        color: var(--muted) !important;
        opacity: 1 !important;
    }

    [data-testid="stChatInput"] button {
        background: color-mix(in srgb, var(--primary) 10%, transparent) !important;
        border: 1px solid color-mix(in srgb, var(--primary) 18%, var(--border)) !important;
        border-radius: 15px !important;
        margin-right: 4px !important;
        transition: all 0.2s ease;
    }

    [data-testid="stChatInput"] button:hover {
        background: color-mix(in srgb, var(--primary) 18%, transparent) !important;
        border-color: color-mix(in srgb, var(--primary) 35%, var(--border)) !important;
        box-shadow: 0 0 18px color-mix(in srgb, var(--primary) 10%, transparent);
    }

    /* Small atmospheric glow beneath composer */
    [data-testid="stChatInput"]::after {
        content: "";
        display: block;
        width: 45%;
        height: 1px;
        margin: 9px auto 0;
        background: linear-gradient(
            90deg,
            transparent,
            rgba(56, 189, 248, 0.18),
            transparent
        );
    }

    @media (max-width: 640px) {
        [data-testid="stChatInput"] > div {
            border-radius: 18px !important;
        }

        [data-testid="stChatInput"] textarea {
            font-size: 14px !important;
        }
    }
    </style>
    """)

    if hasattr(st, "chat_input"):
        user_prompt = st.chat_input(
            "Ask WaterBuddy anything about hydration",
        )
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
        st.rerun() if hasattr(st, "rerun") else st.experimental_rerun()
