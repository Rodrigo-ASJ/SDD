import json
import subprocess
import sys
from datetime import date, timedelta

import pytest

from habits import cli


def test_module_runs_without_error():
    result = subprocess.run(
        [sys.executable, "-m", "habits"],
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0


@pytest.fixture
def data_file(tmp_path, monkeypatch):
    path = tmp_path / "data.json"
    monkeypatch.setenv("HABITS_FILE", str(path))
    return path


def test_add_then_list(data_file, capsys):
    assert cli.main(["add", "Leer"]) == 0
    assert "Hábito 'Leer' creado." in capsys.readouterr().out

    assert cli.main(["list"]) == 0
    out = capsys.readouterr().out
    assert "Leer" in out
    assert "racha: 0" in out


def test_add_duplicate_returns_error(data_file, capsys):
    cli.main(["add", "Leer"])
    capsys.readouterr()
    assert cli.main(["add", "  leer "]) == 1
    assert "ya existe" in capsys.readouterr().err


def test_add_empty_name_returns_error(data_file, capsys):
    assert cli.main(["add", "   "]) == 1
    assert "no puede estar vacío" in capsys.readouterr().err


def test_done_marks_today_and_is_idempotent(data_file, capsys):
    cli.main(["add", "Leer"])
    capsys.readouterr()
    today = date.today().isoformat()

    assert cli.main(["done", "Leer"]) == 0
    assert f"hoy ({today})" in capsys.readouterr().out

    assert cli.main(["done", "Leer"]) == 0
    assert "ya estaba marcado hoy" in capsys.readouterr().out


def test_done_missing_habit_returns_error(data_file, capsys):
    assert cli.main(["done", "Correr"]) == 1
    assert "No existe" in capsys.readouterr().err


def test_list_empty(data_file, capsys):
    assert cli.main(["list"]) == 0
    assert "Aún no hay hábitos" in capsys.readouterr().out


def test_corrupt_file_returns_error(tmp_path, monkeypatch, capsys):
    path = tmp_path / "data.json"
    path.write_text("{ roto", encoding="utf-8")
    monkeypatch.setenv("HABITS_FILE", str(path))
    assert cli.main(["list"]) == 1
    assert "dañado" in capsys.readouterr().err
    assert path.read_text(encoding="utf-8") == "{ roto"


def test_list_orders_by_streak_then_name(data_file, capsys):
    today = date.today()
    yesterday = (today - timedelta(days=1)).isoformat()
    data_file.write_text(
        json.dumps(
            {
                "version": 1,
                "habits": [
                    {
                        "name": "Zeta",
                        "created_on": today.isoformat(),
                        "completed_on": [today.isoformat()],
                    },
                    {
                        "name": "Alfa",
                        "created_on": today.isoformat(),
                        "completed_on": [today.isoformat()],
                    },
                    {
                        "name": "Leer",
                        "created_on": today.isoformat(),
                        "completed_on": [yesterday, today.isoformat()],
                    },
                    {
                        "name": "Beta",
                        "created_on": today.isoformat(),
                        "completed_on": [],
                    },
                ],
            }
        ),
        encoding="utf-8",
    )

    assert cli.main(["list"]) == 0
    out = capsys.readouterr().out
    assert out.index("Leer") < out.index("Alfa") < out.index("Zeta") < out.index("Beta")
    assert "Leer\tracha: 2" in out
    assert "Alfa\tracha: 1" in out
    assert "Zeta\tracha: 1" in out
    assert "Beta\tracha: 0" in out
