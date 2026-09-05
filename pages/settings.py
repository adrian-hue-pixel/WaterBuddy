from __future__ import annotations

import streamlit as st

from components.cards import render_hero_banner
from core.theme import apply_theme, sync_theme_state


def render_settings_page() -> None:
    render_hero_banner(
        "Settings",
        "Customize your experience and keep the app ready for cloud deployment.",
        badge="Preferences",
    )

    theme_choices = {
        "water": "💧 Water",
        "sun": "☀️ Sun",
        "green": "🌿 Green",
        "neon": "🟣 Neon",
        "yin_yang": "☯️ Yin & Yang",
    }
    current_theme = str(st.session_state.get("theme", "water")).lower()
    current_theme_key = current_theme if current_theme in theme_choices else "water"
    settings_theme_key = st.session_state.get("settings_theme", current_theme_key)
    settings_theme_key = settings_theme_key if settings_theme_key in theme_choices else current_theme_key
    selected_label = theme_choices[settings_theme_key]
    options = list(theme_choices.values())
    option_index = options.index(selected_label)

    with st.form("settings_form"):
        selected_label = st.selectbox(
            "Theme style",
            options,
            index=option_index,
            help="Choose the base look for the app — each theme also updates the mascot style.",
            key="settings_theme_select",
        )
        selected_theme_key = next(key for key, label in theme_choices.items() if label == selected_label)
        st.session_state["settings_theme"] = selected_theme_key

        st.checkbox("Show animated progress", value=bool(st.session_state.get("show_animations", True)), key="show_animations")
        st.checkbox("Enable mascot sounds", value=st.session_state.get('sound_on', True), key="sound_on")
        # Weather inputs removed — OpenWeather integration no longer used.
        st.info("API keys are read from .env and never stored in code. Make sure GEMINI_API_KEY is present for AI features.")

        submitted = st.form_submit_button("Save changes")
        if submitted:
            st.session_state["theme"] = selected_theme_key
            sync_theme_state()
            try:
                from database.manager import set_persisted_theme
                set_persisted_theme(theme=selected_theme_key)
            except Exception:
                pass
            st.success("Changes saved.")
            st.rerun()
