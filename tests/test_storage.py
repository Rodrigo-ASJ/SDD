from pathlib import Path

import pytest

from habits import storage

SAMPLE = {
    "version": 1,
    "habits": [
        {
            "name": "Leer",
            "created_on": "2026-10-10",
            "completed_on": ["2026-10-14"],
        }
    ],
}


def test_load_missing_file_returns_empty_state(tmp_path):
    assert storage.load(tmp_path / "data.json") == {"version": 1, "habits": []}


def test_save_then_load_roundtrip(tmp_path):
    path = tmp_path / "data.json"
    storage.save(SAMPLE, path)
    assert storage.load(path) == SAMPLE


def test_load_corrupt_file_raises_and_keeps_content(tmp_path):
    path = tmp_path / "data.json"
    path.write_text("{ esto no es JSON valido", encoding="utf-8")
    original = path.read_text(encoding="utf-8")
    with pytest.raises(storage.StorageError):
        storage.load(path)
    assert path.read_text(encoding="utf-8") == original


def test_data_path_respects_env_override(monkeypatch, tmp_path):
    custom = tmp_path / "custom.json"
    monkeypatch.setenv("HABITS_FILE", str(custom))
    assert storage.data_path() == custom
