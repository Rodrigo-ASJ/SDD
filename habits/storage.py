from __future__ import annotations

import json
import os
from pathlib import Path

VERSION = 1
DEFAULT_PATH = Path.home() / ".habits" / "data.json"


class StorageError(Exception):
    """Error al leer o interpretar el archivo de datos."""


def empty_state() -> dict:
    return {"version": VERSION, "habits": []}


def data_path() -> Path:
    override = os.environ.get("HABITS_FILE")
    if override:
        return Path(override)
    return DEFAULT_PATH


def load(path: Path | None = None) -> dict:
    target = path if path is not None else data_path()
    if not target.exists():
        return empty_state()
    try:
        with target.open(encoding="utf-8") as handle:
            return json.load(handle)
    except (json.JSONDecodeError, OSError) as exc:
        raise StorageError(
            f"El archivo de datos {target} está dañado y no se ha modificado."
        ) from exc


def save(state: dict, path: Path | None = None) -> None:
    target = path if path is not None else data_path()
    target.parent.mkdir(parents=True, exist_ok=True)
    tmp = target.with_suffix(target.suffix + ".tmp")
    with tmp.open("w", encoding="utf-8") as handle:
        json.dump(state, handle, ensure_ascii=False, indent=2)
    os.replace(tmp, target)
