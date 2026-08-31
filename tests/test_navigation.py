from __future__ import annotations

from streamlit.testing.v1 import AppTest

from core.navigation import get_navigation_pages


def test_navigation_pages_are_available():
    pages = get_navigation_pages()
    expected = {"Dashboard", "Hydration", "Analytics", "AI Coach", "Voice Assistant", "Achievements", "Profile", "Settings"}
    assert set(pages) == expected


def test_app_starts_without_uncaught_exceptions():
    at = AppTest.from_file("/Users/adrian/Downloads/WATER BUDDY APP/app.py")
    at.run()
    assert not at.exception
