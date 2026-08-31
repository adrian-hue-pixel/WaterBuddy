from __future__ import annotations

import streamlit as st
from typing import Optional
from models.mascot_models import MascotState, MascotMessage
from datetime import datetime, timezone


class MascotService:
    """Service to manage the mascot state machine and messages.

    It stores minimal state in st.session_state and provides methods to
    trigger events from other services without embedding UI logic.
    """

    SESSION_KEY = "_mascot_state"
    MESSAGE_KEY = "_mascot_message"
    LAST_EVENT_KEY = "_mascot_last_event_at"

    def __init__(self) -> None:
        if self.SESSION_KEY not in st.session_state:
            st.session_state[self.SESSION_KEY] = MascotState.IDLE.value
        if self.MESSAGE_KEY not in st.session_state:
            st.session_state[self.MESSAGE_KEY] = None

    def get_state(self) -> MascotState:
        return MascotState(st.session_state.get(self.SESSION_KEY, MascotState.IDLE.value))

    def set_state(self, state: MascotState) -> None:
        st.session_state[self.SESSION_KEY] = state.value
        st.session_state[self.LAST_EVENT_KEY] = datetime.now(timezone.utc).isoformat()

    def trigger_event(self, event: str, *, hydration_percentage: Optional[int] = None, user_name: Optional[str] = None) -> None:
        """Map high-level events to mascot states.

        Recognized events (examples):
        - water_logged
        - goal_reached
        - ai_thinking
        - ai_speaking
        - voice_listening
        - achievement_unlocked
        - weather_warning
        """
        # Simple mapping; keep deterministic and fast
        if event == "water_logged":
            self.set_state(MascotState.DRINKING)
            # short-lived reaction; schedule idle on next rerun
            st.session_state.setdefault("_mascot_temp_timer", 1)
        elif event == "goal_reached" or event == "achievement_unlocked":
            self.set_state(MascotState.ACHIEVEMENT)
        elif event == "ai_thinking":
            self.set_state(MascotState.THINKING)
        elif event == "ai_speaking":
            self.set_state(MascotState.SPEAKING)
        elif event == "voice_listening":
            self.set_state(MascotState.LISTENING)
        elif event == "missed_goal" or event == "weather_warning":
            self.set_state(MascotState.WARNING)
        elif event == "sleep_mode":
            self.set_state(MascotState.SLEEPING)
        else:
            # fallback to hydration-driven state or idle
            if hydration_percentage is not None:
                if hydration_percentage >= 100:
                    self.set_state(MascotState.ACHIEVEMENT)
                elif hydration_percentage >= 80:
                    self.set_state(MascotState.EXCITED)
                elif hydration_percentage >= 50:
                    self.set_state(MascotState.HAPPY)
                elif hydration_percentage >= 20:
                    self.set_state(MascotState.HAPPY)
                else:
                    self.set_state(MascotState.IDLE)
            else:
                self.set_state(MascotState.IDLE)

    def show_message(self, text: str, *, context: Optional[str] = None, metadata: Optional[dict] = None) -> None:
        st.session_state[self.MESSAGE_KEY] = MascotMessage(text=text, context=context, metadata=metadata)

    def get_message(self) -> Optional[MascotMessage]:
        return st.session_state.get(self.MESSAGE_KEY)


def get_mascot_service() -> MascotService:
    # Use streamlit cache_resource to provide a singleton per session
    if "_mascot_service" not in st.session_state:
        st.session_state["_mascot_service"] = MascotService()
    return st.session_state["_mascot_service"]
