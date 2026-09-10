from __future__ import annotations

from datetime import datetime

import streamlit as st
from plotly import graph_objects as go

from components.cards import render_hero_banner
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
    # Clean metric row — intentionally separate from the generic stat-card
    # component so Analytics keeps the same minimal visual language as AI Hydration.
    metrics = [
        ("Days tracked", str(summary["days_tracked"])),
        ("Best day", f"{summary['best_day']:,} ml"),
        ("Average", f"{summary['average_daily']:,.1f} ml"),
        ("Peak day", summary["most_active_day"]),
    ]

    metric_html = "".join(
        f"""
        <div class="analytics-metric">
            <div class="analytics-metric-icon">✦</div>
            <div class="analytics-metric-label">{label}</div>
            <div class="analytics-metric-value">{value}</div>
        </div>
        """
        for label, value in metrics
    )

    st.html(
        f"""
        <div class="analytics-metrics">
            {metric_html}
        </div>

        <style>
            .analytics-metrics {{
                display: grid;
                grid-template-columns: repeat(4, minmax(0, 1fr));
                gap: 18px;
                margin: 2.25rem 0 3.2rem 0;
            }}

            .analytics-metric {{
                position: relative;
                min-width: 0;
                padding: 21px 22px 23px;
                border-radius: 18px;
                overflow: hidden;

                background:
                    linear-gradient(
                        145deg,
                        rgba(18, 48, 70, 0.72),
                        rgba(6, 18, 31, 0.72)
                    );
                border: 1px solid rgba(92, 225, 230, 0.12);

                box-shadow:
                    0 16px 45px rgba(0, 0, 0, 0.22),
                    inset 0 1px 0 rgba(255, 255, 255, 0.035);

                backdrop-filter: blur(16px);
            }}

            .analytics-metric::after {{
                content: "";
                position: absolute;
                width: 90px;
                height: 90px;
                right: -45px;
                top: -45px;
                border-radius: 50%;
                background: rgba(92, 225, 230, 0.10);
                filter: blur(25px);
                pointer-events: none;
            }}

            .analytics-metric-icon {{
                width: 26px;
                height: 26px;
                margin-bottom: 15px;

                display: flex;
                align-items: center;
                justify-content: center;

                color: #5ce1e6;
                font-size: 15px;
                text-shadow: 0 0 16px rgba(92, 225, 230, 0.65);
            }}

            .analytics-metric-label {{
                margin-bottom: 7px;
                color: #9ca3af;
                font-size: 13px;
                line-height: 1.3;
                font-weight: 550;
            }}

            .analytics-metric-value {{
                color: #ffffff;
                font-size: 17px;
                line-height: 1.25;
                font-weight: 700;
                letter-spacing: -0.01em;
            }}

            @media (max-width: 900px) {{
                .analytics-metrics {{
                    grid-template-columns: repeat(2, minmax(0, 1fr));
                }}
            }}

            @media (max-width: 560px) {{
                .analytics-metrics {{
                    grid-template-columns: 1fr;
                    gap: 12px;
                    margin-bottom: 2.4rem;
                }}
            }}
        </style>
        """
    )

    if history:
        palette = _get_theme_palette()
        ordered_history = sorted(history, key=lambda item: str(item.get("intake_date", "")))

        def _display_date(item):
            raw = str(item.get("intake_date", ""))
            try:
                return datetime.strptime(raw[:10], "%Y-%m-%d").strftime("%b %-d")
            except ValueError:
                return raw[:10] or "—"

        dates = [_display_date(item) for item in ordered_history]
        values = [int(item.get("total_ml", 0) or 0) for item in ordered_history]
        goal = int(st.session_state.get("goal_ml", 2500))

        st.html(
            f"""
            <div class="ai-panel" style="
                margin-top: 1.4rem;
                margin-bottom: 0.8rem;
                padding: 1.15rem 1.35rem;
                border-radius: 20px;
            ">
                <div style="
                    font-size: 0.78rem;
                    font-weight: 750;
                    letter-spacing: 0.12em;
                    text-transform: uppercase;
                    color: {palette["primary"]};
                    margin-bottom: 0.35rem;
                ">Hydration trend</div>

                <div style="
                    font-size: 1.35rem;
                    font-weight: 800;
                    color: {palette["text"]};
                    margin-bottom: 0.25rem;
                ">Your last 7 days</div>

                <div style="
                    font-size: 0.88rem;
                    color: {palette["muted"]};
                ">Daily intake compared with your hydration goal.</div>
            </div>
            """
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
                title=dict(
                    text="Intake (ml)",
                    font=dict(
                        color=palette["text"],
                        size=13,
                    ),
                    standoff=28,
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

        st.html(
            f"""
            <div style="
                margin-top: 0.35rem;
                margin-bottom: -0.15rem;
                padding-left: 0.15rem;
                font-size: 0.78rem;
                color: {palette["muted"]};
            ">
                Goal: <strong style="color:{palette["text"]};">{goal:,} ml</strong> per day
            </div>
            """
        )

        st.html(
            """
            <style>
                div[data-testid="stPlotlyChart"] {
                    position: relative;
                    padding: 18px 18px 8px;
                    margin-top: 0.25rem;
                    border-radius: 22px;

                    background:
                        linear-gradient(
                            145deg,
                            rgba(10, 31, 48, 0.88),
                            rgba(3, 12, 22, 0.92)
                        );

                    border: 1px solid rgba(92, 225, 230, 0.10);

                    box-shadow:
                        0 24px 70px rgba(0, 0, 0, 0.30),
                        0 0 55px rgba(42, 190, 220, 0.055),
                        inset 0 1px 0 rgba(255, 255, 255, 0.035);
                }
            </style>
            """
        )

        st.plotly_chart(
            fig,
            use_container_width=True,
            theme=None,
        )
    else:
        st.info("No hydration history yet — start logging and your weekly trend will appear here.")
