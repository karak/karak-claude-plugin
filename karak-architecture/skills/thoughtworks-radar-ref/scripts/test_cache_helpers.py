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

    Iterates every volume on disk so regressions in older volumes are
    caught, not just the latest.
    """
    volume_numbers = _discover_volume_numbers()
    assert volume_numbers, "no volume directories found under references/volumes/"
    for vol in volume_numbers:
        blips = json.loads((REFERENCES_DIR / "volumes" / f"v{vol}" / "blips.json").read_text(encoding="utf-8"))
        themes = json.loads((REFERENCES_DIR / "volumes" / f"v{vol}" / "themes.json").read_text(encoding="utf-8"))
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
    vol = json.loads((REFERENCES_DIR / "source_info.json").read_text(encoding="utf-8"))["latest_volume"]
    manifest = json.loads(
        (REFERENCES_DIR / "volumes" / f"v{vol}" / "manifest.json").read_text(encoding="utf-8")
    )
    allowed = set(manifest["ring_vocabulary"])
    blips = json.loads((REFERENCES_DIR / "volumes" / f"v{vol}" / "blips.json").read_text(encoding="utf-8"))
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
    data = json.loads(cache_file.read_text(encoding="utf-8"))
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
# Cache entries are bound to the URL they were fetched from (#31 review):
# correcting radar_url / source_url in the index must invalidate old entries.
# ---------------------------------------------------------------------------


def _cache_file(home: Path, volume: int, name: str) -> Path:
    return home / "karak-claude-plugin" / "thoughtworks-radar-ref" / f"v{volume}" / name


def test_write_summary_records_source_url(fake_cache_home):
    ch.write_cached_summary("TOON", "x", volume=34)
    data = json.loads(_cache_file(fake_cache_home, 34, "blip_summaries.json").read_text(encoding="utf-8"))
    assert data["TOON"]["source_url"] == ch.find_blip("TOON", 34)["radar_url"]


def test_summary_from_old_radar_url_is_a_miss(fake_cache_home):
    """The v34 TOON entry fetched from the old /toon URL (the quadrant page)
    must not be served after radar_url was corrected."""
    path = _cache_file(fake_cache_home, 34, "blip_summaries.json")
    path.parent.mkdir(parents=True)
    path.write_text(json.dumps({"TOON": {
        "summary": "Languages & Frameworks quadrant page",
        "fetched_at": "2026-10-01T00:00:00+00:00",
        "source_url": "https://www.thoughtworks.com/radar/languages-and-frameworks/toon",
    }}), encoding="utf-8")
    assert ch.get_cached_summary("TOON", volume=34) is None

    called = []
    result = ch.get_or_fetch_summary("TOON", fetcher=lambda u: called.append(u) or "blip page", volume=34)
    assert result == "blip page"
    assert called == [ch.find_blip("TOON", 34)["radar_url"]]
    assert ch.get_cached_summary("TOON", volume=34) == "blip page"


def test_summary_without_source_url_is_a_miss(fake_cache_home):
    """Entries written before source_url was recorded cannot be trusted
    (the v34 TOON entry is one of them), so they are refetched once."""
    path = _cache_file(fake_cache_home, 34, "blip_summaries.json")
    path.parent.mkdir(parents=True)
    path.write_text(json.dumps({"TOON": {"summary": "old", "fetched_at": "2026-10-01T00:00:00+00:00"}}), encoding="utf-8")
    assert ch.get_cached_summary("TOON", volume=34) is None


def test_explicit_source_url_overrides_index_lookup(fake_cache_home):
    ch.write_cached_summary("not-in-index", "x", volume=34, source_url="https://example.com/a")
    assert ch.get_cached_summary("not-in-index", volume=34, source_url="https://example.com/a") == "x"
    assert ch.get_cached_summary("not-in-index", volume=34, source_url="https://example.com/b") is None
    assert ch.get_cached_summary("not-in-index", volume=34) is None


def test_theme_narrative_from_old_source_url_is_a_miss(fake_cache_home):
    theme_id = "putting-coding-agents-on-a-leash"
    path = _cache_file(fake_cache_home, 34, "theme_narratives.json")
    path.parent.mkdir(parents=True)
    path.write_text(json.dumps({theme_id: {
        "narrative": "stale", "fetched_at": "2026-10-01T00:00:00+00:00",
        "source_url": "https://example.com/old",
    }}), encoding="utf-8")
    assert ch.get_cached_theme_narrative(theme_id, volume=34) is None
    ch.write_cached_theme_narrative(theme_id, "fresh", volume=34)
    assert ch.get_cached_theme_narrative(theme_id, volume=34) == "fresh"


# ---------------------------------------------------------------------------
# page_title is a lookup alias for name (#31 review)
# ---------------------------------------------------------------------------


def test_find_blip_matches_page_title():
    blip = ch.find_blip("Amazon Bedrock AgentCore", 34)
    assert blip is not None
    assert blip["name"] == "AWS Bedrock AgentCore"


def test_get_or_fetch_summary_by_page_title_uses_name_as_cache_key(fake_cache_home):
    result = ch.get_or_fetch_summary("Amazon Bedrock AgentCore", fetcher=lambda u: "agentcore", volume=34)
    assert result == "agentcore"
    data = json.loads(_cache_file(fake_cache_home, 34, "blip_summaries.json").read_text(encoding="utf-8"))
    assert list(data) == ["AWS Bedrock AgentCore"]
    assert ch.get_cached_summary("AWS Bedrock AgentCore", volume=34) == "agentcore"


# ---------------------------------------------------------------------------
# Theme narrative cache + find_theme (twin of the blip-side tests above)
# ---------------------------------------------------------------------------


def test_get_or_fetch_theme_narrative_round_trip(fake_cache_home):
    """Miss → fetcher invoked once → second call hits cache, fetcher not
    invoked again. Mirrors the blip-summary contract.
    """
    called = []

    def fetcher(url):
        called.append(url)
        return "fetched-narrative"

    theme_id = "putting-coding-agents-on-a-leash"
    result = ch.get_or_fetch_theme_narrative(theme_id, fetcher=fetcher, volume=34)
    assert result == "fetched-narrative"
    assert len(called) == 1

    result2 = ch.get_or_fetch_theme_narrative(theme_id, fetcher=fetcher, volume=34)
    assert result2 == "fetched-narrative"
    assert len(called) == 1, "second call must come from cache, not fetcher"


def test_get_or_fetch_theme_narrative_returns_none_for_unknown_id(fake_cache_home):
    assert (
        ch.get_or_fetch_theme_narrative(
            "definitely-not-a-real-theme", fetcher=lambda u: "x", volume=34
        )
        is None
    )


def test_find_theme_returns_none_for_unknown_id():
    assert ch.find_theme("definitely-not-a-real-theme", volume=34) is None


def test_find_theme_resolves_within_volume():
    """find_theme scopes to the requested volume and returns the matching
    record. Multi-volume "latest wins" semantics are NOT part of the current
    contract — the function takes a volume and looks only there.
    """
    theme_id = "putting-coding-agents-on-a-leash"
    theme = ch.find_theme(theme_id, volume=34)
    assert theme is not None
    assert theme["id"] == theme_id
    assert theme["volume"] == 34


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


def _volume_files(vol: int) -> tuple[dict, list]:
    vdir = REFERENCES_DIR / "volumes" / f"v{vol}"
    manifest = json.loads((vdir / "manifest.json").read_text(encoding="utf-8"))
    blips = json.loads((vdir / "blips.json").read_text(encoding="utf-8"))
    return manifest, blips


def test_manifest_counts_match_blips():
    """manifest blip_counts / ring_counts (when present) equal the tallies of blips.json."""
    for vol in _discover_volume_numbers():
        manifest, blips = _volume_files(vol)
        if "blip_counts" in manifest:
            by_quadrant = {}
            for b in blips:
                by_quadrant[b["quadrant"]] = by_quadrant.get(b["quadrant"], 0) + 1
            expected = {**by_quadrant, "total": len(blips)}
            assert manifest["blip_counts"] == expected, f"v{vol} blip_counts drifted"
        if "ring_counts" in manifest:
            by_ring = {}
            for b in blips:
                by_ring[b["ring"]] = by_ring.get(b["ring"], 0) + 1
            assert manifest["ring_counts"] == by_ring, f"v{vol} ring_counts drifted"


def test_radar_urls_use_quadrant_slug_form():
    """radar_url is https://www.thoughtworks.com/radar/<quadrant-slug>/<slug>,
    with the quadrant slug matching the blip's quadrant and no /summary/ segment."""
    slugs = {
        "Techniques": "techniques",
        "Platforms": "platforms",
        "Tools": "tools",
        "Languages & Frameworks": "languages-and-frameworks",
    }
    base = "https://www.thoughtworks.com/radar/"
    for vol in _discover_volume_numbers():
        _, blips = _volume_files(vol)
        bad = []
        for b in blips:
            rest = b["radar_url"].removeprefix(base)
            parts = rest.split("/")
            if len(parts) != 2 or parts[0] != slugs[b["quadrant"]] or not parts[1]:
                bad.append(b["name"])
        assert bad == [], f"v{vol} radar_url outside the expected form: {bad}"


def test_ring_changes_use_blip_moves_form_from_v35():
    """From v35 on, manifest.ring_changes_from_prev uses the blipMoves form
    (radar-schema.json $defs/blipMoves). v34 keeps the legacy ringRename form."""
    for vol in _discover_volume_numbers():
        if vol < 35:
            continue
        manifest, _ = _volume_files(vol)
        changes = manifest["ring_changes_from_prev"]
        assert {"vocabulary_changed", "moved_blips", "carried_over_count"} <= changes.keys(), (
            f"v{vol} ring_changes_from_prev is not in the blipMoves form"
        )


def test_blip_moves_match_previous_volume():
    """moved_blips / carried_over_count / vocabulary_changed equal a recomputation
    from this volume's and the previous volume's blips.json (exact-name match)."""
    volumes = _discover_volume_numbers()
    for prev, vol in zip(volumes, volumes[1:]):
        manifest, blips = _volume_files(vol)
        changes = manifest["ring_changes_from_prev"]
        if "moved_blips" not in changes:
            continue
        prev_manifest, prev_blips = _volume_files(prev)
        before = {b["name"]: b for b in prev_blips}
        carried = [b for b in blips if b["name"] in before]
        expected = {
            b["name"]: (before[b["name"]]["quadrant"], b["quadrant"], before[b["name"]]["ring"], b["ring"])
            for b in carried
            if (b["quadrant"], b["ring"]) != (before[b["name"]]["quadrant"], before[b["name"]]["ring"])
        }
        actual = {
            m["name"]: (
                m.get("from_quadrant", m.get("quadrant")),
                m.get("to_quadrant", m.get("quadrant")),
                m["from"],
                m["to"],
            )
            for m in changes["moved_blips"]
        }
        assert actual == expected, f"v{vol} moved_blips drifted from v{prev}"
        assert changes["carried_over_count"] == len(carried), f"v{vol} carried_over_count drifted"
        assert changes["vocabulary_changed"] == (
            prev_manifest["ring_vocabulary"] != manifest["ring_vocabulary"]
        ), f"v{vol} vocabulary_changed is wrong"


