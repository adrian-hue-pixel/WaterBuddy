from __future__ import annotations

from datetime import datetime, timedelta
import streamlit as st

from components.cards import render_badge, render_hero_banner
from database.manager import get_recent_history
from services.hydration import calculate_progress, get_hydration_records
from services.mascot_service import get_mascot_service


ACHIEVEMENTS = [
    ("first_sip", "First Sip", "Log your first drink.", "drop", "first"),
    ("500ml", "Getting Started", "Reach 500 ml in a day.", "drop", "daily_500"),
    ("1000ml", "Hydration Rookie", "Reach 1,000 ml in a day.", "drop", "daily_1000"),
    ("halfway", "Halfway There", "Reach 50% of your daily goal.", "sparkle", "daily_50"),
    ("75percent", "Hydration Hero", "Reach 75% of your daily goal.", "trophy", "daily_75"),
    ("goal", "Goal Crusher", "Reach 100% of your daily goal.", "trophy", "daily_100"),
    ("125percent", "Overachiever", "Reach 125% of your daily goal.", "star", "daily_125"),

    ("2day", "Two-Day Flow", "Hit your hydration goal 2 days in a row.", "drop", "streak_2"),
    ("3day", "Three-Day Sprout", "Hit your hydration goal 3 days in a row.", "leaf", "streak_3"),
    ("7day", "One Week Strong", "Maintain a 7-day hydration streak.", "trophy", "streak_7"),
    ("14day", "Two Week Flow", "Maintain a 14-day hydration streak.", "wave", "streak_14"),
    ("30day", "30-Day Wave", "Maintain a 30-day hydration streak.", "wave", "streak_30"),
    ("50day", "50-Day Splash", "Maintain a 50-day hydration streak.", "drop", "streak_50"),
    ("75day", "Hydration Veteran", "Maintain a 75-day hydration streak.", "medal", "streak_75"),
    ("100day", "100-Day Legend", "Maintain a 100-day hydration streak.", "trophy", "streak_100"),
    ("150day", "Hydration Dragon", "Maintain a 150-day hydration streak.", "star", "streak_150"),
    ("182day", "Half-Year Hero", "Maintain a 182-day hydration streak.", "medal", "streak_182"),
    ("250day", "Water Warrior", "Maintain a 250-day hydration streak.", "shield", "streak_250"),
    ("365day", "365-Day Water Legend", "Maintain a full 365-day hydration streak.", "crown", "streak_365"),

    ("early_bird", "Early Bird", "Log water before 9 AM.", "sun", "early"),
    ("night_owl", "Night Owl", "Reach your daily goal after 8 PM.", "moon", "night"),
    ("comeback", "Comeback Kid", "Finish your goal after being below 50%.", "rocket", "comeback"),
    ("perfect_week", "Perfect Week", "Hit your goal every day for 7 days.", "calendar", "streak_7"),
    ("perfect_month", "Perfect Month", "Hit your goal every day for 30 days.", "calendar", "streak_30"),
]


def _history() -> list[dict]:
    try:
        return get_recent_history(
            days=365,
            user_id=st.session_state.get("user_id"),
        )
    except Exception:
        return []


def _date_value(item: dict) -> str:
    return str(item.get("intake_date", ""))


def _streak(history: list[dict], goal_ml: int) -> int:
    """Calculate the longest consecutive goal-reaching streak."""
    qualifying = set()

    for item in history:
        try:
            intake = int(item.get("total_ml", 0) or 0)
            date = _date_value(item)
            if date and intake >= goal_ml:
                qualifying.add(date)
        except (TypeError, ValueError):
            continue

    if not qualifying:
        return 0

    dates = sorted(
        datetime.strptime(d, "%Y-%m-%d").date()
        for d in qualifying
    )

    longest = 1
    current = 1

    for previous, current_date in zip(dates, dates[1:]):
        if current_date == previous + timedelta(days=1):
            current += 1
            longest = max(longest, current)
        else:
            current = 1

    return longest


def _achievement_states(history: list[dict], goal_ml: int) -> dict[str, bool]:
    states = {item[0]: False for item in ACHIEVEMENTS}

    if not history:
        return states

    totals = []
    for item in history:
        try:
            totals.append(
                (
                    _date_value(item),
                    int(item.get("total_ml", 0) or 0),
                )
            )
        except (TypeError, ValueError):
            continue

    if not totals:
        return states

    states["first_sip"] = any(value > 0 for _, value in totals)
    states["500ml"] = any(value >= 500 for _, value in totals)
    states["1000ml"] = any(value >= 1000 for _, value in totals)

    # Use the best available daily percentage.
    best_percent = max(
        (
            int(round((value / max(goal_ml, 1)) * 100))
            for _, value in totals
        ),
        default=0,
    )

    states["halfway"] = best_percent >= 50
    states["75percent"] = best_percent >= 75
    states["goal"] = best_percent >= 100
    states["125percent"] = best_percent >= 125

    streak = _streak(history, goal_ml)

    for achievement_id, threshold in (
        ("2day", 2),
        ("3day", 3),
        ("7day", 7),
        ("14day", 14),
        ("30day", 30),
        ("50day", 50),
        ("75day", 75),
        ("100day", 100),
        ("150day", 150),
        ("182day", 182),
        ("250day", 250),
        ("365day", 365),
    ):
        states[achievement_id] = streak >= threshold

    # Time-based achievements use the recorded timestamp when available.
    early = False
    night = False

    for item in history:
        raw = item.get("created_at") or item.get("logged_at") or item.get("timestamp")
        if raw:
            try:
                hour = datetime.fromisoformat(
                    str(raw).replace("Z", "+00:00")
                ).hour
                early |= hour < 9
                night |= hour >= 20
            except (TypeError, ValueError):
                pass

    states["early_bird"] = early
    states["night_owl"] = night
    states["comeback"] = best_percent >= 100

    states["perfect_week"] = streak >= 7
    states["perfect_month"] = streak >= 30

    return states


def _celebrate_new_unlocks(states: dict[str, bool]) -> None:
    previous = st.session_state.setdefault("_unlocked_achievements", set())

    if not isinstance(previous, set):
        previous = set(previous)

    newly_unlocked = [
        achievement
        for achievement in ACHIEVEMENTS
        if states.get(achievement[0], False)
        and achievement[0] not in previous
    ]

    if not newly_unlocked:
        return

    for achievement in newly_unlocked:
        previous.add(achievement[0])

    st.session_state["_unlocked_achievements"] = previous

    # Celebrate the newest achievement.
    newest = newly_unlocked[-1]
    _, title, detail, icon, _ = newest

    st.toast(
        f"🏆 Achievement unlocked: {title}",
        icon="🎉",
    )

    st.session_state["_achievement_popup"] = {
        "title": title,
        "detail": detail,
        "icon": icon,
    }

    try:
        get_mascot_service().trigger_event(
            "achievement_unlocked",
            hydration_percentage=100,
        )
    except Exception:
        pass


def _render_confetti() -> None:
    st.markdown(
        """
        <style>
        .wb-confetti {
            position: fixed;
            inset: 0;
            pointer-events: none;
            z-index: 999999;
            overflow: hidden;
        }

        .wb-confetti span {
            position: absolute;
            top: -20px;
            width: 7px;
            height: 12px;
            border-radius: 2px;
            animation: wb-fall 2.8s linear forwards;
        }

        @keyframes wb-fall {
            0% {
                transform: translateY(0) rotate(0deg);
                opacity: 1;
            }
            100% {
                transform: translateY(105vh) rotate(720deg);
                opacity: 0;
            }
        }
        </style>

        <div class="wb-confetti">
            <span style="left:5%;animation-delay:.0s"></span>
            <span style="left:12%;animation-delay:.2s"></span>
            <span style="left:20%;animation-delay:.4s"></span>
            <span style="left:29%;animation-delay:.1s"></span>
            <span style="left:38%;animation-delay:.5s"></span>
            <span style="left:47%;animation-delay:.15s"></span>
            <span style="left:56%;animation-delay:.35s"></span>
            <span style="left:65%;animation-delay:.05s"></span>
            <span style="left:74%;animation-delay:.45s"></span>
            <span style="left:83%;animation-delay:.25s"></span>
            <span style="left:92%;animation-delay:.55s"></span>
        </div>
        """,
        unsafe_allow_html=True,
    )


def _render_popup() -> None:
    popup = st.session_state.pop("_achievement_popup", None)

    if not popup:
        return

    _render_confetti()

    st.markdown(
        f"""
        <div style="
            position: fixed;
            top: 22px;
            right: 22px;
            z-index: 1000000;
            width: min(360px, calc(100vw - 44px));
            padding: 18px 20px;
            border-radius: 18px;
            background: rgba(15, 35, 52, .96);
            border: 1px solid rgba(100, 220, 255, .45);
            box-shadow: 0 12px 40px rgba(0,0,0,.28);
            color: white;
            animation: wb-pop .35s ease-out;
        ">
            <div style="font-size:30px;margin-bottom:6px;">🏆 🎉</div>
            <div style="font-size:19px;font-weight:800;">{popup["title"]}</div>
            <div style="font-size:14px;margin-top:5px;opacity:.85;">
                {popup["detail"]}
            </div>
        </div>

        <style>
        @keyframes wb-pop {{
            from {{ transform: translateY(-15px) scale(.95); opacity: 0; }}
            to {{ transform: translateY(0) scale(1); opacity: 1; }}
        }}
        </style>
        """,
        unsafe_allow_html=True,
    )


def render_achievements_page() -> None:
    render_hero_banner(
        "Achievements",
        "Small victories add up. Build your hydration streak and unlock milestones.",
        badge="Milestones",
    )

    history = _history()
    goal_ml = int(st.session_state.get("goal_ml", 2500))
    states = _achievement_states(history, goal_ml)
    records = get_hydration_records()

    st.subheader("🏅 Personal records")
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("🔥 Current streak", f"{records['current_streak']} days")
    col2.metric("🏆 Best streak", f"{records['longest_streak']} days")
    col3.metric("💧 Highest day", f"{records['highest_intake_ml']} ml")
    col4.metric("🎯 Consistency", f"{records['consistency_percent']}%")
    st.caption(f"{records['completed_days']} of {records['tracked_days']} tracked days reached your hydration goal.")

    _celebrate_new_unlocks(states)
    _render_popup()

    unlocked_count = sum(states.values())

    st.markdown(
        f"### 🏆 {unlocked_count}/{len(ACHIEVEMENTS)} achievements unlocked"
    )

    for achievement_id, title, detail, icon, _ in ACHIEVEMENTS:
        unlocked = states.get(achievement_id, False)

        render_badge(
            title if unlocked else f"{title} (locked)",
            detail if unlocked else "Keep going to unlock this achievement.",
            icon if unlocked else "lock",
            locked=not unlocked,
        )
