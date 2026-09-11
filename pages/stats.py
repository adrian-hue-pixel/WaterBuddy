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

    chart = (
        alt.Chart(daily)
        .mark_line(point=True)
        .encode(
            x=alt.X('date:T', title='Date'),
            y=alt.Y(
                'total:Q',
                title='Intake (ml)',
                axis=alt.Axis(
                    format=',d',
                    labelPadding=8,
                    titlePadding=18,
                    labelLimit=90,
                    minExtent=70,
                ),
                scale=alt.Scale(zero=True),
            ),
            tooltip=[
                alt.Tooltip('date:T', title='Date'),
                alt.Tooltip('total:Q', title='Intake', format=',d'),
            ],
        )
        .properties(width='container', height=300)
        .configure_axis(labelFontSize=13, titleFontSize=13)
    )

    st.altair_chart(chart, use_container_width=True)
    st.write('Summary')
    st.write(daily['total'].describe())
