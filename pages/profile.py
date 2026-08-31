from __future__ import annotations

import streamlit as st

from components.cards import render_hero_banner
from database.manager import load_profile, save_profile
from services.hydration import get_age_goal


def render_profile_page() -> None:
    render_hero_banner(
        "Profile",
        "Set a profile that shapes your hydration goal and the tone of your coaching.",
        badge="Personalization",
    )
    user_id = st.session_state.get("user_id")
    saved_profile = load_profile(user_id=user_id)
    if saved_profile:
        st.session_state["profile_name"] = saved_profile.get("name", "")
        st.session_state["age_group"] = saved_profile.get("age_group", "19–50")
        st.session_state["goal_ml"] = saved_profile.get("goal_ml", get_age_goal(saved_profile.get("age_group", "19–50")))

    prev_age = st.session_state.get("age_group", "19–50")
    age_group = st.selectbox(
        "Age group",
        ["6–12", "13–18", "19–50", "65+"],
        index=["6–12", "13–18", "19–50", "65+"].index(prev_age),
        key="age_group",
    )

    # New personalization inputs: climate and activity
    climate = st.selectbox(
        "Typical climate",
        ["temperate", "hot", "cold"],
        index=["temperate", "hot", "cold"].index(st.session_state.get("profile_climate", "temperate")),
        format_func=lambda v: {"temperate": "Temperate", "hot": "Hot", "cold": "Cold"}.get(v, v.title()),
        key="profile_climate",
    )
    activity = st.selectbox(
        "Activity level",
        ["low", "moderate", "high"],
        index=["low", "moderate", "high"].index(st.session_state.get("profile_activity", "moderate")),
        format_func=lambda v: {"low": "Low", "moderate": "Moderate", "high": "High"}.get(v, v.title()),
        key="profile_activity",
    )

    from services.personalization import compute_goal_ml

    suggested_goal = compute_goal_ml(age_group, climate, activity)
    # If user hasn't explicitly set a custom goal, prefill with suggested
    if "goal_ml" not in st.session_state or not st.session_state.get("goal_override", False):
        st.session_state["goal_ml"] = suggested_goal

    name = st.text_input("Name", value=st.session_state.get("profile_name", ""), key="profile_name")
    # Allow user to override the suggested goal; mark goal_override if changed manually
    goal_ml = st.number_input(
        "Daily hydration goal (ml)",
        min_value=1000,
        max_value=5000,
        step=50,
        value=int(st.session_state.get("goal_ml", suggested_goal)),
        key="goal_ml",
    )

    if int(goal_ml) != suggested_goal:
        st.session_state["goal_override"] = True

    notes = st.text_area("Notes", value=st.session_state.get("profile_notes", ""), key="profile_notes")

    st.markdown(f"**Calculated suggestion:** Based on your age ({age_group}), climate ({climate.title()}), and activity ({activity.title()}), a recommended daily goal is **{suggested_goal} ml**. You can adjust this number above to personalize it further.")

    if st.button("Save profile"):
        save_profile(name, age_group, int(goal_ml), notes, user_id=user_id)
        st.session_state["goal_override"] = True
        # Mark profile complete so the app unlocks other pages
        st.session_state["profile_complete"] = True
        st.success("Profile saved. Your hydration plan is ready.")
        # After saving profile, request navigation to Dashboard on next render
        st.session_state["pending_page_nav"] = "Dashboard"
        st.rerun() if hasattr(st, "rerun") else st.experimental_rerun()
    