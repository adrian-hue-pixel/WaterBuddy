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
    "star": (
        '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">'
        '<path d="m12 3 2.8 5.7 6.2.9-4.5 4.4 1.1 6.2-5.6-2.9-5.6 2.9 1.1-6.2L3 9.6l6.2-.9L12 3z"/></svg>'
    ),
    "leaf": (
        '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">'
        '<path d="M20.5 3.5C11 3.5 5 6.5 5 13c0 4 3 6.5 6.5 6.5C18 19.5 20.5 12 20.5 3.5z"/>'
        '<path d="M4 21c3-5 6-8 12-11"/></svg>'
    ),
    "wave": (
        '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">'
        '<path d="M2 12c2.5-4 5-4 7.5 0s5 4 7.5 0 5-4 7 0"/></svg>'
    ),
    "medal": (
        '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">'
        '<circle cx="12" cy="14" r="5"/><path d="M9 9 7 3l5 3 5-3-2 6"/></svg>'
    ),
    "shield": (
        '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">'
        '<path d="M12 3 20 6v5c0 5-3.3 8.5-8 10-4.7-1.5-8-5-8-10V6l8-3z"/></svg>'
    ),
    "crown": (
        '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">'
        '<path d="m3 7 4 4 5-7 5 7 4-4-2 12H5L3 7z"/><path d="M5 19h14"/></svg>'
    ),
    "sun": (
        '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">'
        '<circle cx="12" cy="12" r="4"/><path d="M12 2v2M12 20v2M2 12h2M20 12h2M4.9 4.9l1.4 1.4M17.7 17.7l1.4 1.4M19.1 4.9l-1.4 1.4M6.3 17.7l-1.4 1.4"/></svg>'
    ),
    "moon": (
        '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">'
        '<path d="M20 15.5A8.5 8.5 0 0 1 8.5 4 8.5 8.5 0 1 0 20 15.5z"/></svg>'
    ),
    "rocket": (
        '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">'
        '<path d="M14 4c3-1 5-1 6-1 0 1 0 3-1 6l-6 6-4-4 5-7z"/><path d="m9 15-3 3"/><path d="m6 12-3 1 3 3"/><circle cx="15.5" cy="7.5" r="1"/></svg>'
    ),
    "calendar": (
        '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">'
        '<rect x="3" y="5" width="18" height="16" rx="2"/><path d="M7 3v4M17 3v4M3 10h18"/></svg>'
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


def render_badge(title: str, detail: str, icon: str = "sparkle", locked: bool = False) -> None:
    icon_svg = _icon_html(icon)
    state_class = " is-locked" if locked else " is-unlocked"
    status_text = "Locked" if locked else "Unlocked"

    st.markdown(
        f"""
        <div class="badge-card{state_class}">
            <div class="badge-icon">
                {icon_svg}
            </div>
            <div class="badge-content">
                <div class="badge-title">{title}</div>
                <div class="badge-detail">{detail}</div>
            </div>
            <div class="badge-status">
                {status_text}
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )
