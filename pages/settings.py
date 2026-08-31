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

        preview_dark = bool(st.session_state.get("dark_mode", False))
        dark_mode_preview = st.checkbox(
            "Dark mode",
            value=preview_dark,
            key="settings_dark_mode_preview",
            help="This preview is saved when you click Save changes.",
        )

        sync_theme_state()
        apply_theme(dark_override=dark_mode_preview)

        st.session_state["theme"] = selected_theme_key
        st.session_state["mascot_variant"] = {"water": "aqua", "sun": "sunrise", "green": "forest", "neon": "neon", "yin_yang": "yin_yang"}.get(selected_theme_key, "aqua")

        preview_title = "Preview"
        preview_map = {
            "water": {"bg": "linear-gradient(135deg, #dff8ff, #bfe7ff)", "accent": "#12b7d6", "label": "Water mode"},
            "sun": {"bg": "linear-gradient(135deg, #fff3df, #ffd5b8)", "accent": "#ff8d5c", "label": "Sun mode"},
            "green": {"bg": "linear-gradient(135deg, #ebfff1, #d7f5dd)", "accent": "#64d79d", "label": "Green mode"},
            "neon": {"bg": "linear-gradient(135deg, #f3e8ff, #ddd6fe)", "accent": "#8b5cf6", "label": "Neon mode"},
            "yin_yang": {"bg": "linear-gradient(135deg, #ffffff, #f4f4f5)", "accent": "#000000", "label": "Yin & Yang mode"},
        }
        palette = preview_map.get(selected_theme_key, preview_map["water"])
        st.markdown(
            f"""
            <div style="background:{palette['bg']}; border:1px solid rgba(255,255,255,0.2); border-radius:18px; padding:1rem 1.1rem; margin-top:0.8rem; box-shadow: 0 10px 28px rgba(0,0,0,0.08);">
                <div style="display:flex; align-items:center; justify-content:space-between; gap:0.75rem; margin-bottom:0.55rem;">
                    <div style="font-weight:800; font-size:1rem; color:#0f172a;">{preview_title}</div>
                    <span style="background:{palette['accent']}; color:white; border-radius:999px; font-size:0.72rem; font-weight:700; padding:0.32rem 0.62rem;">{palette['label']}</span>
                </div>
                <div style="display:flex; align-items:center; gap:0.8rem;">
                    <div style="width:44px; height:44px; border-radius:14px; background: {palette['accent']}; box-shadow: inset 0 1px 0 rgba(255,255,255,0.4);"></div>
                    <div>
                        <div style="font-weight:700; color:#0f172a;">{selected_label}</div>
                        <div style="font-size:0.82rem; color:#334155;">{('Dark preview is enabled' if dark_mode_preview else 'Light preview is enabled')}</div>
                    </div>
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

        st.checkbox("Show animated progress", value=True, key="show_animations")
        st.checkbox("Enable mascot sounds", value=st.session_state.get('sound_on', True), key="sound_on")
        # Weather inputs removed — OpenWeather integration no longer used.
        st.info("API keys are read from .env and never stored in code. Make sure GEMINI_API_KEY is present for AI features.")

        submitted = st.form_submit_button("Save changes")
        if submitted:
            st.session_state["theme"] = selected_theme_key
            st.session_state["settings_dark_mode"] = bool(dark_mode_preview)
            sync_theme_state()
            apply_theme(dark_override=bool(dark_mode_preview))
            try:
                from database.manager import set_persisted_theme

                set_persisted_theme(theme=selected_theme_key, dark=bool(dark_mode_preview))
            except Exception:
                pass
            st.success("Changes saved.")
            st.rerun()