def test_volume_files_match_radar_schema():
    """blips / themes / manifest of every volume validate against radar-schema.json."""
    jsonschema = pytest.importorskip("jsonschema")
    schema = json.loads((REFERENCES_DIR / "radar-schema.json").read_text(encoding="utf-8"))
    jsonschema.Draft7Validator.check_schema(schema)

    def validator(name):
        return jsonschema.Draft7Validator({**schema["$defs"][name], "$defs": schema["$defs"]})

    for vol in _discover_volume_numbers():
        vdir = REFERENCES_DIR / "volumes" / f"v{vol}"
        manifest = json.loads((vdir / "manifest.json").read_text(encoding="utf-8"))
        errors = [e.message for e in validator("manifest").iter_errors(manifest)]
        for kind in ("blip", "theme"):
            records = json.loads((vdir / f"{kind}s.json").read_text(encoding="utf-8"))
            errors += [f"{r.get('name', r.get('id'))}: {e.message}" for r in records for e in validator(kind).iter_errors(r)]
        assert errors == [], f"v{vol} schema violations: {errors[:5]}"


def _verify_urls_module():
    import importlib

    return importlib.import_module("verify_urls")


def test_verify_urls_uses_page_title_when_set(monkeypatch):
    vu = _verify_urls_module()
    monkeypatch.setattr(vu, "page_title", lambda url: "Amazon Bedrock AgentCore")
    blip = {"name": "AWS Bedrock AgentCore", "radar_url": "u", "page_title": "Amazon Bedrock AgentCore"}
    assert vu.check(blip) is None
    del blip["page_title"]
    assert "expected 'AWS Bedrock AgentCore'" in vu.check(blip)


def test_verify_urls_reports_quadrant_page_as_mismatch(monkeypatch):
    """An unknown slug returns the quadrant page, titled with the quadrant name."""
    vu = _verify_urls_module()
    monkeypatch.setattr(vu, "page_title", lambda url: "Languages & Frameworks")
    assert vu.check({"name": "TOON", "radar_url": "u"}) == (
        "TOON: page title is 'Languages & Frameworks', expected 'TOON'"
    )


def test_page_title_only_where_it_differs_from_name():
    """page_title is set only to record a difference from name, never as a copy of it."""
    for vol in _discover_volume_numbers():
        _, blips = _volume_files(vol)
        same = [b["name"] for b in blips if "page_title" in b and b["page_title"].lower() == b["name"].lower()]
        assert same == [], f"v{vol} page_title equals name: {same}"
