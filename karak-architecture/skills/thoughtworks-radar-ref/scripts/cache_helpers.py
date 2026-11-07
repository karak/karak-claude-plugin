"""Runtime cache helpers for thoughtworks-radar-ref.

Stdlib only. Reads the structural index (which ships with the skill) and a
per-user cache that holds Thoughtworks-authored summary/narrative text fetched
on demand. Cache lives outside the distribution to keep copyrighted prose out
of the git repo.

Cache layout::

    ${XDG_CACHE_HOME:-$HOME/.cache}/karak-claude-plugin/thoughtworks-radar-ref/v<NN>/
        blip_summaries.json     { "<blip_name>": { "summary": "...", "fetched_at": "...", "source_url": "..." } }
        theme_narratives.json   { "<theme_id>":  { "narrative": "...", "fetched_at": "...", "source_url": "..." } }
        .meta.json              { "volume": NN, "last_full_refresh": "..." }

An entry is served only while its ``source_url`` equals the blip's current
``radar_url`` (or the theme's ``source_url``) in the index, so correcting a
URL in a published volume invalidates the old entry.
"""

from __future__ import annotations

import json
import os
import sys
import tempfile
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Callable


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
    """Read a JSON cache file. On corruption, quarantine the bad file and
    return ``{}`` so the caller can rebuild — never raise JSONDecodeError
    from a cache read, since the cache is rebuildable by re-fetching.
    """
    if not path.exists():
        return {}
    try:
        with path.open("r", encoding="utf-8") as f:
            return json.load(f)
    except json.JSONDecodeError as exc:
        backup = path.with_suffix(path.suffix + f".corrupt-{int(time.time())}")
        try:
            path.rename(backup)
        except OSError:
            backup = None
        print(
            f"WARNING: cache file {path} was corrupt ({exc}); "
            f"{'quarantined as ' + str(backup) if backup else 'could not quarantine'}; "
            f"rebuilding from empty.",
            file=sys.stderr,
        )
        return {}


def _write_json_atomic(path: Path, data: dict) -> None:
    """Write JSON atomically — unique tmp file in the same directory then
    rename — to avoid torn writes AND avoid concurrent-writer collision on
    a fixed `.tmp` filename. The rename itself is filesystem-atomic; the
    unique tmp name means two writers don't truncate each other's tmp.
    """
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, tmp_name = tempfile.mkstemp(
        prefix=path.name + ".",
        suffix=".tmp",
        dir=str(path.parent),
    )
    tmp = Path(tmp_name)
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2, sort_keys=True)
        tmp.replace(path)
    except Exception:
        # Clean up the orphan tmp file on failure so we don't leak.
        try:
            tmp.unlink()
        except OSError:
            pass
        raise


def _entry_if_current(entry: dict | None, source_url: str | None) -> dict | None:
    """Return ``entry`` only if it was fetched from ``source_url``.

    Entries are bound to the URL they were fetched from, so correcting a
    blip's ``radar_url`` (or a theme's ``source_url``) in the index turns the
    old entry into a miss. Entries without ``source_url`` predate this rule
    and are treated as misses too.
    """
    if not entry or source_url is None or entry.get("source_url") != source_url:
        return None
    return entry


def _blip_key_and_url(blip_name: str, volume: int, source_url: str | None) -> tuple[str, str | None]:
    """Resolve the cache key (the index ``name``, even when looked up by
    ``page_title``) and the expected source URL (the index ``radar_url``
    unless given explicitly)."""
    blip = find_blip(blip_name, volume)
    key = blip["name"] if blip else blip_name
    if source_url is None and blip:
        source_url = blip["radar_url"]
    return key, source_url


def get_cached_summary(
    blip_name: str, volume: int | None = None, source_url: str | None = None
) -> str | None:
    """Return cached summary text for blip, or None if not cached.

    An entry counts only if it was fetched from ``source_url`` (default: the
    blip's current ``radar_url`` in the index). The caller is responsible for
    invoking WebFetch on the blip's radar_url if this returns None, then
    calling write_cached_summary().
    """
    v = volume if volume is not None else latest_volume()
    key, url = _blip_key_and_url(blip_name, v, source_url)
    cache = _read_json(volume_cache_dir(v) / "blip_summaries.json")
    entry = _entry_if_current(cache.get(key), url)
    return entry.get("summary") if entry else None


