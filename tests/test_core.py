from datetime import date

import pytest

from habits import core

TODAY = date(2026, 10, 14)


def _state_with(name: str = "Leer") -> dict:
    return core.add_habit(
        {"version": 1, "habits": []}, name, created_on=date(2026, 10, 10)
    )


def test_normalize_name_trims_and_casefolds():
    assert core.normalize_name("  Leer ") == "leer"


def test_add_habit_creates_habit():
    state = {"version": 1, "habits": []}
    new_state = core.add_habit(state, "Leer", created_on=TODAY)
    assert new_state["habits"] == [
        {"name": "Leer", "created_on": "2026-10-14", "completed_on": []}
    ]
    assert state["habits"] == []


def test_add_habit_rejects_duplicate_ignoring_case_and_spaces():
    state = core.add_habit({"version": 1, "habits": []}, "Leer", created_on=TODAY)
    with pytest.raises(core.DuplicateHabitError):
        core.add_habit(state, "  leer ", created_on=TODAY)


def test_add_habit_rejects_empty_name():
    with pytest.raises(core.InvalidNameError):
        core.add_habit({"version": 1, "habits": []}, "   ", created_on=TODAY)


def test_mark_done_adds_today():
    new_state, added = core.mark_done(_state_with(), "Leer", today=TODAY)
    assert added is True
    assert new_state["habits"][0]["completed_on"] == ["2026-10-14"]


def test_mark_done_is_idempotent_same_day():
    state, _ = core.mark_done(_state_with(), "Leer", today=TODAY)
    same_state, added = core.mark_done(state, "  leer ", today=TODAY)
    assert added is False
    assert same_state["habits"][0]["completed_on"] == ["2026-10-14"]


def test_mark_done_missing_habit_raises():
    with pytest.raises(core.HabitNotFoundError):
        core.mark_done(_state_with(), "Correr", today=TODAY)


def test_current_streak_empty_is_zero():
    assert core.current_streak([], today=TODAY) == 0


def test_current_streak_single_day_today():
    assert core.current_streak(["2026-10-14"], today=TODAY) == 1


def test_current_streak_alive_when_last_is_yesterday():
    assert core.current_streak(["2026-10-12", "2026-10-13"], today=TODAY) == 2


def test_current_streak_broken_when_gap_too_big():
    assert core.current_streak(["2026-10-11", "2026-10-12"], today=TODAY) == 0


def test_current_streak_long_and_ignores_duplicates():
    dates = [
        "2026-10-10",
        "2026-10-11",
        "2026-10-11",
        "2026-10-12",
        "2026-10-13",
        "2026-10-14",
    ]
    assert core.current_streak(dates, today=TODAY) == 5


def test_current_streak_today_and_anteayer_without_yesterday():
    assert core.current_streak(["2026-10-12", "2026-10-14"], today=TODAY) == 1


def test_list_habits_sorted_by_streak_then_name():
    state = {
        "version": 1,
        "habits": [
            {
                "name": "Zeta",
                "created_on": "2026-10-10",
                "completed_on": ["2026-10-14"],
            },
            {
                "name": "Alfa",
                "created_on": "2026-10-10",
                "completed_on": ["2026-10-14"],
            },
            {"name": "Beta", "created_on": "2026-10-10", "completed_on": []},
        ],
    }
    result = core.list_habits(state, today=TODAY)
    assert [item["name"] for item in result] == ["Alfa", "Zeta", "Beta"]
    assert [item["streak"] for item in result] == [1, 1, 0]


def test_list_habits_empty():
    assert core.list_habits({"version": 1, "habits": []}, today=TODAY) == []
