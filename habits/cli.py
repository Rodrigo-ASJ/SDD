from __future__ import annotations

import argparse
import sys
from datetime import date

from habits import core, storage


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="habits", description="Registra hábitos de estudio y sus rachas."
    )
    subparsers = parser.add_subparsers(dest="command")
    add = subparsers.add_parser("add", help="Crea un hábito.")
    add.add_argument("name", help="Nombre del hábito.")
    done = subparsers.add_parser("done", help="Marca un hábito como hecho hoy.")
    done.add_argument("name", help="Nombre del hábito.")
    subparsers.add_parser("list", help="Lista los hábitos con su racha.")
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = _build_parser()
    args = parser.parse_args(argv)

    if args.command is None:
        parser.print_help()
        return 0

    try:
        state = storage.load()
    except storage.StorageError as exc:
        print(str(exc), file=sys.stderr)
        return 1

    today = date.today()
    name = getattr(args, "name", "").strip()

    try:
        if args.command == "add":
            state = core.add_habit(state, name, created_on=today)
            storage.save(state)
            print(f"Hábito '{name}' creado.")
            return 0

        if args.command == "done":
            state, added = core.mark_done(state, name, today=today)
            if added:
                storage.save(state)
                print(f"Hecho: '{name}' hoy ({today.isoformat()}).")
            else:
                print(f"'{name}' ya estaba marcado hoy.")
            return 0

        if args.command == "list":
            entries = core.list_habits(state, today=today)
            if not entries:
                print("Aún no hay hábitos. Crea el primero con: habits add <nombre>")
                return 0
            for entry in entries:
                print(f"{entry['name']}\tracha: {entry['streak']} días")
            return 0
    except core.HabitError as exc:
        print(str(exc), file=sys.stderr)
        return 1

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
