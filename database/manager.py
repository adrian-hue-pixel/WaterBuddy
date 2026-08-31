from __future__ import annotations

import hashlib
import hmac
import json
import secrets
import sqlite3
from pathlib import Path
from typing import Any

from core.config import BASE_DIR

DB_PATH = BASE_DIR / "waterbuddy.db"

__all__ = [
    "initialize_db",
    "create_user",
    "authenticate_user",
    "get_user_by_id",
    "save_profile",
    "load_profile",
    "save_intake",
    "get_today_total",
    "clear_today_intake",
    "get_recent_history",
    "get_connection",
]


def _resolve_db_path(db_path: str | Path | None = None) -> Path:
    return Path(db_path) if db_path is not None else DB_PATH


def get_connection(db_path: str | Path | None = None) -> sqlite3.Connection:
    """Return a scoped SQLite connection for the target database path."""
    target = str(_resolve_db_path(db_path))
    connection = sqlite3.connect(target, check_same_thread=False, timeout=30)
    connection.row_factory = sqlite3.Row
    connection.execute("PRAGMA foreign_keys = ON")
    connection.execute("PRAGMA journal_mode = WAL")
    connection.execute("PRAGMA busy_timeout = 5000")
    return connection


def _table_sql(connection: sqlite3.Connection, table_name: str) -> str | None:
    row = connection.execute(
        "SELECT sql FROM sqlite_master WHERE type = 'table' AND name = ?",
        (table_name,),
    ).fetchone()
    return row[0] if row else None


def _rebuild_table_with_checks(connection: sqlite3.Connection, table_name: str, create_sql: str, columns: str, where_clause: str = "1=1") -> None:
    if "CHECK" in (_table_sql(connection, table_name) or ""):
        return
    tmp_name = f"{table_name}_new"
    savepoint = f"sp_{table_name}"
    try:
        # Use a SAVEPOINT so we can rollback the migration if anything fails.
        connection.execute(f"SAVEPOINT {savepoint}")
        connection.execute(f"DROP TABLE IF EXISTS {tmp_name}")
        connection.execute(create_sql.replace(f"CREATE TABLE IF NOT EXISTS {table_name}", f"CREATE TABLE {tmp_name}"))
        connection.execute(
            f"INSERT INTO {tmp_name} ({columns}) SELECT {columns} FROM {table_name} WHERE {where_clause}"
        )
        connection.execute(f"DROP TABLE {table_name}")
        connection.execute(f"ALTER TABLE {tmp_name} RENAME TO {table_name}")
        connection.execute(f"RELEASE {savepoint}")
        connection.commit()
    except Exception:
        try:
            connection.execute(f"ROLLBACK TO {savepoint}")
            connection.execute(f"RELEASE {savepoint}")
            connection.rollback()
        except Exception:
            # If rollback fails, re-raise the original error to be handled by the caller.
            raise


def _column_exists(connection: sqlite3.Connection, table_name: str, column_name: str) -> bool:
    columns = connection.execute(f"PRAGMA table_info({table_name})").fetchall()
    return any(row[1] == column_name for row in columns)


def _hash_password(password: str, salt: bytes | None = None) -> str:
    salt_bytes = salt or secrets.token_bytes(16)
    digest = hashlib.pbkdf2_hmac("sha256", password.encode("utf-8"), salt_bytes, 100_000)
    return f"pbkdf2_sha256$100000${salt_bytes.hex()}${digest.hex()}"


def _verify_password(password: str, stored_hash: str) -> bool:
    if not stored_hash or "$" not in stored_hash:
        return False
    try:
        algorithm, iterations, salt_hex, digest_hex = stored_hash.split("$", 3)
    except ValueError:
        return False
    if algorithm != "pbkdf2_sha256":
        return False
    expected = hashlib.pbkdf2_hmac(
        "sha256",
        password.encode("utf-8"),
        bytes.fromhex(salt_hex),
        int(iterations),
    )
    return hmac.compare_digest(expected.hex(), digest_hex)


