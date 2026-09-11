from __future__ import annotations

import streamlit as st

from components.cards import render_hero_banner
from database.manager import load_profile, save_profile
from services.hydration import get_age_goal


st.html("""
<style>
/* =========================================================
   WaterBuddy Profile — premium personalization UI
   Functionality intentionally untouched.
   ========================================================= */

.profile-section {
    margin: 28px 0 12px;
}

.profile-section-label {
    color: #38bdf8;
    font-size: 10px;
    font-weight: 800;
    letter-spacing: .16em;
    text-transform: uppercase;
    margin-bottom: 6px;
}

.profile-section-title {
    color: #f5fbff;
    font-family: "Manrope", "DM Sans", sans-serif;
    font-size: 22px;
    font-weight: 800;
    letter-spacing: -.025em;
    margin: 0;
}

.profile-section-subtitle {
    margin-top: 5px;
    color: #718696;
    font-size: 13px;
    line-height: 1.55;
}

/* Form controls */
[data-testid="stSelectbox"] > div > div,
[data-testid="stTextInput"] > div,
[data-testid="stTextArea"] > div,
[data-testid="stNumberInput"] > div {
    border-radius: 15px !important;
    border-color: rgba(56,189,248,.13) !important;
    background: rgba(7,19,30,.78) !important;
}

[data-testid="stSelectbox"] label,
[data-testid="stTextInput"] label,
[data-testid="stTextArea"] label,
[data-testid="stNumberInput"] label {
    color: #9eb2c0 !important;
    font-weight: 650 !important;
}

/* Goal controls */
[data-testid="stNumberInput"] {
    margin-top: 0 !important;
}

[data-testid="stNumberInput"] button {
    border-radius: 10px !important;
}

.profile-goal-row {
    margin: 8px 0 20px;
    padding: 18px;
    border-radius: 22px;
    border: 1px solid rgba(56,189,248,.12);
    background:
        radial-gradient(
            circle at 50% 0%,
            rgba(56,189,248,.06),
            transparent 58%
        ),
        rgba(7,19,30,.72);
    box-shadow:
        0 18px 42px rgba(0,0,0,.18),
        inset 0 1px 0 rgba(255,255,255,.025);
}

/* Buttons */
.stButton > button {
    min-height: 44px !important;
    border-radius: 14px !important;
    border: 1px solid rgba(56,189,248,.16) !important;
    background:
        linear-gradient(
            135deg,
            rgba(17,48,66,.92),
            rgba(7,24,37,.96)
        ) !important;
    color: #eafaff !important;
    font-weight: 750 !important;
    box-shadow:
        0 10px 26px rgba(0,0,0,.18),
        inset 0 1px 0 rgba(255,255,255,.025) !important;
    transition: all .18s ease !important;
}

.stButton > button:hover {
    border-color: rgba(56,189,248,.40) !important;
    background:
        linear-gradient(
            135deg,
            rgba(21,61,82,.96),
            rgba(8,29,44,.98)
        ) !important;
    box-shadow:
        0 12px 30px rgba(0,0,0,.24),
        0 0 24px rgba(56,189,248,.08) !important;
    transform: translateY(-1px);
}

/* Save button gets stronger visual priority */
.stButton > button[kind="primary"] {
    border-color: rgba(56,189,248,.32) !important;
}

/* Calculated recommendation */
.profile-recommendation {
    margin: 22px 0 24px;
    padding: 18px 20px;
    border-radius: 20px;
    border: 1px solid rgba(245,158,11,.14);
    background:
        linear-gradient(
            135deg,
            rgba(245,158,11,.055),
            rgba(7,19,30,.76)
        );
    box-shadow:
        0 14px 34px rgba(0,0,0,.16),
        inset 0 1px 0 rgba(255,255,255,.02);
}

.profile-recommendation-label {
    color: #f59e0b;
    font-size: 10px;
    font-weight: 800;
    letter-spacing: .15em;
    text-transform: uppercase;
    margin-bottom: 7px;
}

.profile-recommendation-text {
    color: #9eb2c0;
    font-size: 13px;
    line-height: 1.6;
}

.profile-recommendation-value {
    color: #f5fbff;
    font-weight: 800;
}

/* Success message */
[data-testid="stAlert"] {
    border-radius: 18px !important;
}

/* Mobile */
@media (max-width: 640px) {
    .profile-section-title {
        font-size: 19px;
    }

    .profile-goal-row {
        padding: 15px;
        border-radius: 18px;
    }

    .profile-recommendation {
        padding: 16px;
        border-radius: 18px;
    }
}
</style>
""")


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

    st.html("""
    <div class="profile-section">
        <div class="profile-section-label">Personalization</div>
        <div class="profile-section-title">Your hydration profile</div>
        <div class="profile-section-subtitle">
            A few details help WaterBuddy tailor your daily hydration plan.
        </div>
    </div>
    """)

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
    # Hydration goal controls: manual entry + reliable +/- buttons.
    if "goal_ml" not in st.session_state:
        st.session_state["goal_ml"] = suggested_goal

    if "goal_ml_input" not in st.session_state:
        st.session_state["goal_ml_input"] = int(st.session_state["goal_ml"])

    current_goal = int(st.session_state.get("goal_ml_input", suggested_goal))
    current_goal = max(1000, min(5000, current_goal))

    st.html("""
    <div class="profile-section">
        <div class="profile-section-label">Daily target</div>
        <div class="profile-section-title">Hydration goal</div>
        <div class="profile-section-subtitle">
            WaterBuddy suggests a target from your profile. Adjust it if you want a more personal goal.
        </div>
    </div>
    """)

    def _decrease_goal():
        new_goal = max(1000, int(st.session_state.get("goal_ml_input", current_goal)) - 50)
        st.session_state["goal_ml_input"] = new_goal
        st.session_state["goal_ml"] = new_goal
        st.session_state["goal_override"] = True

    def _increase_goal():
        new_goal = min(5000, int(st.session_state.get("goal_ml_input", current_goal)) + 50)
        st.session_state["goal_ml_input"] = new_goal
        st.session_state["goal_ml"] = new_goal
        st.session_state["goal_override"] = True

    st.html('<div class="profile-goal-row">')
    goal_cols = st.columns([1, 3, 1])

    with goal_cols[0]:
        st.button(
            "−",
            key="goal_minus",
            use_container_width=True,
            on_click=_decrease_goal,
        )

    with goal_cols[1]:
        st.html("""
        <style>
        div[data-testid="stNumberInput"] button {
            display: none !important;
        }
        </style>
        """)
        goal_ml = st.number_input(
            "Daily hydration goal (ml)",
            min_value=1000,
            max_value=5000,
            step=50,
            key="goal_ml_input",
            label_visibility="collapsed",
        )
        st.session_state["goal_ml"] = int(goal_ml)

    with goal_cols[2]:
        st.button(
            "+",
            key="goal_plus",
            use_container_width=True,
            on_click=_increase_goal,
        )

    if int(goal_ml) != suggested_goal:
        st.session_state["goal_override"] = True

    st.html('</div>')

    notes = st.text_area("Notes", value=st.session_state.get("profile_notes", ""), key="profile_notes")

    st.html(f"""
    <div class="profile-recommendation">
        <div class="profile-recommendation-label">WaterBuddy recommendation</div>
        <div class="profile-recommendation-text">
            Based on your age ({age_group}), climate ({climate.title()}), and
            activity ({activity.title()}), WaterBuddy recommends
            <span class="profile-recommendation-value">{suggested_goal} ml</span>
            per day.
            You can adjust the target above to personalize it further.
        </div>
    </div>
    """)

    if st.button("Save profile"):
        save_profile(name, age_group, int(goal_ml), notes, user_id=user_id)
        st.session_state["goal_override"] = True
        # Mark profile complete so the app unlocks other pages
        st.session_state["profile_complete"] = True
        st.success("Profile saved. Your hydration plan is ready.")
        # After saving profile, request navigation to Dashboard on next render
        st.session_state["pending_page_nav"] = "Dashboard"
        st.rerun() if hasattr(st, "rerun") else st.experimental_rerun()
    