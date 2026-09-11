import streamlit as st
from services.hydration import HydrationService
import pandas as pd
import altair as alt


def app():
    st.header('Stats')
    hs = HydrationService()
    history = hs.get_history()
    if not history:
        st.info('No data yet. Start tracking to see stats.')
        return

    df = pd.DataFrame(history)
    df['date'] = pd.to_datetime(df['intake_date'])
    daily = df.groupby('date', as_index=False)['total_ml'].sum()
    daily = daily.rename(columns={'total_ml': 'total'})

    chart = alt.Chart(daily).mark_line(point=True).encode(
        x='date:T',
        y='total:Q',
        tooltip=['date:T', 'total:Q']
    ).properties(width=700, height=300)

    st.altair_chart(chart, use_container_width=True)
    st.write('Summary')
    st.write(daily['total'].describe())
