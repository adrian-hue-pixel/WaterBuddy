import streamlit as st


def apply_theme():
    st.markdown(
        """
        <style>
        :root {
            color-scheme: light;
        }
        .stApp {
            background: linear-gradient(135deg, #f6fcff 0%, #eefcfb 100%);
            color: #0f172a;
        }
        [data-testid="stSidebar"] {
            background: linear-gradient(180deg, #06131f 0%, #124057 100%);
            color: #f8fafc;
        }
        [data-testid="stSidebar"] .block-container {
            padding-top: 1.2rem;
        }
        .hero-card {
            background: linear-gradient(135deg, rgba(14, 165, 164, 0.96), rgba(37, 99, 235, 0.92));
            border-radius: 24px;
            padding: 24px 28px;
            color: white;
            box-shadow: 0 20px 45px rgba(15, 23, 42, 0.14);
            margin-bottom: 18px;
        }
        .hero-card h1 {
            font-size: 2rem;
            margin-bottom: 0.25rem;
            font-weight: 800;
        }
        .hero-card p {
            margin: 0;
            color: rgba(255,255,255,0.93);
            line-height: 1.5;
            font-size: 1rem;
        }
        .pill {
            display: inline-block;
            padding: 6px 12px;
            border-radius: 999px;
            background: rgba(255,255,255,0.18);
            font-size: 0.8rem;
            font-weight: 700;
            margin-bottom: 10px;
            letter-spacing: 0.04em;
            text-transform: uppercase;
        }
        .metric-card {
            background: white;
            border: 1px solid rgba(15, 23, 42, 0.06);
            border-radius: 18px;
            padding: 16px;
            box-shadow: 0 10px 24px rgba(15, 23, 42, 0.08);
            min-height: 132px;
            margin-bottom: 14px;
        }
        .metric-card .label {
            font-size: 0.78rem;
            text-transform: uppercase;
            letter-spacing: 0.08em;
            color: #64748b;
            font-weight: 700;
        }
        .metric-card .value {
            font-size: 1.55rem;
            font-weight: 800;
            color: #0f172a;
            margin-top: 6px;
        }
        .metric-card .caption {
            margin-top: 8px;
            color: #475569;
            line-height: 1.45;
        }
        .metric-icon {
            width: 42px;
            height: 42px;
            border-radius: 14px;
            display: inline-flex;
            align-items: center;
            justify-content: center;
            font-size: 1.15rem;
            margin-bottom: 10px;
        }
        .section-card {
            background: rgba(255,255,255,0.92);
            border: 1px solid rgba(15, 23, 42, 0.06);
            border-radius: 20px;
            padding: 16px 18px;
            box-shadow: 0 10px 24px rgba(15, 23, 42, 0.06);
            margin-bottom: 16px;
        }
        .section-card h3, .section-card h4 {
            margin-top: 0;
            color: #0f172a;
        }
        .stButton > button {
            border-radius: 999px;
            padding: 0.55rem 1rem;
            border: 0;
            background: linear-gradient(135deg, #0ea5a4, #2563eb);
            color: white;
            font-weight: 700;
            box-shadow: 0 10px 24px rgba(14, 165, 164, 0.16);
        }
        .stButton > button:hover {
            transform: translateY(-1px);
        }
        .stTextInput > div > div > input, .stNumberInput > div > div > input {
            border-radius: 12px;
            border: 1px solid #cbd5e1;
        }
        .stProgress > div > div > div > div {
            background: linear-gradient(90deg, #0ea5a4, #2563eb);
        }
        </style>
        """,
        unsafe_allow_html=True,
    )


def hero_banner(title, subtitle, badge="WaterBuddy Premium"):
    st.markdown(
        f"""
        <div class="hero-card">
            <div class="pill">{badge}</div>
            <h1>{title}</h1>
            <p>{subtitle}</p>
        </div>
        """,
        unsafe_allow_html=True,
    )


def metric_card(title, value, caption="", icon="💧", accent="#0ea5a4"):
    st.markdown(
        f"""
        <div class="metric-card">
            <div class="metric-icon" style="background:{accent}16;color:{accent};">{icon}</div>
            <div class="label">{title}</div>
            <div class="value">{value}</div>
            <div class="caption">{caption}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def section_card(title, body, icon="✨"):
    st.markdown(
        f"""
        <div class="section-card">
            <h3>{icon} {title}</h3>
            <div>{body}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )
