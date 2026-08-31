from __future__ import annotations

from enum import Enum
from dataclasses import dataclass
from typing import Any


class MascotState(str, Enum):
    IDLE = "idle"
    HAPPY = "happy"
    THINKING = "thinking"
    DRINKING = "drinking"
    EXCITED = "excited"
    SLEEPING = "sleeping"
    WARNING = "warning"
    SAD = "sad"
    LISTENING = "listening"
    SPEAKING = "speaking"
    ACHIEVEMENT = "achievement"


@dataclass
class MascotMessage:
    text: str
    context: str | None = None
    metadata: dict[str, Any] | None = None
