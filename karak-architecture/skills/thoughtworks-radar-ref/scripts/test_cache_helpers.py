"""Tests for thoughtworks-radar-ref cache_helpers and data integrity.

Run with::

    pytest karak-architecture/skills/thoughtworks-radar-ref/scripts/test_cache_helpers.py

Covers the highest-value contracts identified by the PR test analyzer:
- data integrity: themes.related_blip_names must resolve to actual blips
- atomic write: torn-write protection, no .tmp leftover, concurrent-safe
- cache I/O: round-trip, JSONDecodeError recovery (corrupt-file quarantine)
- environment: XDG_CACHE_HOME resolution including the empty-string footgun
"""

from __future__ import annotations

import json
import os
import sys
import time
from pathlib import Path

import pytest

SCRIPT_DIR = Path(__file__).resolve().parent
SKILL_ROOT = SCRIPT_DIR.parent
REFERENCES_DIR = SKILL_ROOT / "references"

sys.path.insert(0, str(SCRIPT_DIR))
import cache_helpers as ch  # noqa: E402


@pytest.fixture
def fake_cache_home(tmp_path, monkeypatch):
    """Redirect XDG_CACHE_HOME so cache writes land in tmp_path."""
    monkeypatch.setenv("XDG_CACHE_HOME", str(tmp_path))
    return tmp_path


# ---------------------------------------------------------------------------
# Data integrity (catches the bug PR review #1 identified)
# ---------------------------------------------------------------------------


def _discover_volume_numbers() -> list[int]:
    """Enumerate volumes by directory walk under references/volumes/. The
    directory layout is the source of truth — source_info.json carries only
    latest_volume, so we don't double-track availability.
    """
    volumes_root = REFERENCES_DIR / "volumes"
    nums = []
    for p in volumes_root.iterdir():
        if p.is_dir() and p.name.startswith("v") and p.name[1:].isdigit():
            nums.append(int(p.name[1:]))
    return sorted(nums)


def test_every_theme_related_blip_resolves_to_a_real_blip():
    """themes.related_blip_names must reference names that exist in blips.json
    for the same volume. The PR's own self-check documents this rule; the
    test makes it actually enforceable.

    Iterates every volume present on disk, not just the latest — protects
    against regressions in older volumes when v35/v36 land.
    """
    volume_numbers = _discover_volume_numbers()
    assert volume_numbers, "no volume directories found under references/volumes/"
    for vol in volume_numbers:
        blips = json.loads((REFERENCES_DIR / "volumes" / f"v{vol}" / "blips.json").read_text())
        themes = json.loads((REFERENCES_DIR / "volumes" / f"v{vol}" / "themes.json").read_text())
        blip_names = {b["name"] for b in blips}
        missing = []
        for theme in themes:
            for ref in theme["related_blip_names"]:
                if ref not in blip_names:
                    missing.append((theme["id"], ref))
        assert missing == [], (
            f"v{vol} themes reference blip names not present in blips.json: {missing}"
        )


def test_blip_rings_match_volume_ring_vocabulary():
    """Each blip's ring must be one of the values declared in its volume's
    manifest.ring_vocabulary.
    """
    vol = json.loads((REFERENCES_DIR / "source_info.json").read_text())["latest_volume"]
    manifest = json.loads(
        (REFERENCES_DIR / "volumes" / f"v{vol}" / "manifest.json").read_text()
    )
    allowed = set(manifest["ring_vocabulary"])
    blips = json.loads((REFERENCES_DIR / "volumes" / f"v{vol}" / "blips.json").read_text())
    offenders = [b["name"] for b in blips if b["ring"] not in allowed]
    assert offenders == [], (
        f"blips with rings outside manifest.ring_vocabulary {allowed}: {offenders}"
    )


def test_blips_carry_required_factual_fields():
    """Every blip must have the required fields per the schema; no blip
    should accidentally ship a free-form description field."""
    vol = ch.latest_volume()
    blips = ch.load_blips(vol)
    required = {"name", "ring", "quadrant", "volume", "radar_url"}
    forbidden = {"summary", "description"}  # would imply TW prose leaked in
    for blip in blips:
        assert required <= blip.keys(), f"missing keys on {blip.get('name')}: {required - blip.keys()}"
        leaked = forbidden & blip.keys()
        assert not leaked, f"blip {blip['name']} carries forbidden prose field(s): {leaked}"


# ---------------------------------------------------------------------------
# XDG_CACHE_HOME resolution
# ---------------------------------------------------------------------------


def test_cache_root_uses_xdg_cache_home_when_set(monkeypatch, tmp_path):
    monkeypatch.setenv("XDG_CACHE_HOME", str(tmp_path))
    assert ch.cache_root() == tmp_path / "karak-claude-plugin" / "thoughtworks-radar-ref"


def test_cache_root_falls_back_when_xdg_unset(monkeypatch):
    monkeypatch.delenv("XDG_CACHE_HOME", raising=False)
    root = ch.cache_root()
    assert root == Path.home() / ".cache" / "karak-claude-plugin" / "thoughtworks-radar-ref"


def test_cache_root_handles_empty_xdg_string(monkeypatch):
    """Empty-string XDG_CACHE_HOME must fall back to $HOME/.cache rather than
    rooting the cache at the filesystem root. Classic footgun: a refactor
    to ``os.environ.get(KEY, default)`` would silently break this.
    """
    monkeypatch.setenv("XDG_CACHE_HOME", "")
    root = ch.cache_root()
    assert root == Path.home() / ".cache" / "karak-claude-plugin" / "thoughtworks-radar-ref"


# ---------------------------------------------------------------------------
# Cache round-trip
# ---------------------------------------------------------------------------


def test_write_then_read_summary_round_trip(fake_cache_home):
    ch.write_cached_summary("OpenClaw", "test summary text", volume=34)
    assert ch.get_cached_summary("OpenClaw", volume=34) == "test summary text"


def test_write_summary_preserves_other_entries(fake_cache_home):
    ch.write_cached_summary("OpenClaw", "first", volume=34)
    ch.write_cached_summary("Cursor", "second", volume=34)
    assert ch.get_cached_summary("OpenClaw", volume=34) == "first"
    assert ch.get_cached_summary("Cursor", volume=34) == "second"


def test_write_summary_overwrites_same_key(fake_cache_home):
    ch.write_cached_summary("OpenClaw", "v1", volume=34)
    ch.write_cached_summary("OpenClaw", "v2", volume=34)
    assert ch.get_cached_summary("OpenClaw", volume=34) == "v2"


def test_cached_record_has_iso_timestamp_with_offset(fake_cache_home):
    ch.write_cached_summary("OpenClaw", "x", volume=34)
    cache_file = fake_cache_home / "karak-claude-plugin" / "thoughtworks-radar-ref" / "v34" / "blip_summaries.json"
    data = json.loads(cache_file.read_text())
    fetched_at = data["OpenClaw"]["fetched_at"]
    # ISO-8601 with timezone — either '+00:00' or 'Z'
    assert "T" in fetched_at
    assert fetched_at.endswith("+00:00") or fetched_at.endswith("Z"), (
        f"timestamp lacks timezone marker: {fetched_at!r}"
    )


def test_get_or_fetch_summary_calls_fetcher_on_miss(fake_cache_home):
    called = []

    def fetcher(url):
        called.append(url)
        return "fetched-summary"

    result = ch.get_or_fetch_summary("OpenClaw", fetcher=fetcher, volume=34)
    assert result == "fetched-summary"
    assert len(called) == 1
    # Second call hits cache; fetcher must not be invoked again
    result2 = ch.get_or_fetch_summary("OpenClaw", fetcher=fetcher, volume=34)
    assert result2 == "fetched-summary"
    assert len(called) == 1


def test_get_or_fetch_summary_returns_none_when_blip_unknown(fake_cache_home):
    assert (
        ch.get_or_fetch_summary("not-a-real-blip", fetcher=lambda u: "x", volume=34)
        is None
    )


def test_get_or_fetch_summary_no_fetcher_acts_as_pure_read(fake_cache_home):
    # Cache miss + fetcher=None must return None, not raise.
    assert ch.get_or_fetch_summary("OpenClaw", fetcher=None, volume=34) is None


