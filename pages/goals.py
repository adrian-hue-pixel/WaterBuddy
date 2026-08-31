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
