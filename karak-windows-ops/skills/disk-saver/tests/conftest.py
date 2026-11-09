import json
import os
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "scripts"))

CATALOG_PATH = ROOT / "catalog" / "windows.json"


@pytest.fixture
def catalog():
    return json.loads(CATALOG_PATH.read_text(encoding="utf-8"))


@pytest.fixture
def fake_env(tmp_path):
    """A fake Windows profile rooted in tmp_path."""
    home = tmp_path / "Users" / "someone"
    local = home / "AppData" / "Local"
    roaming = home / "AppData" / "Roaming"
    for d in (home, local, roaming, local / "Temp"):
        d.mkdir(parents=True, exist_ok=True)
    return {
        "USERPROFILE": str(home),
        "LOCALAPPDATA": str(local),
        "APPDATA": str(roaming),
        "TEMP": str(local / "Temp"),
        "PROGRAMDATA": str(tmp_path / "ProgramData"),
        "SYSTEMDRIVE": str(tmp_path / "C"),
        "ONEDRIVE": str(home / "OneDrive - Org"),
    }


def write_file(path: Path, size: int, mtime: float | None = None) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(b"x" * size)
    if mtime is not None:
        os.utime(path, (mtime, mtime))
    return path