# ---------------------------------------------------------------------------
# Corruption recovery
# ---------------------------------------------------------------------------


def test_read_json_quarantines_corrupt_file_and_returns_empty(fake_cache_home, capsys):
    cache_dir = fake_cache_home / "karak-claude-plugin" / "thoughtworks-radar-ref" / "v34"
    cache_dir.mkdir(parents=True)
    bad = cache_dir / "blip_summaries.json"
    bad.write_text("not json at all {{{")

    # _read_json must not raise; it must quarantine and return {}
    data = ch._read_json(bad)
    assert data == {}
    assert not bad.exists(), "corrupt file should have been renamed"
    quarantined = list(cache_dir.glob("blip_summaries.json.corrupt-*"))
    assert len(quarantined) == 1, f"expected exactly one quarantined file, got {quarantined}"
    err = capsys.readouterr().err
    assert "corrupt" in err.lower()


def test_write_path_recovers_after_quarantine(fake_cache_home):
    """A corrupt cache must not block subsequent writes."""
    cache_dir = fake_cache_home / "karak-claude-plugin" / "thoughtworks-radar-ref" / "v34"
    cache_dir.mkdir(parents=True)
    (cache_dir / "blip_summaries.json").write_text("garbage")

    ch.write_cached_summary("OpenClaw", "fresh", volume=34)
    assert ch.get_cached_summary("OpenClaw", volume=34) == "fresh"


# ---------------------------------------------------------------------------
# Atomic write
# ---------------------------------------------------------------------------


def test_atomic_write_leaves_no_tmp_artifact_on_success(fake_cache_home):
    ch.write_cached_summary("OpenClaw", "ok", volume=34)
    cache_dir = fake_cache_home / "karak-claude-plugin" / "thoughtworks-radar-ref" / "v34"
    stragglers = list(cache_dir.glob("*.tmp"))
    assert stragglers == [], f"leftover tmp files: {stragglers}"


def test_atomic_write_preserves_original_on_failure(fake_cache_home, monkeypatch):
    """If json.dump raises mid-write, the original file must be unchanged
    and the tmp file must be cleaned up. The whole point of the
    tmp+rename pattern.
    """
    ch.write_cached_summary("OpenClaw", "good", volume=34)
    cache_dir = fake_cache_home / "karak-claude-plugin" / "thoughtworks-radar-ref" / "v34"
    target = cache_dir / "blip_summaries.json"
    before = target.read_bytes()

    # Make json.dump raise on the next call
    real_dump = ch.json.dump

    def boom(*args, **kwargs):
        raise RuntimeError("simulated disk-full")

    monkeypatch.setattr(ch.json, "dump", boom)

    with pytest.raises(RuntimeError):
        ch.write_cached_summary("Cursor", "should not land", volume=34)

    # Original untouched
    assert target.read_bytes() == before
    # No tmp leftover
    monkeypatch.setattr(ch.json, "dump", real_dump)
    stragglers = list(cache_dir.glob("*.tmp"))
    assert stragglers == [], f"leftover tmp files after failed write: {stragglers}"


def test_atomic_write_uses_unique_tmp_names(fake_cache_home, monkeypatch):
    """Two writers must not collide on a single fixed `.tmp` filename. We
    simulate by inspecting the tmp names mkstemp produces during a write.
    """
    cache_dir = fake_cache_home / "karak-claude-plugin" / "thoughtworks-radar-ref" / "v34"
    cache_dir.mkdir(parents=True)
    target = cache_dir / "blip_summaries.json"

    captured = []
    real_mkstemp = ch.tempfile.mkstemp

    def spy_mkstemp(*args, **kwargs):
        fd, name = real_mkstemp(*args, **kwargs)
        captured.append(name)
        return fd, name

    monkeypatch.setattr(ch.tempfile, "mkstemp", spy_mkstemp)

    ch._write_json_atomic(target, {"a": 1})
    ch._write_json_atomic(target, {"a": 2})
    assert len(captured) == 2
    assert captured[0] != captured[1], "tmp names must differ across writes"
