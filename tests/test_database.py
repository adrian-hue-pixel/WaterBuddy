from __future__ import annotations

import sqlite3

from database import manager as db_manager


def test_database_initialization_creates_expected_tables(isolated_db):
    db_manager.initialize_db()
    with sqlite3.connect(isolated_db) as connection:
        tables = {
            row[0]
            for row in connection.execute(
                "SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%'"
            )
        }
    assert {"profiles", "intakes"}.issubset(tables)


def test_database_profile_round_trip(isolated_db):
    db_manager.save_profile("Ava", "19–50", 2500, "Morning focus")
    profile = db_manager.load_profile()
    assert profile is not None
    assert profile["name"] == "Ava"
    assert profile["age_group"] == "19–50"
    assert profile["goal_ml"] == 2500
    assert profile["notes"] == "Morning focus"


def test_database_hydration_log_round_trip(isolated_db):
    db_manager.save_intake("2026-08-14", 250, "quick")
    db_manager.save_intake("2026-08-14", 500, "custom")
    total = db_manager.get_today_total("2026-08-14")
    history = db_manager.get_recent_history(7)
    assert total == 750
    assert any(item["intake_date"] == "2026-08-14" and item["total_ml"] == 750 for item in history)


def test_database_achievement_and_memory_accounts_are_stored_when_available(isolated_db):
    conn = sqlite3.connect(isolated_db)
    conn.execute(
        "CREATE TABLE IF NOT EXISTS achievements (id INTEGER PRIMARY KEY AUTOINCREMENT, user_name TEXT, title TEXT, unlocked_at TEXT)"
    )
    conn.execute(
        "CREATE TABLE IF NOT EXISTS memories (id INTEGER PRIMARY KEY AUTOINCREMENT, user_name TEXT, content TEXT, created_at TEXT)"
    )
    conn.execute(
        "INSERT INTO achievements (user_name, title, unlocked_at) VALUES (?, ?, ?)",
        ("Ava", "First sip", "2026-08-14T09:00:00"),
    )
    conn.execute(
        "INSERT INTO memories (user_name, content, created_at) VALUES (?, ?, ?)",
        ("Ava", "Drank water before noon.", "2026-08-14T09:10:00"),
    )
    conn.commit()
    achievement = conn.execute("SELECT title FROM achievements WHERE user_name = ?", ("Ava",)).fetchone()
    memory = conn.execute("SELECT content FROM memories WHERE user_name = ?", ("Ava",)).fetchone()
    assert achievement is not None and achievement[0] == "First sip"
    assert memory is not None and memory[0] == "Drank water before noon."
    conn.close()


def test_database_data_isolation_between_database_paths(tmp_path, monkeypatch):
    first = tmp_path / "user_a.db"
    second = tmp_path / "user_b.db"
    monkeypatch.setattr(db_manager, "DB_PATH", first)
    db_manager.get_connection.clear()
    db_manager.initialize_db()
    db_manager.save_intake("2026-08-14", 250, "quick")

    monkeypatch.setattr(db_manager, "DB_PATH", second)
    db_manager.get_connection.clear()
    db_manager.initialize_db()
    db_manager.save_intake("2026-08-14", 500, "quick")

    assert db_manager.get_today_total("2026-08-14") == 500

    monkeypatch.setattr(db_manager, "DB_PATH", first)
    db_manager.get_connection.clear()
    assert db_manager.get_today_total("2026-08-14") == 250
