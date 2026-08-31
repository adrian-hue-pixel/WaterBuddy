from __future__ import annotations

from typing import Callable

from pages.analytics import render_analytics_page
from pages.achievements import render_achievements_page
from pages.ai_coach import render_ai_coach_page
from pages.dashboard import render_dashboard_page
from pages.hydration import render_hydration_page
from pages.profile import render_profile_page
from pages.settings import render_settings_page
from pages.voice_assistant import render_voice_assistant_page


PageRenderer = Callable[[], None]


def get_navigation_pages() -> dict[str, PageRenderer]:
    return {
        "Dashboard": render_dashboard_page,
        "Hydration": render_hydration_page,
        "Analytics": render_analytics_page,
        "AI Coach": render_ai_coach_page,
        "Voice Assistant": render_voice_assistant_page,
        "Achievements": render_achievements_page,
        "Profile": render_profile_page,
        "Settings": render_settings_page,
    }
