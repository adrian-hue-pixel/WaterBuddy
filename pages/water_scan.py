from __future__ import annotations

import streamlit as st

from components.cards import render_hero_banner
from services.ai import ApiRateLimitError, analyze_water_bottle_image
from services.hydration import update_daily_intake


def _reset_scan() -> None:
    st.session_state.pop("water_scan_last_volume", None)
    st.session_state.pop("water_scan_last_capacity", None)


def render_water_scan_page() -> None:
    render_hero_banner(
        "Water Scan",
        "Show your bottle to the camera and let WaterBuddy estimate the water level.",
        badge="AI Vision",
    )

    st.info(
        "For the best estimate, use a clear photo with the whole bottle visible "
        "and keep it upright."
    )

    capacity = st.number_input(
        "Bottle capacity (ml)",
        min_value=100,
        max_value=5000,
        value=int(st.session_state.get("water_scan_capacity", 750)),
        step=50,
        key="water_scan_capacity",
        help="Use the bottle's labeled capacity when possible. This makes the estimate more accurate.",
    )

    photo = st.camera_input(
        "Show your bottle and take a photo",
        key="water_scan_camera",
    )

    if photo is None:
        st.caption(
            "Tip: a visible water line and a straight-on photo give the AI a better estimate."
        )
        return

    if st.button("🔍 Analyze water level", type="primary", use_container_width=True):
        with st.spinner("WaterBuddy is analyzing the bottle…"):
            try:
                result = analyze_water_bottle_image(
                    photo.getvalue(),
                    int(capacity),
                )
            except ApiRateLimitError as exc:
                wait = exc.retry_seconds
                if wait:
                    st.error(f"AI rate limit reached. Try again in about {wait} seconds.")
                else:
                    st.error("AI rate limit reached. Please try again shortly.")
                return
            except Exception as exc:
                st.error(f"Water Scan is temporarily unavailable: {exc}")
                return

        if result.get("error"):
            st.error(result["error"])
            return

        if not result.get("container_detected") or not result.get("water_visible"):
            st.warning(
                "I couldn't clearly identify the bottle and water level. "
                "Try a brighter, more straight-on photo."
            )
            if result.get("note"):
                st.caption(result["note"])
            return

        current_ml = int(result.get("current_water_ml", 0))
        fill_percent = int(result.get("fill_percent", 0))
        confidence = str(result.get("confidence", "Low"))

        previous_ml = st.session_state.get("water_scan_last_volume")
        previous_capacity = st.session_state.get("water_scan_last_capacity")

        st.session_state["water_scan_result"] = result
        st.session_state["water_scan_current_volume"] = current_ml
        st.session_state["water_scan_current_percent"] = fill_percent
        st.session_state["water_scan_current_confidence"] = confidence

        if previous_ml is not None and int(previous_capacity or capacity) == int(capacity):
            consumed = max(0, int(previous_ml) - current_ml)
            st.session_state["water_scan_consumed"] = consumed

        st.session_state["water_scan_last_volume"] = current_ml
        st.session_state["water_scan_last_capacity"] = int(capacity)

    result = st.session_state.get("water_scan_result")

    if not result:
        return

    current_ml = int(st.session_state.get("water_scan_current_volume", 0))
    fill_percent = int(st.session_state.get("water_scan_current_percent", 0))
    confidence = st.session_state.get("water_scan_current_confidence", "Low")

    st.divider()
    st.subheader("💧 Scan result")

    col1, col2, col3 = st.columns(3)
    col1.metric("Current water", f"{current_ml} ml")
    col2.metric("Fill level", f"{fill_percent}%")
    col3.metric("Confidence", confidence)

    if result.get("note"):
        st.caption(result["note"])

    consumed = st.session_state.get("water_scan_consumed")

    if consumed is not None and consumed > 0:
        st.success(
            f"💧 Estimated water consumed since your previous scan: **~{consumed} ml**"
        )

        if st.button(
            f"➕ Add ~{consumed} ml to today's intake",
            type="primary",
            use_container_width=True,
            key="add_scanned_water",
        ):
            update_daily_intake(consumed, "AI water scan")
            st.session_state.pop("water_scan_consumed", None)
            st.success(f"Added {consumed} ml to today's hydration!")
            st.rerun()

    elif consumed == 0:
        st.info(
            "The water level looks about the same as your previous scan, "
            "so no water was automatically counted."
        )
    else:
        st.info(
            "This is your first scan. Scan the same bottle again after drinking "
            "to estimate how much you consumed."
        )

    if st.button("🔄 Start a new bottle / reset scan", key="reset_water_scan"):
        _reset_scan()
        st.rerun()
