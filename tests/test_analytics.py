from __future__ import annotations

from services.analytics import summarize_history


def test_summarize_history_for_empty_dataset():
    summary = summarize_history([])
    assert summary == {"days_tracked": 0, "best_day": 0, "most_active_day": "—", "average_daily": 0}


def test_summarize_history_for_daily_totals():
    history = [
        {"intake_date": "2026-08-10", "total_ml": 1500},
        {"intake_date": "2026-08-11", "total_ml": 2200},
        {"intake_date": "2026-08-12", "total_ml": 1900},
    ]
    summary = summarize_history(history)
    assert summary["days_tracked"] == 3
    assert summary["best_day"] == 2200
    assert summary["average_daily"] == 1866.7


def test_summarize_history_handles_missing_values_gracefully():
    history = [
        {"intake_date": "2026-08-10", "total_ml": 0},
        {"intake_date": "2026-08-11", "total_ml": None},
        {"intake_date": "2026-08-12", "total_ml": 999},
    ]
    summary = summarize_history(history)
    assert summary["days_tracked"] == 3
    assert summary["best_day"] == 999
