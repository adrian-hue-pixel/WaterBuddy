from __future__ import annotations

from dataclasses import dataclass


@dataclass
class UserProfile:
    name: str = ""
    age_group: str = "19–50"
    goal_ml: int = 2500
    notes: str = ""