def write_cached_summary(
    blip_name: str, summary: str, volume: int | None = None, source_url: str | None = None
) -> None:
    """Cache ``summary`` together with the URL it was fetched from
    (default: the blip's current ``radar_url`` in the index)."""
    v = volume if volume is not None else latest_volume()
    key, url = _blip_key_and_url(blip_name, v, source_url)
    path = volume_cache_dir(v) / "blip_summaries.json"
    cache = _read_json(path)
    cache[key] = {
        "summary": summary,
        "fetched_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "source_url": url,
    }
    _write_json_atomic(path, cache)


def _theme_url(theme_id: str, volume: int, source_url: str | None) -> str | None:
    if source_url is not None:
        return source_url
    theme = find_theme(theme_id, volume)
    return theme["source_url"] if theme else None


def get_cached_theme_narrative(
    theme_id: str, volume: int | None = None, source_url: str | None = None
) -> str | None:
    v = volume if volume is not None else latest_volume()
    cache = _read_json(volume_cache_dir(v) / "theme_narratives.json")
    entry = _entry_if_current(cache.get(theme_id), _theme_url(theme_id, v, source_url))
    return entry.get("narrative") if entry else None


def write_cached_theme_narrative(
    theme_id: str, narrative: str, volume: int | None = None, source_url: str | None = None
) -> None:
    v = volume if volume is not None else latest_volume()
    path = volume_cache_dir(v) / "theme_narratives.json"
    cache = _read_json(path)
    cache[theme_id] = {
        "narrative": narrative,
        "fetched_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "source_url": _theme_url(theme_id, v, source_url),
    }
    _write_json_atomic(path, cache)


def get_or_fetch_summary(
    blip_name: str,
    fetcher: Callable[[str], str] | None = None,
    volume: int | None = None,
) -> str | None:
    """Read a blip summary from cache, falling back to ``fetcher(radar_url)``
    on miss and persisting the result. Returns ``None`` only if the blip is
    not in the structural index for this volume.

    ``fetcher`` is a caller-supplied function that takes the blip's
    ``radar_url`` and returns the summary text. Pass ``None`` to disable
    fetching (acts as a pure cache read).

    This is the convenience entry point referenced from SKILL.md; tools that
    need finer control can still call ``get_cached_summary`` /
    ``write_cached_summary`` directly.
    """
    cached = get_cached_summary(blip_name, volume)
    if cached is not None:
        return cached
    if fetcher is None:
        return None
    blip = find_blip(blip_name, volume)
    if blip is None:
        return None
    summary = fetcher(blip["radar_url"])
    if not summary:
        return None
    write_cached_summary(blip["name"], summary, volume)
    return summary


def get_or_fetch_theme_narrative(
    theme_id: str,
    fetcher: Callable[[str], str] | None = None,
    volume: int | None = None,
) -> str | None:
    """Theme-narrative twin of :func:`get_or_fetch_summary`."""
    cached = get_cached_theme_narrative(theme_id, volume)
    if cached is not None:
        return cached
    if fetcher is None:
        return None
    theme = find_theme(theme_id, volume)
    if theme is None:
        return None
    narrative = fetcher(theme["source_url"])
    if not narrative:
        return None
    write_cached_theme_narrative(theme_id, narrative, volume)
    return narrative


def find_blip(blip_name: str, volume: int | None = None) -> dict | None:
    """Look up a blip by exact ``name``, falling back to exact ``page_title``
    (the name the site shows now, when it was renamed after publication)."""
    blips = load_blips(volume)
    for blip in blips:
        if blip["name"] == blip_name:
            return blip
    for blip in blips:
        if blip.get("page_title") == blip_name:
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
