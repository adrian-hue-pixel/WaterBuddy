from __future__ import annotations

import sqlite3

import pytest
import streamlit as st

from database import manager as db_manager


@pytest.fixture
def isolated_db(tmp_path, monkeypatch):
    db_path = tmp_path / "waterbuddy-test.db"
    monkeypatch.setattr(db_manager, "DB_PATH", db_path)
    if hasattr(db_manager.get_connection, "clear"):
        db_manager.get_connection.clear()
    db_manager.initialize_db()
    yield db_path
    if hasattr(db_manager.get_connection, "clear"):
        db_manager.get_connection.clear()
    if db_path.exists():
        db_path.unlink()


@pytest.fixture
def clear_session_state():
    for key in list(st.session_state.keys()):
        del st.session_state[key]
    yield st.session_state
    for key in list(st.session_state.keys()):
        del st.session_state[key]


@pytest.fixture
def temp_db_connection(isolated_db):
    connection = sqlite3.connect(isolated_db)
    connection.row_factory = sqlite3.Row
    yield connection
    connection.close()
