from __future__ import annotations
from pathlib import Path

from streamlit.testing.v1 import AppTest

from core.navigation import get_navigation_pages


def test_navigation_pages_are_available():
    pages = get_navigation_pages()
    expected = {
        "Dashboard",
        "Analytics",
        "AI Coach",
        "AI Hydration",
        "Voice Assistant",
        "Water Scan",
        "Daily Tasks",
        "Achievements",
        "Profile",
        "Reminder",
        "Settings",
    }
    assert set(pages) == expected


def test_app_starts_without_uncaught_exceptions():
    at = AppTest.from_file("/Users/adrian/Downloads/WATER BUDDY APP/app.py")
    at.run()
    assert not at.exception
