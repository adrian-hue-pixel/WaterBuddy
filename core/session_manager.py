from __future__ import annotations

import streamlit as st
import logging

logger = logging.getLogger(__name__)

__all__ = ["ensure_session_state", "safe_rerun"]


def safe_rerun() -> None:
    """Trigger a rerun across older and newer Streamlit versions."""
    if hasattr(st, "rerun"):
        try:
            st.rerun()
        except Exception as exc:
            logger.exception("safe_rerun: st.rerun() failed: %s", exc)
        return

    if hasattr(st, "experimental_rerun"):
        try:
            st.experimental_rerun()
        except Exception as exc:
            logger.exception("safe_rerun: st.experimental_rerun() failed: %s", exc)


def ensure_session_state() -> None:
    defaults = {
        # 'theme' is the base theme variant: 'water', 'sun', or 'green'
        "theme": "water",
        "dark_mode": True,
        # mascot_variant will be kept in sync with the selected base theme
        "mascot_variant": "aqua",
        "authenticated": False,
        "user_id": None,
        "username": "",
        "age_group": "19–50",
        "goal_ml": 2500,
        "daily_intake_ml": 0,
        "custom_amount_ml": 250,
        "goal_override": False,
        "profile_name": "",
        "profile_notes": "",
        "last_logged_amount": 0,
        "last_water_at": None,
        "last_message": "Start your hydration ritual.",
        "last_milestone": 0,
        "weather_city": "London",
        "weather_units": "metric",
        "sound_on": True,
        "show_animations": True,
    }
    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value

    # Validate base theme names — allow all configured themes for the app
    valid_base = {"water", "sun", "green", "neon", "yin_yang"}
    if "theme" not in st.session_state or st.session_state.get("theme") not in valid_base:
        st.session_state["theme"] = "water"

    # Ensure dark_mode exists as an independent boolean
    if "dark_mode" not in st.session_state:
        st.session_state["dark_mode"] = True

    # Keep mascot in sync with the base theme unless user explicitly set a different mascot
    theme_to_mascot = {
        "water": "aqua",
        "sun": "sunrise",
        "green": "forest",
        "neon": "neon",
        "yin_yang": "yin_yang",
    }
    if "mascot_variant" not in st.session_state or st.session_state.get("mascot_variant") not in set(theme_to_mascot.values()):
        st.session_state["mascot_variant"] = theme_to_mascot.get(st.session_state.get("theme", "water"), "aqua")
