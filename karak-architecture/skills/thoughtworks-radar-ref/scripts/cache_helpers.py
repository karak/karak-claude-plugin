"""Runtime cache helpers for thoughtworks-radar-ref.

Stdlib only. Reads the structural index (which ships with the skill) and a
per-user cache that holds Thoughtworks-authored summary/narrative text fetched
on demand. Cache lives outside the distribution to keep copyrighted prose out
of the git repo.

Cache layout::

    ${XDG_CACHE_HOME:-$HOME/.cache}/karak-claude-plugin/thoughtworks-radar-ref/v<NN>/
        blip_summaries.json     { "<blip_name>": { "summary": "...", "fetched_at": "..." } }
        theme_narratives.json   { "<theme_id>":  { "narrative": "...", "fetched_at": "..." } }
        .meta.json              { "volume": NN, "last_full_refresh": "..." }
"""

from __future__ import annotations

import json
import os
from datetime import datetime, timezone
from pathlib import Path


SKILL_ROOT = Path(__file__).resolve().parent.parent
REFERENCES_DIR = SKILL_ROOT / "references"


def cache_root() -> Path:
    """Return the XDG-compliant cache root for this skill."""
    base = os.environ.get("XDG_CACHE_HOME") or str(Path.home() / ".cache")
    return Path(base) / "karak-claude-plugin" / "thoughtworks-radar-ref"


def volume_cache_dir(volume: int) -> Path:
    d = cache_root() / f"v{volume}"
    d.mkdir(parents=True, exist_ok=True)
    return d


def latest_volume() -> int:
    """Resolve the latest volume number from source_info.json."""
    with (REFERENCES_DIR / "source_info.json").open("r", encoding="utf-8") as f:
        return int(json.load(f)["latest_volume"])


def volume_dir(volume: int) -> Path:
    return REFERENCES_DIR / "volumes" / f"v{volume}"


def load_blips(volume: int | None = None) -> list[dict]:
    v = volume if volume is not None else latest_volume()
    with (volume_dir(v) / "blips.json").open("r", encoding="utf-8") as f:
        return json.load(f)


def load_themes(volume: int | None = None) -> list[dict]:
    v = volume if volume is not None else latest_volume()
    with (volume_dir(v) / "themes.json").open("r", encoding="utf-8") as f:
        return json.load(f)


def _read_json(path: Path) -> dict:
    if not path.exists():
        return {}
    with path.open("r", encoding="utf-8") as f:
        return json.load(f)


def _write_json_atomic(path: Path, data: dict) -> None:
    """Write JSON atomically — tmp file then rename — to avoid torn writes."""
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(path.suffix + ".tmp")
    with tmp.open("w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2, sort_keys=True)
    tmp.replace(path)


def get_cached_summary(blip_name: str, volume: int | None = None) -> str | None:
    """Return cached summary text for blip, or None if not cached.

    The caller is responsible for invoking WebFetch on the blip's radar_url
    if this returns None, then calling write_cached_summary().
    """
    v = volume if volume is not None else latest_volume()
    cache = _read_json(volume_cache_dir(v) / "blip_summaries.json")
    entry = cache.get(blip_name)
    return entry.get("summary") if entry else None


def write_cached_summary(blip_name: str, summary: str, volume: int | None = None) -> None:
    v = volume if volume is not None else latest_volume()
    path = volume_cache_dir(v) / "blip_summaries.json"
    cache = _read_json(path)
    cache[blip_name] = {
        "summary": summary,
        "fetched_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
    }
    _write_json_atomic(path, cache)


def get_cached_theme_narrative(theme_id: str, volume: int | None = None) -> str | None:
    v = volume if volume is not None else latest_volume()
    cache = _read_json(volume_cache_dir(v) / "theme_narratives.json")
    entry = cache.get(theme_id)
    return entry.get("narrative") if entry else None


def write_cached_theme_narrative(theme_id: str, narrative: str, volume: int | None = None) -> None:
    v = volume if volume is not None else latest_volume()
    path = volume_cache_dir(v) / "theme_narratives.json"
    cache = _read_json(path)
    cache[theme_id] = {
        "narrative": narrative,
        "fetched_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
    }
    _write_json_atomic(path, cache)


def find_blip(blip_name: str, volume: int | None = None) -> dict | None:
    """Look up a blip by exact name."""
    for blip in load_blips(volume):
        if blip["name"] == blip_name:
            return blip
    return None


def find_theme(theme_id: str, volume: int | None = None) -> dict | None:
    for theme in load_themes(volume):
        if theme["id"] == theme_id:
            return theme
    return None


if __name__ == "__main__":
    # Quick self-test
    v = latest_volume()
    print(f"Latest volume: v{v}")
    print(f"Cache dir: {volume_cache_dir(v)}")
    print(f"Blip count: {len(load_blips(v))}")
    print(f"Theme count: {len(load_themes(v))}")
