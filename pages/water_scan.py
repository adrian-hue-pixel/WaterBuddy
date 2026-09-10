from __future__ import annotations

from datetime import datetime

import streamlit as st

from components.cards import render_hero_banner
from services.ai import ApiRateLimitError, analyze_water_bottle_image
from services.hydration import update_daily_intake


def _scan_history() -> list[dict]:
    return st.session_state.setdefault("water_scan_history", [])


def _reset_scan() -> None:
    for key in (
        "water_scan_last_volume",
        "water_scan_last_capacity",
        "water_scan_result",
        "water_scan_current_volume",
        "water_scan_current_percent",
        "water_scan_current_confidence",
        "water_scan_consumed",
    ):
        st.session_state.pop(key, None)


def _bottle_profiles() -> dict[str, int]:
    return st.session_state.setdefault(
        "water_scan_bottles",
        {
            "My Bottle": 750,
            "Large Bottle": 1000,
        },
    )


def render_water_scan_page() -> None:
    render_hero_banner(
        "Water Scan",
        "Use AI vision to estimate your bottle's water level and track changes between scans.",
        badge="AI Vision 2.0",
    )

    st.info(
        "For the best estimate, keep the whole bottle visible, upright, and "
        "well lit. Scan results are approximate."
    )

    bottles = _bottle_profiles()

    bottle_name = st.selectbox(
        "Bottle",
        list(bottles.keys()),
        key="water_scan_bottle_name",
    )

    capacity = st.number_input(
        "Bottle capacity (ml)",
        min_value=100,
        max_value=5000,
        value=int(bottles[bottle_name]),
        step=50,
        key="water_scan_capacity",
        help="Use the bottle's labeled capacity when possible.",
    )

    if bottles.get(bottle_name) != int(capacity):
        bottles[bottle_name] = int(capacity)

    photo = st.camera_input(
        "Show your bottle and take a photo",
        key="water_scan_camera",
    )

    if photo is None:
        st.caption(
            "Tip: a visible water line and a straight-on photo give the AI a better estimate."
        )

    if photo is not None and st.button(
        "🔍 Analyze water level",
        type="primary",
        use_container_width=True,
    ):
        with st.spinner("WaterBuddy is analyzing the bottle…"):
            try:
                result = analyze_water_bottle_image(
                    photo.getvalue(),
                    int(capacity),
                )
            except ApiRateLimitError as exc:
                wait = exc.retry_seconds
                if wait:
                    st.error(
                        f"AI rate limit reached. Try again in about {wait} seconds."
                    )
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

        consumed = None
        event = "baseline"

        if previous_ml is not None and int(previous_capacity or capacity) == int(capacity):
            difference = int(previous_ml) - current_ml

            if difference >= 25:
                consumed = difference
                event = "drank"

            elif difference <= -50:
                event = "refilled"

            else:
                consumed = 0
                event = "unchanged"

        scan = {
            "time": datetime.now().strftime("%H:%M"),
            "bottle": bottle_name,
            "capacity_ml": int(capacity),
            "current_ml": current_ml,
            "fill_percent": fill_percent,
            "confidence": confidence,
            "event": event,
        }

        _scan_history().append(scan)

        st.session_state["water_scan_result"] = result
        st.session_state["water_scan_current_volume"] = current_ml
        st.session_state["water_scan_current_percent"] = fill_percent
        st.session_state["water_scan_current_confidence"] = confidence
        st.session_state["water_scan_consumed"] = consumed
        st.session_state["water_scan_last_volume"] = current_ml
        st.session_state["water_scan_last_capacity"] = int(capacity)

    result = st.session_state.get("water_scan_result")

    if not result:
        return

    current_ml = int(st.session_state.get("water_scan_current_volume", 0))
    fill_percent = int(st.session_state.get("water_scan_current_percent", 0))
    confidence = st.session_state.get("water_scan_current_confidence", "Low")
    consumed = st.session_state.get("water_scan_consumed")

    st.divider()
    st.subheader("💧 Scan result")

    col1, col2, col3 = st.columns(3)
    col1.metric("Current water", f"{current_ml} ml")
    col2.metric("Fill level", f"{fill_percent}%")
    col3.metric("Confidence", confidence)

    if result.get("note"):
        st.caption(result["note"])

    if consumed is not None and consumed > 0:
        st.success(
            f"💧 Estimated drinking since your previous scan: **~{consumed} ml**"
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
            "so nothing was counted."
        )

    elif _scan_history() and _scan_history()[-1]["event"] == "refilled":
        st.info(
            "🔄 It looks like the bottle was refilled. "
            "The refill was not counted as drinking."
        )

    else:
        st.info(
            "This is your baseline scan. Scan the same bottle again after "
            "drinking to estimate how much you consumed."
        )

    history = _scan_history()

    if history:
        st.divider()
        st.subheader("📊 Scan history")

        for scan in reversed(history[-8:]):
            event_labels = {
                "baseline": "📍 Baseline",
                "drank": "💧 Drinking detected",
                "refilled": "🔄 Refill detected",
                "unchanged": "➖ No major change",
            }

            st.write(
                f"**{scan['time']}** · {scan['bottle']} · "
                f"{scan['current_ml']} ml ({scan['fill_percent']}%) · "
                f"{event_labels.get(scan['event'], scan['event'])}"
            )

    col_a, col_b = st.columns(2)

    with col_a:
        if st.button(
            "🔄 Start a new bottle / reset",
            key="reset_water_scan",
            use_container_width=True,
        ):
            _reset_scan()
            st.rerun()

    with col_b:
        if st.button(
            "🗑️ Clear scan history",
            key="clear_water_scan_history",
            use_container_width=True,
        ):
            st.session_state["water_scan_history"] = []
            _reset_scan()
            st.rerun()
