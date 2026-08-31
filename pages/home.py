import streamlit as st

from core.session_manager import safe_rerun
from services.hydration import HydrationService


def app():
    st.title('WaterBuddy — Stay hydrated 💧')
    st.markdown('A friendly app to help you track your daily water intake and reach hydration goals.')

    hs = HydrationService()
    goal = hs.get_goal()
    today_total = hs.get_today_total()

    st.metric('Today', f"{today_total} ml", delta=f"{max(0, goal - today_total)} ml to goal" if goal else None)

    if goal:
        pct = min(1.0, today_total / goal)
        st.progress(pct)
        st.caption(f"Daily goal: {goal} ml")
    else:
        st.info('No daily goal set. Go to Goals to set one.')

    st.subheader('Quick actions')
    col1, col2, col3 = st.columns(3)
    if col1.button('Add 250 ml'):
        hs.add_entry(250)
        st.rerun() if hasattr(st, "rerun") else st.experimental_rerun()
    if col2.button('Add 500 ml'):
        hs.add_entry(500)
        st.rerun() if hasattr(st, "rerun") else st.experimental_rerun()
    if col3.button('Undo last'):
        hs.undo_last()
        st.rerun() if hasattr(st, "rerun") else st.experimental_rerun()

    st.subheader('Recent entries')
    entries = hs.get_today_entries(limit=10)
    if entries:
        for e in reversed(entries):
            st.write(f"• {e['amount']} ml — {e['time']}")
    else:
        st.write('No entries yet. Start by adding water!')

    st.markdown('---')
    st.write('Pro tip: Use the Track Water page for manual entries, and check Stats for trends.')
