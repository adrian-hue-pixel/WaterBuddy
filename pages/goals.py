import streamlit as st

from core.session_manager import safe_rerun
from services.hydration import HydrationService


def app():
    st.header('Goals')
    st.write('Set your daily hydration goal.')
    hs = HydrationService()
    current = hs.get_goal() or 2000
    new_goal = st.number_input('Daily goal (ml)', min_value=200, max_value=10000, value=current, step=50)
    if st.button('Save goal'):
        hs.set_goal(int(new_goal))
        st.success('Goal saved')
        st.rerun() if hasattr(st, "rerun") else st.experimental_rerun()

    st.markdown('---')
    st.write('Why set a goal?')
    st.write('A daily goal helps build consistent hydration habits. Adjust for activity, climate, and body size.')


    st.markdown("### Goal progress")

    goal = int(st.session_state.get("goal_ml", 2500))
    intake = int(st.session_state.get("daily_intake_ml", 0))
    progress = min(int((intake / goal) * 100), 100) if goal > 0 else 0

    st.progress(progress / 100)
    st.caption(f"{intake:,} ml / {goal:,} ml · {progress}% complete")

    if progress >= 100:
        st.success("🏆 Daily hydration goal complete!")
    elif progress >= 75:
        st.info("🔥 You're 75% of the way there!")
    elif progress >= 50:
        st.info("💧 Halfway there — keep going!")
    elif progress >= 25:
        st.info("🌊 Great start — keep building your progress!")