def _ensure_legacy_user(connection: sqlite3.Connection) -> int | None:
    existing = connection.execute("SELECT id FROM users WHERE username = ?", ("legacy_user",)).fetchone()
    if existing:
        return int(existing[0])
    if connection.execute("SELECT COUNT(*) FROM users").fetchone()[0] > 0:
        return None
    legacy_hash = _hash_password("legacy-user-migration")
    cursor = connection.execute(
        "INSERT INTO users (username, email, password_hash) VALUES (?, ?, ?)",
        ("legacy_user", "legacy_user@waterbuddy.local", legacy_hash),
    )
    connection.commit()
    return int(cursor.lastrowid)


def initialize_db(db_path: str | Path | None = None) -> None:
    connection = get_connection(db_path)
    try:
        connection.execute(
            """
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT NOT NULL UNIQUE,
                email TEXT NOT NULL UNIQUE,
                password_hash TEXT NOT NULL,
                created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
            )
            """
        )
        connection.execute(
            """
            CREATE TABLE IF NOT EXISTS profiles (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                profile_name TEXT NOT NULL,
                age_group TEXT NOT NULL,
                goal_ml INTEGER NOT NULL,
                notes TEXT,
                user_id INTEGER
            )
            """
        )
        connection.execute(
            """
            CREATE TABLE IF NOT EXISTS intakes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                intake_date TEXT NOT NULL,
                amount_ml INTEGER NOT NULL,
                source TEXT NOT NULL,
                created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
                user_id INTEGER
            )
            """
        )

        if not _column_exists(connection, "profiles", "user_id"):
            connection.execute("ALTER TABLE profiles ADD COLUMN user_id INTEGER")
        if not _column_exists(connection, "intakes", "user_id"):
            connection.execute("ALTER TABLE intakes ADD COLUMN user_id INTEGER")

        legacy_user_id = _ensure_legacy_user(connection)
        if legacy_user_id is not None:
            connection.execute(
                "UPDATE profiles SET user_id = ? WHERE user_id IS NULL",
                (legacy_user_id,),
            )
            connection.execute(
                "UPDATE intakes SET user_id = ? WHERE user_id IS NULL",
                (legacy_user_id,),
            )

        profiles_sql = _table_sql(connection, "profiles") or ""
        if "CHECK" not in profiles_sql:
            _rebuild_table_with_checks(
                connection,
                "profiles",
                """
                CREATE TABLE profiles_new (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    profile_name TEXT NOT NULL,
                    age_group TEXT NOT NULL,
                    goal_ml INTEGER NOT NULL CHECK (goal_ml > 0 AND goal_ml <= 5000),
                    notes TEXT,
                    user_id INTEGER
                )
                """,
                "id, profile_name, age_group, goal_ml, notes, user_id",
                "goal_ml > 0 AND goal_ml <= 5000",
            )

        intakes_sql = _table_sql(connection, "intakes") or ""
        if "CHECK" not in intakes_sql:
            _rebuild_table_with_checks(
                connection,
                "intakes",
                """
                CREATE TABLE intakes_new (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    intake_date TEXT NOT NULL,
                    amount_ml INTEGER NOT NULL CHECK (amount_ml > 0 AND amount_ml <= 10000),
                    source TEXT NOT NULL,
                    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
                    user_id INTEGER
                )
                """,
                "id, intake_date, amount_ml, source, created_at, user_id",
                "amount_ml > 0 AND amount_ml <= 10000",
            )

        connection.execute("CREATE INDEX IF NOT EXISTS idx_intakes_intake_date ON intakes (intake_date)")
        connection.execute("CREATE INDEX IF NOT EXISTS idx_intakes_created_at ON intakes (created_at)")
        connection.execute("CREATE INDEX IF NOT EXISTS idx_profiles_name ON profiles (profile_name)")
        connection.execute("CREATE INDEX IF NOT EXISTS idx_profiles_user_id ON profiles (user_id)")
        connection.execute("CREATE INDEX IF NOT EXISTS idx_intakes_user_id ON intakes (user_id)")
        connection.execute("CREATE INDEX IF NOT EXISTS idx_users_username ON users (username)")
        connection.execute("CREATE INDEX IF NOT EXISTS idx_users_email ON users (email)")

        connection.commit()
    finally:
        connection.close()


def create_user(username: str, email: str, password: str, db_path: str | Path | None = None) -> dict[str, Any]:
    clean_username = (username or "").strip()
    clean_email = (email or "").strip().lower()
    if not clean_username or not clean_email or not password:
        raise ValueError("Username, email, and password are required.")
    connection = get_connection(db_path)
    try:
        existing = connection.execute(
            "SELECT id FROM users WHERE LOWER(username) = LOWER(?) OR LOWER(email) = LOWER(?)",
            (clean_username, clean_email),
        ).fetchone()
        if existing:
            raise ValueError("An account with that username or email already exists.")
        hashed = _hash_password(password)
        cursor = connection.execute(
            "INSERT INTO users (username, email, password_hash) VALUES (?, ?, ?)",
            (clean_username, clean_email, hashed),
        )
        connection.commit()
        return {"id": int(cursor.lastrowid), "username": clean_username, "email": clean_email}
    finally:
        connection.close()


def authenticate_user(identifier: str, password: str, db_path: str | Path | None = None) -> dict[str, Any] | None:
    clean_identifier = (identifier or "").strip()
    if not clean_identifier or not password:
        return None
    connection = get_connection(db_path)
    try:
        row = connection.execute(
            "SELECT id, username, email, password_hash FROM users WHERE LOWER(username) = LOWER(?) OR LOWER(email) = LOWER(?)",
            (clean_identifier, clean_identifier),
        ).fetchone()
        if row is None:
            return None
        if not _verify_password(password, row["password_hash"]):
            return None
        return {"id": int(row["id"]), "username": row["username"], "email": row["email"]}
    finally:
        connection.close()


def get_user_by_id(user_id: int, db_path: str | Path | None = None) -> dict[str, Any] | None:
    connection = get_connection(db_path)
    try:
        row = connection.execute(
            "SELECT id, username, email FROM users WHERE id = ?",
            (user_id,),
        ).fetchone()
        if row is None:
            return None
        return {"id": int(row["id"]), "username": row["username"], "email": row["email"]}
    finally:
        connection.close()


def save_profile(profile_name: str, age_group: str, goal_ml: int, notes: str = "", db_path: str | Path | None = None, user_id: int | None = None) -> None:
    connection = get_connection(db_path)
    try:
        if user_id is not None:
            existing = connection.execute("SELECT id FROM profiles WHERE user_id = ?", (user_id,)).fetchone()
            if existing:
                connection.execute(
                    "UPDATE profiles SET profile_name = ?, age_group = ?, goal_ml = ?, notes = ? WHERE user_id = ?",
                    (profile_name, age_group, goal_ml, notes, user_id),
                )
            else:
                connection.execute(
                    "INSERT INTO profiles (profile_name, age_group, goal_ml, notes, user_id) VALUES (?, ?, ?, ?, ?)",
                    (profile_name, age_group, goal_ml, notes, user_id),
                )
        else:
            connection.execute("DELETE FROM profiles")
            connection.execute(
                "INSERT INTO profiles (profile_name, age_group, goal_ml, notes) VALUES (?, ?, ?, ?)",
                (profile_name, age_group, goal_ml, notes),
            )
        connection.commit()
    finally:
        connection.close()


def load_profile(db_path: str | Path | None = None, user_id: int | None = None) -> dict[str, Any] | None:
    connection = get_connection(db_path)
    try:
        if user_id is not None:
            row = connection.execute(
                "SELECT profile_name, age_group, goal_ml, notes FROM profiles WHERE user_id = ? ORDER BY id DESC LIMIT 1",
                (user_id,),
            ).fetchone()
        else:
            row = connection.execute(
                "SELECT profile_name, age_group, goal_ml, notes FROM profiles ORDER BY id DESC LIMIT 1"
            ).fetchone()
        if row is None:
            return None
        return {
            "name": row[0],
            "age_group": row[1],
            "goal_ml": row[2],
            "notes": row[3],
        }
    finally:
        connection.close()


def save_intake(intake_date: str, amount_ml: int, source: str, db_path: str | Path | None = None, user_id: int | None = None) -> None:
    connection = get_connection(db_path)
    try:
        if user_id is not None:
            connection.execute(
                "INSERT INTO intakes (intake_date, amount_ml, source, user_id) VALUES (?, ?, ?, ?)",
                (intake_date, amount_ml, source, user_id),
            )
        else:
            connection.execute(
                "INSERT INTO intakes (intake_date, amount_ml, source) VALUES (?, ?, ?)",
                (intake_date, amount_ml, source),
            )
        connection.commit()
    finally:
        connection.close()


