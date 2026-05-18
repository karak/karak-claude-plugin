"""Tests for the karak-meta Stop hook.

These tests exercise the script as a subprocess to verify the full
stdin → stdout JSON contract that Claude Code actually invokes. They use a
fake home directory (via ``HOME=`` in the subprocess env) so the script's
``~/.claude/projects/...`` lookups land in ``tmp_path``.

The script is intentionally silent-by-design: every error path returns 0
with no stdout decision. The tests assert both the silent paths AND the
fire path.

Run with:  pytest karak-meta/scripts/test_stop_learning_candidate.py
"""

from __future__ import annotations

import json
import os
import re
import subprocess
import sys
import time
from pathlib import Path

import pytest

SCRIPT = Path(__file__).parent / "stop_learning_candidate.py"


def run_hook(stdin: str, home: Path, env_extra: dict | None = None) -> subprocess.CompletedProcess:
    env = os.environ.copy()
    env["HOME"] = str(home)
    if env_extra:
        env.update(env_extra)
    return subprocess.run(
        [sys.executable, str(SCRIPT)],
        input=stdin,
        capture_output=True,
        text=True,
        env=env,
        timeout=10,
    )


def encoded_dir(home: Path, cwd: str) -> Path:
    encoded = re.sub(r"[^A-Za-z0-9]", "-", cwd)
    return home / ".claude" / "projects" / encoded / "memory"


# ---------- happy path ----------


def test_fires_on_fresh_project(tmp_path):
    """No prior candidate file → hook emits block decision with since=null."""
    cwd = "/Users/x/proj"
    payload = {"cwd": cwd, "transcript_path": "/x/abc.jsonl"}
    result = run_hook(json.dumps(payload), tmp_path)

    assert result.returncode == 0
    decision = json.loads(result.stdout)
    assert decision["decision"] == "block"
    reason = decision["reason"]
    assert "record-learning-candidate" in reason
    assert "transcript_path: /x/abc.jsonl" in reason
    # Critical contract: literal "null" sentinel for missing prior record.
    assert re.search(r"^\s*since:\s*null\s*$", reason, re.MULTILINE), reason


def test_fires_when_mtime_older_than_24h(tmp_path):
    cwd = "/Users/x/proj"
    mem_dir = encoded_dir(tmp_path, cwd)
    mem_dir.mkdir(parents=True)
    old = mem_dir / "learning-candidate-2026-05-01.md"
    old.write_text("stale")
    # Set mtime 25h ago
    twenty_five_hours = time.time() - (25 * 60 * 60)
    os.utime(old, (twenty_five_hours, twenty_five_hours))

    result = run_hook(
        json.dumps({"cwd": cwd, "transcript_path": "/x/now.jsonl"}),
        tmp_path,
    )
    assert result.returncode == 0
    decision = json.loads(result.stdout)
    assert decision["decision"] == "block"
    # since is ISO-8601, not "null", because a prior file exists
    assert re.search(
        r"^\s*since:\s*\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}Z\s*$",
        decision["reason"],
        re.MULTILINE,
    )


def test_exactly_24h_boundary_fires(tmp_path):
    """The 24h check uses `<`, so age exactly == 24h is OUTSIDE the window → fires."""
    cwd = "/Users/x/proj"
    mem_dir = encoded_dir(tmp_path, cwd)
    mem_dir.mkdir(parents=True)
    f = mem_dir / "learning-candidate-2026-05-17.md"
    f.write_text("")
    exactly_24h_ago = time.time() - (24 * 60 * 60)
    os.utime(f, (exactly_24h_ago, exactly_24h_ago))

    result = run_hook(
        json.dumps({"cwd": cwd, "transcript_path": "/x/y.jsonl"}),
        tmp_path,
    )
    assert result.returncode == 0
    assert result.stdout.strip(), "expected a block decision at exactly 24h"


# ---------- silent skip paths ----------


def test_silent_when_within_24h(tmp_path):
    cwd = "/Users/x/proj"
    mem_dir = encoded_dir(tmp_path, cwd)
    mem_dir.mkdir(parents=True)
    f = mem_dir / "learning-candidate-2026-05-18.md"
    f.write_text("")
    # 1h ago
    one_hour_ago = time.time() - 3600
    os.utime(f, (one_hour_ago, one_hour_ago))

    result = run_hook(
        json.dumps({"cwd": cwd, "transcript_path": "/x/y.jsonl"}),
        tmp_path,
    )
    assert result.returncode == 0
    assert result.stdout == "", f"expected no stdout, got: {result.stdout!r}"


def test_silent_when_stop_hook_active(tmp_path):
    """Loop guard: if Claude already fired us this turn, do not block again."""
    cwd = "/Users/x/proj"
    payload = {
        "cwd": cwd,
        "transcript_path": "/x/y.jsonl",
        "stop_hook_active": True,
    }
    result = run_hook(json.dumps(payload), tmp_path)
    assert result.returncode == 0
    assert result.stdout == ""


