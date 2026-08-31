from __future__ import annotations

import streamlit as st

ICON_SVG: dict[str, str] = {
    "drop": (
        '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" '
        'stroke-linejoin="round" aria-hidden="true"><path d="M12 2.5c-3.3 4.6-6 7.9-6 11.5a6 6 0 0012 0c0-3.6-2.7-7-6-11.5z"/></svg>'
    ),
    "sparkle": (
        '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" '
        'stroke-linejoin="round" aria-hidden="true"><path d="M12 3l1.5 3.5 3.5 1.5-3.5 1.5L12 15l-1.5-3.5-3.5-1.5 3.5-1.5L12 3z"/><path d="M5 13.5L6.5 16 9 17l-2.5 1.5L5 21l-1.5-2.5L1 17l2.5-1.5L5 13.5z"/></svg>'
    ),
    "trophy": (
        '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" '
        'stroke-linejoin="round" aria-hidden="true"><path d="M8 5V3h8v2"/><path d="M6 8h12a2 2 0 012 2v3a5 5 0 01-5 5h-4a5 5 0 01-5-5V10a2 2 0 012-2z"/><path d="M9 21h6"/></svg>'
    ),
    "lock": (
        '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" '
        'stroke-linejoin="round" aria-hidden="true"><rect x="5" y="11" width="14" height="10" rx="2"/><path d="M8 11V7a4 4 0 018 0v4"/></svg>'
    ),
}


def _icon_html(name: str) -> str:
    return ICON_SVG.get(name, name)


def render_hero_banner(title: str, subtitle: str, badge: str = "Live Dashboard") -> None:
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


def render_stat_card(title: str, value: str, accent: str = "primary", icon: str = "drop") -> None:
    st.markdown(
        f"""
        <div class="stat-card accent-{accent}">
            <div class="stat-card__icon">{_icon_html(icon)}</div>
            <div class="label">{title}</div>
            <div class="value">{value}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_badge(title: str, detail: str, icon: str = "sparkle") -> None:
    st.markdown(
        f"""
        <div class="badge-card">
            <div class="badge-icon">{_icon_html(icon)}</div>
            <div>
                <div class="badge-title">{title}</div>
                <div class="badge-detail">{detail}</div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )
