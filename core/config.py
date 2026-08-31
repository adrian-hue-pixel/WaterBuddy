from __future__ import annotations

import os
from pathlib import Path

from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parents[1]
ENV_PATH = BASE_DIR / ".env"
load_dotenv(ENV_PATH)


def get_setting(key: str, default: str | None = None) -> str | None:
    value = os.getenv(key, default)
    return value if value not in (None, "") else default
