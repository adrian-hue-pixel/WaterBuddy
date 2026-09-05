from __future__ import annotations

import streamlit as st
from plotly import graph_objects as go

from components.cards import render_hero_banner, render_stat_card
from database.manager import get_recent_history
from services.analytics import summarize_history


def _get_theme_palette() -> dict[str, str]:
    base = str(st.session_state.get("theme", "water")).lower()
    dark = bool(st.session_state.get("dark_mode", False))
    # Map base themes to internal palette keys
    base_map = {"water": "ocean", "sun": "sunrise", "green": "forest"}
    key = base_map.get(base, "ocean")

    palettes = {
        "ocean": {
            "bg": "rgba(0,0,0,0)",
            "surface": "rgba(7,31,49,0.76)",
            "text": "#e6f9ff",
            "muted": "#a4d7ea",
            "primary": "#41d8ff",
            "accent": "#5cb8ff",
            "goal": "#ffb46b",
            "grid": "rgba(128,205,239,0.18)",
            "area": "rgba(65,216,255,0.18)",
        },
        "sunrise": {
            "bg": "rgba(0,0,0,0)",
            "surface": "rgba(255,245,238,0.82)",
            "text": "#3f2618",
            "muted": "#805c4d",
            "primary": "#ff8d5c",
            "accent": "#d96d3d",
            "goal": "#fb923c",
            "grid": "rgba(108,70,56,0.12)",
            "area": "rgba(255,141,92,0.18)",
        },
        "forest": {
            "bg": "rgba(0,0,0,0)",
            "surface": "rgba(12,34,28,0.76)",
            "text": "#ecfdf5",
            "muted": "#bfe4d2",
            "primary": "#64d79d",
            "accent": "#55b882",
            "goal": "#f2c66d",
            "grid": "rgba(123,193,152,0.18)",
            "area": "rgba(100,215,157,0.18)",
        },
        "light": {
            "bg": "rgba(0,0,0,0)",
            "surface": "rgba(255,255,255,0.82)",
            "text": "#11314d",
            "muted": "#4b647c",
            "primary": "#12b7d6",
            "accent": "#1d63d4",
            "goal": "#f5792c",
            "grid": "rgba(17,49,77,0.10)",
            "area": "rgba(18,183,214,0.18)",
        },
        "dark": {
            "bg": "rgba(0,0,0,0)",
            "surface": "rgba(10,20,34,0.72)",
            "text": "#eef7ff",
            "muted": "#93b4cf",
            "primary": "#6de9ff",
            "accent": "#5fb0ff",
            "goal": "#ffb069",
            "grid": "rgba(255,255,255,0.10)",
            "area": "rgba(109,233,255,0.20)",
        },
    }

    palette = palettes.get(key, palettes["light"]).copy()
    if dark:
        # Blend in dark overrides from the 'dark' palette for contrast
        dark_palette = palettes["dark"]
        for k, v in dark_palette.items():
            # Only override a small set of tokens we care about for charts
            if k in {"surface", "text", "muted", "primary", "accent", "goal", "grid", "area"}:
                palette[k] = v
    return palette


def render_analytics_page() -> None:
    render_hero_banner(
        "Insights",
        "Review your hydration rhythm and spot your strongest days at a glance.",
        badge="Weekly analytics",
    )
    history = get_recent_history(days=7, user_id=st.session_state.get("user_id"))
    summary = summarize_history(history)
    stats = st.columns(4)
    with stats[0]:
        render_stat_card("Days tracked", str(summary["days_tracked"]), "primary")
    with stats[1]:
        render_stat_card("Best day", f"{summary['best_day']} ml", "accent")
    with stats[2]:
        render_stat_card("Average", f"{summary['average_daily']} ml", "primary")
    with stats[3]:
        render_stat_card("Peak day", summary["most_active_day"], "accent")

    if history:
        palette = _get_theme_palette()
        ordered_history = sorted(history, key=lambda item: str(item.get("intake_date", "")))
        dates = [str(item.get("intake_date", "")) for item in ordered_history]
        values = [int(item.get("total_ml", 0) or 0) for item in ordered_history]
        goal = int(st.session_state.get("goal_ml", 2500))

        st.markdown(
            f"""
            <div style="
                margin: 1.2rem 0 0.6rem 0;
                font-size: 1.35rem;
                font-weight: 800;
                color: {palette["text"]};
                letter-spacing: 0.08em;
            ">GRAPH</div>
            """,
            unsafe_allow_html=True,
        )

        fig = go.Figure()

        fig.add_trace(
            go.Bar(
                x=dates,
                y=values,
                name="Daily intake",
                marker=dict(
                    color=palette["primary"],
                    line=dict(color=palette["accent"], width=1),
                ),
                hovertemplate="%{x}<br>%{y:.0f} ml<extra></extra>",
            )
        )

        fig.add_hline(
            y=goal,
            line_dash="dot",
            line_color=palette["goal"],
            line_width=2,
            annotation_text="Goal",
            annotation_position="right top",
            annotation_font=dict(
                color=palette["goal"],
                size=11,
            ),
        )

        fig.update_layout(
            height=380,
            margin=dict(l=20, r=20, t=25, b=40),
            paper_bgcolor=palette["bg"],
            plot_bgcolor=palette["bg"],
            hovermode="x",
            font=dict(
                color=palette["text"],
                family="sans-serif",
            ),
            showlegend=False,
            xaxis=dict(
                title="Day",
                title_font=dict(
                    color=palette["text"],
                    size=13,
                ),
                tickfont=dict(
                    color=palette["text"],
                    size=12,
                ),
                gridcolor=palette["grid"],
                zeroline=False,
                showline=False,
            ),
            yaxis=dict(
                title="Intake (ml)",
                title_font=dict(
                    color=palette["text"],
                    size=13,
                ),
                tickfont=dict(
                    color=palette["text"],
                    size=12,
                ),
                gridcolor=palette["grid"],
                zeroline=False,
                rangemode="tozero",
            ),
        )

        st.plotly_chart(
            fig,
            use_container_width=True,
            theme=None,
        )
    else:
        st.info("No hydration history yet — start logging and your weekly trend will appear here.")
