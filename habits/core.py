from __future__ import annotations

from datetime import date, timedelta

VERSION = 1


class HabitError(Exception):
    """Error de negocio al manipular hábitos."""


class InvalidNameError(HabitError):
    """El nombre del hábito no es válido."""


class DuplicateHabitError(HabitError):
    """Ya existe un hábito con ese nombre."""


class HabitNotFoundError(HabitError):
    """No existe un hábito con ese nombre."""


def normalize_name(name: str) -> str:
    return name.strip().casefold()


def add_habit(state: dict, name: str, *, created_on: date) -> dict:
    clean = name.strip()
    if not clean:
        raise InvalidNameError("El nombre no puede estar vacío. Ejemplo: habits add Leer")

    key = normalize_name(name)
    for habit in state["habits"]:
        if normalize_name(habit["name"]) == key:
            raise DuplicateHabitError(
                f"El hábito '{clean}' ya existe. Usa 'habits list' para verlos."
            )

    new_habit = {
        "name": clean,
        "created_on": created_on.isoformat(),
        "completed_on": [],
    }
    new_state = dict(state)
    new_state["habits"] = [*state["habits"], new_habit]
    return new_state


def _find_habit(state: dict, name: str) -> tuple[int, dict]:
    key = normalize_name(name)
    for index, habit in enumerate(state["habits"]):
        if normalize_name(habit["name"]) == key:
            return index, habit
    raise HabitNotFoundError(
        f"No existe el hábito '{name.strip()}'. Usa 'habits list' para verlos."
    )


def mark_done(state: dict, name: str, *, today: date) -> tuple[dict, bool]:
    index, habit = _find_habit(state, name)
    stamp = today.isoformat()
    if stamp in habit["completed_on"]:
        return state, False

    new_habit = {**habit, "completed_on": [*habit["completed_on"], stamp]}
    new_state = dict(state)
    new_state["habits"] = [
        new_habit if position == index else entry
        for position, entry in enumerate(state["habits"])
    ]
    return new_state, True


def current_streak(completed_on: list[str], *, today: date) -> int:
    if not completed_on:
        return 0

    dates = {date.fromisoformat(value) for value in completed_on}
    last = max(dates)
    if last != today and last != today - timedelta(days=1):
        return 0

    streak = 1
    cursor = last
    for value in sorted(dates, reverse=True):
        if value == cursor:
            continue
        if value == cursor - timedelta(days=1):
            streak += 1
            cursor = value
        else:
            break
    return streak


def list_habits(state: dict, *, today: date) -> list[dict]:
    entries = [
        {
            "name": habit["name"],
            "streak": current_streak(habit["completed_on"], today=today),
        }
        for habit in state["habits"]
    ]
    entries.sort(key=lambda entry: (-entry["streak"], entry["name"].casefold()))
    return entries