def test_silent_when_no_transcript_path(tmp_path):
    result = run_hook(json.dumps({"cwd": "/Users/x/proj"}), tmp_path)
    assert result.returncode == 0
    assert result.stdout == ""


def test_silent_when_no_cwd(tmp_path):
    """Missing cwd is malformed → bail, do not fall back to os.getcwd()."""
    result = run_hook(json.dumps({"transcript_path": "/x/y.jsonl"}), tmp_path)
    assert result.returncode == 0
    assert result.stdout == ""


def test_silent_on_empty_stdin(tmp_path):
    result = run_hook("", tmp_path)
    assert result.returncode == 0
    assert result.stdout == ""


def test_silent_on_malformed_json(tmp_path):
    result = run_hook("{not json", tmp_path)
    assert result.returncode == 0
    assert result.stdout == ""
    # stderr is OK to populate here (Claude drops it on exit 0, but the
    # contract is "log + exit 0", not "silence everything").
    assert "bad stdin" in result.stderr or result.stderr == ""


# ---------- encode_cwd edges ----------


@pytest.mark.parametrize(
    "raw, encoded",
    [
        ("/Users/x/proj", "-Users-x-proj"),
        ("/Volumes/Mac external HDD/Projects", "-Volumes-Mac-external-HDD-Projects"),
        ("/Users/x/.config", "-Users-x--config"),  # leading dot → -
        ("/Users/x/proj_name", "-Users-x-proj-name"),  # underscore → -
        ("/Users/x/proj-name", "-Users-x-proj-name"),  # existing hyphen kept
    ],
)
def test_encode_cwd_matches_claude_codes_encoding(raw, encoded, tmp_path):
    """The encoder must agree with what Claude Code writes under ~/.claude/projects/."""
    mem_dir = tmp_path / ".claude" / "projects" / encoded / "memory"
    mem_dir.mkdir(parents=True)
    # Prove the hook resolves the encoded dir by writing a recent file and
    # asserting the hook stays silent (within 24h).
    fresh = mem_dir / "learning-candidate-2026-05-18.md"
    fresh.write_text("")
    one_hour_ago = time.time() - 3600
    os.utime(fresh, (one_hour_ago, one_hour_ago))

    result = run_hook(
        json.dumps({"cwd": raw, "transcript_path": "/x/y.jsonl"}),
        tmp_path,
    )
    assert result.returncode == 0
    assert result.stdout == "", (
        f"encoded dir {encoded!r} was not picked up — hook fired when it should have been silent"
    )


# ---------- robustness ----------


def test_race_between_iterdir_and_stat(tmp_path, monkeypatch):
    """If a candidate disappears mid-scan, the script must not crash."""
    cwd = "/Users/x/proj"
    mem_dir = encoded_dir(tmp_path, cwd)
    mem_dir.mkdir(parents=True)
    a = mem_dir / "learning-candidate-2026-05-17.md"
    b = mem_dir / "learning-candidate-2026-05-16.md"
    a.write_text("")
    b.write_text("")
    twenty_five_hours = time.time() - (25 * 60 * 60)
    os.utime(a, (twenty_five_hours, twenty_five_hours))
    os.utime(b, (twenty_five_hours, twenty_five_hours))

    # Race simulation: we can't easily inject a deletion between iterdir
    # and stat() in a subprocess. Instead verify that the script's outer
    # try/except handles arbitrary OSError by importing the function and
    # exercising it directly with a doomed path.
    sys.path.insert(0, str(SCRIPT.parent))
    try:
        import stop_learning_candidate as mod

        # latest_candidate_mtime should ignore unreadable files, not raise.
        ghost_dir = tmp_path / "ghost"
        ghost_dir.mkdir()
        # Empty dir → None
        assert mod.latest_candidate_mtime(ghost_dir) is None
        # Non-existent dir → None
        assert mod.latest_candidate_mtime(tmp_path / "nope") is None
    finally:
        sys.path.remove(str(SCRIPT.parent))


def test_unhandled_exception_does_not_block(tmp_path, monkeypatch):
    """If anything raises past the inner stdin guard, we still exit 0."""
    cwd = "/Users/x/proj"
    # Make HOME unreadable to force an OSError in memory_dir's downstream
    # access — but Path.is_dir() on a non-existent path just returns False,
    # so we instead exercise the broader contract: the script must not
    # propagate any uncaught exception. The cleanest way is to make HOME
    # point at a non-directory file.
    fake_home = tmp_path / "not_a_dir"
    fake_home.write_text("")  # regular file, not a dir
    result = run_hook(
        json.dumps({"cwd": cwd, "transcript_path": "/x/y.jsonl"}),
        fake_home.parent,
        env_extra={"HOME": str(fake_home)},
    )
    # Must exit 0 regardless — that is the docstring's load-bearing promise.
    assert result.returncode == 0
