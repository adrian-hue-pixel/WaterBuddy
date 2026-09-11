from __future__ import annotations

from datetime import date, datetime, timedelta

import pytest

from database import manager as db_manager
from services import hydration as hydration_service
from services.hydration import calculate_progress, get_age_goal, get_milestone_message, get_streak, reset_daily_intake, update_daily_intake


@pytest.mark.parametrize(
    "intake, goal, expected",
    [
        (500, 2500, (20, 2000, False)),
        (2500, 2500, (100, 0, True)),
        (3000, 2500, (100, 0, True)),
        (0, 2500, (0, 2500, False)),
    ],
)
def test_calculate_progress_for_valid_inputs(intake, goal, expected):
    assert calculate_progress(intake, goal) == expected


def test_calculate_progress_handles_invalid_amounts_without_crashing():
    assert calculate_progress(-200, 2000) == (0, 2000, False)
    assert calculate_progress(0, 0) == (0, 1, False)
    assert calculate_progress(-50, -50) == (0, 1, False)


def test_update_daily_intake_and_goal_sync(isolated_db):
    today = date.today().strftime("%Y-%m-%d")
    db_manager.save_intake(today, 250, "quick")
    assert db_manager.get_today_total(today) == 250
    total, goal = update_daily_intake(500, "custom")
    assert total == 750
    assert goal == get_age_goal("19–50")


def test_daily_goal_and_milestone_messages_are_sensible():
    msg, emoji = get_milestone_message(25)
    assert "strong start" in msg.lower()
    assert emoji
    assert get_age_goal("65+") == 2000


def test_reset_daily_intake_clears_today_history(clear_session_state, isolated_db):
    clear_session_state["goal_ml"] = 2500
    today = date.today().strftime("%Y-%m-%d")
    db_manager.save_intake(today, 250, "quick")
    total, goal = reset_daily_intake()
    assert total == 0
    assert goal == 2500
    assert db_manager.get_today_total(today) == 0


def test_get_streak_counts_recent_days(clear_session_state, isolated_db):
    clear_session_state["goal_ml"] = 2500
    today = date.today()
    for offset in range(3):
        day = (today - timedelta(days=offset)).strftime("%Y-%m-%d")
        db_manager.save_intake(day, 250, "quick")
    assert get_streak(7) >= 1


def test_hydration_prediction_uses_hours_as_hours(clear_session_state, isolated_db, monkeypatch):
    class FixedDateTime(datetime):
        @classmethod
        def now(cls, tz=None):
            return cls(
                date.today().year,
                date.today().month,
                date.today().day,
                9,
                30,
            )

    clear_session_state["goal_ml"] = 2500
    monkeypatch.setattr(hydration_service, "datetime", FixedDateTime)

    today = date.today().strftime("%Y-%m-%d")
    db_manager.save_intake(today, 1200, "quick")

    prediction = hydration_service.get_hydration_prediction()

    assert prediction["pace_ml_per_hour"] == 480
    assert prediction["projected_intake_ml"] == 7680


def test_hydration_prediction_does_not_project_past_day_end(clear_session_state, isolated_db, monkeypatch):
    class FixedDateTime(datetime):
        @classmethod
        def now(cls, tz=None):
            return cls(
                date.today().year,
                date.today().month,
                date.today().day,
                23,
                30,
            )

    clear_session_state["goal_ml"] = 2500
    monkeypatch.setattr(hydration_service, "datetime", FixedDateTime)

    today = date.today().strftime("%Y-%m-%d")
    db_manager.save_intake(today, 3000, "quick")

    prediction = hydration_service.get_hydration_prediction()

    assert prediction["projected_intake_ml"] == 3000


def test_get_streak_respects_requested_window(clear_session_state, isolated_db):
    clear_session_state["goal_ml"] = 2500
    today = date.today()
    for offset in range(10):
        day = (today - timedelta(days=offset)).strftime("%Y-%m-%d")
        db_manager.save_intake(day, 250, "quick")

    assert get_streak(7) == 7


def test_hydration_data_isolation_across_users(tmp_path, monkeypatch):
    a = tmp_path / "user_a.db"
    b = tmp_path / "user_b.db"
    today = date.today().strftime("%Y-%m-%d")

    monkeypatch.setattr(db_manager, "DB_PATH", a)
    db_manager.get_connection.clear()
    db_manager.initialize_db()
    db_manager.save_intake(today, 250, "quick")

    monkeypatch.setattr(db_manager, "DB_PATH", b)
    db_manager.get_connection.clear()
    db_manager.initialize_db()
    db_manager.save_intake(today, 500, "quick")

    assert db_manager.get_today_total(today) == 500

    monkeypatch.setattr(db_manager, "DB_PATH", a)
    db_manager.get_connection.clear()
    assert db_manager.get_today_total(today) == 250
