from __future__ import annotations

from models.mascot_models import MascotState
from services.mascot_service import MascotService


def test_mascot_state_machine_transitions():
    service = MascotService()
    transitions = {
        "water_logged": MascotState.DRINKING,
        "goal_reached": MascotState.ACHIEVEMENT,
        "ai_thinking": MascotState.THINKING,
        "ai_speaking": MascotState.SPEAKING,
        "voice_listening": MascotState.LISTENING,
        "achievement_unlocked": MascotState.ACHIEVEMENT,
        "weather_warning": MascotState.WARNING,
    }
    for event, expected in transitions.items():
        service.trigger_event(event)
        assert service.get_state() == expected


def test_mascot_ignores_unknown_events_without_crashing():
    service = MascotService()
    service.trigger_event("totally_unknown_event")
    assert service.get_state() in set(MascotState)


def test_mascot_messages_are_stored():
    service = MascotService()
    service.show_message("Hydration reminder", context="ui")
    message = service.get_message()
    assert message is not None
    assert message.text == "Hydration reminder"
    assert message.context == "ui"
