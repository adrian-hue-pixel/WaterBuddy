from __future__ import annotations

from collections import Counter
from datetime import datetime
from typing import Any


def summarize_history(history: list[dict[str, Any]]) -> dict[str, Any]:
    if not history:
        return {"days_tracked": 0, "best_day": 0, "most_active_day": "—", "average_daily": 0}

    totals: list[int] = []
    day_names: list[str] = []
    for item in history:
        raw_total = item.get("total_ml")
        totals.append(int(raw_total) if raw_total is not None and raw_total != "" else 0)
        raw_date = item.get("intake_date", "1970-01-01")
        try:
            day_names.append(datetime.strptime(str(raw_date), "%Y-%m-%d").strftime("%a"))
        except (TypeError, ValueError):
            day_names.append("—")

    counts = Counter(day_names)
    counts.pop("—", None)
    most_active_day = counts.most_common(1)[0][0] if counts else "—"
    return {
        "days_tracked": len(history),
        "best_day": max(totals, default=0),
        "most_active_day": most_active_day,
        "average_daily": round(sum(totals) / len(totals), 1) if totals else 0,
    }
