from __future__ import annotations

from datetime import datetime, timedelta, timezone

import streamlit as st

from components.cards import render_hero_banner


def render_reminder_page() -> None:
    render_hero_banner(
        "Hydration Reminders",
        "Stay on track with simple, flexible hydration reminders.",
        badge="Smart Reminder",
    )

    enabled = st.checkbox(
        "Enable hydration reminders",
        value=bool(st.session_state.get("reminders_enabled", True)),
        key="reminders_enabled",
    )

    interval = st.selectbox(
        "Reminder interval",
        [15, 30, 45, 60],
        index=[15, 30, 45, 60].index(
            st.session_state.get("reminder_interval", 60)
        ),
        format_func=lambda x: f"Every {x} minutes",
        key="reminder_interval",
    )

    if enabled:
        last_water = st.session_state.get("last_water_at")

        if last_water:
            try:
                last_time = datetime.fromisoformat(
                    str(last_water).replace("Z", "+00:00")
                )
                if last_time.tzinfo is None:
                    last_time = last_time.replace(tzinfo=timezone.utc)

                next_time = last_time + timedelta(minutes=int(interval))
                now = datetime.now(timezone.utc)
                remaining = next_time - now

                if remaining.total_seconds() > 0:
                    minutes = max(1, int(remaining.total_seconds() // 60))
                    st.info(f"💧 Next hydration reminder in about {minutes} minutes.")
                else:
                    st.warning("💧 Time for a hydration check-in!")
            except (ValueError, TypeError, OverflowError):
                st.info("💧 Log a drink to start your reminder timer.")
        else:
            st.info("💧 Log your first drink to start the reminder timer.")

    if st.button("🔔 Save reminder settings", use_container_width=True):
        # The checkbox/selectbox already own and update these session-state keys.
        # Do not assign to them again after widget creation, or Streamlit raises
        # StreamlitWidgetAlreadyInstantiatedError.
        st.success("Reminder settings saved.")
        st.rerun()