def get_today_total(intake_date: str, db_path: str | Path | None = None, user_id: int | None = None) -> int:
    connection = get_connection(db_path)
    try:
        if user_id is not None:
            total = connection.execute(
                "SELECT COALESCE(SUM(amount_ml), 0) FROM intakes WHERE intake_date = ? AND user_id = ?",
                (intake_date, user_id),
            ).fetchone()[0]
        else:
            total = connection.execute(
                "SELECT COALESCE(SUM(amount_ml), 0) FROM intakes WHERE intake_date = ?",
                (intake_date,),
            ).fetchone()[0]
        return int(total or 0)
    finally:
        connection.close()


def clear_today_intake(intake_date: str, db_path: str | Path | None = None, user_id: int | None = None) -> None:
    connection = get_connection(db_path)
    try:
        if user_id is not None:
            connection.execute("DELETE FROM intakes WHERE intake_date = ? AND user_id = ?", (intake_date, user_id))
        else:
            connection.execute("DELETE FROM intakes WHERE intake_date = ?", (intake_date,))
        connection.commit()
    finally:
        connection.close()


def get_recent_history(days: int = 7, db_path: str | Path | None = None, user_id: int | None = None) -> list[dict[str, Any]]:
    connection = get_connection(db_path)
    try:
        if user_id is not None:
            rows = connection.execute(
                """
                SELECT intake_date, SUM(amount_ml) AS total_ml
                FROM intakes
                WHERE user_id = ?
                GROUP BY intake_date
                ORDER BY intake_date DESC
                LIMIT ?
                """,
                (user_id, days),
            ).fetchall()
        else:
            rows = connection.execute(
                """
                SELECT intake_date, SUM(amount_ml) AS total_ml
                FROM intakes
                GROUP BY intake_date
                ORDER BY intake_date DESC
                LIMIT ?
                """,
                (days,),
            ).fetchall()
        return [dict(row) for row in rows]
    finally:
        connection.close()



# Simple remembered-user persistence for development: store last authenticated user ID
_LAST_USER_FILE = Path(BASE_DIR) / ".last_user"


def set_remembered_user(user_id: int | None) -> None:
    """Remember the last authenticated user ID (development convenience)."""
    try:
        if user_id is None:
            if _LAST_USER_FILE.exists():
                _LAST_USER_FILE.unlink()
        else:
            _LAST_USER_FILE.write_text(str(int(user_id)), encoding="utf-8")
    except Exception:
        # Best-effort; do not let persistence failures block auth flows
        pass


def get_remembered_user() -> int | None:
    try:
        if _LAST_USER_FILE.exists():
            content = _LAST_USER_FILE.read_text(encoding="utf-8").strip()
            if content:
                return int(content)
    except Exception:
        return None
    return None



# Theme persistence (development convenience) — store the selected theme and dark mode.
_THEME_PREF_FILE = Path(BASE_DIR) / ".theme_pref"


def _read_theme_pref() -> dict[str, Any]:
    try:
        if not _THEME_PREF_FILE.exists():
            return {}
        content = _THEME_PREF_FILE.read_text(encoding="utf-8").strip()
        if not content:
            return {}
        if content.startswith("{"):
            loaded = json.loads(content)
            return loaded if isinstance(loaded, dict) else {}
        legacy_value = content.strip().lower()
        if legacy_value in {"1", "0"}:
            return {"dark_mode": legacy_value == "1"}
    except Exception:
        return {}
    return {}


def set_persisted_theme(theme: str | None = None, dark: bool | None = None) -> None:
    """Persist the current theme preference to a tiny JSON file.

    Passing None clears the matching preference.
    """
    try:
        pref = _read_theme_pref()
        if theme is not None:
            pref["theme"] = str(theme).lower()
        if dark is not None:
            pref["dark_mode"] = bool(dark)
        if not pref:
            if _THEME_PREF_FILE.exists():
                _THEME_PREF_FILE.unlink()
            return
        _THEME_PREF_FILE.write_text(json.dumps(pref), encoding="utf-8")
    except Exception:
        pass


def get_persisted_theme() -> dict[str, Any] | bool | None:
    pref = _read_theme_pref()
    if not pref:
        return None
    if "dark_mode" in pref and "theme" not in pref:
        return bool(pref.get("dark_mode"))
    return pref


get_connection.clear = lambda: None
