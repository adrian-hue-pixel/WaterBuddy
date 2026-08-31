import streamlit as st

from core.session_manager import safe_rerun
from services.hydration import HydrationService


def app():
    st.header('Track Water')
    st.write('Log the water you drink quickly.')
    hs = HydrationService()

    with st.form('add_form'):
        amount = st.number_input('Amount (ml)', min_value=10, max_value=5000, value=250, step=10)
        note = st.text_input('Optional note')
        submitted = st.form_submit_button('Add')
    if submitted:
        hs.add_entry(int(amount), note=note)
        st.success(f'Added {amount} ml')

    st.markdown('### Fast add')
    col1, col2, col3, col4 = st.columns(4)
    if col1.button('100 ml'):
        hs.add_entry(100)
        st.rerun() if hasattr(st, "rerun") else st.experimental_rerun()
    if col2.button('200 ml'):
        hs.add_entry(200)
        st.rerun() if hasattr(st, "rerun") else st.experimental_rerun()
    if col3.button('300 ml'):
        hs.add_entry(300)
        st.rerun() if hasattr(st, "rerun") else st.experimental_rerun()
    if col4.button('500 ml'):
        hs.add_entry(500)
        st.rerun() if hasattr(st, "rerun") else st.experimental_rerun()

    st.markdown('---')
    st.subheader('Today')
    total = hs.get_today_total()
    st.write(f'Total: **{total} ml**')
    st.write('Recent entries:')
    for e in reversed(hs.get_today_entries(20)):
        st.write(f"• {e['amount']} ml — {e['time']} {('- ' + e['note']) if e.get('note') else ''}")
