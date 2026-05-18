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
from datetime import datetime, timezone
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
    # since is ISO-8601 (Z-suffixed UTC), not "null", because a prior file
    # exists. Verify both the shape AND that the value actually corresponds
    # to the mtime we set — a regression that converted to local time would
    # still produce a Z-suffixed string but with the wrong value.
    m = re.search(
        r"^\s*since:\s*(\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}Z)\s*$",
        decision["reason"],
        re.MULTILINE,
    )
    assert m, decision["reason"]
    parsed = datetime.strptime(m.group(1), "%Y-%m-%dT%H:%M:%SZ").replace(
        tzinfo=timezone.utc
    )
    expected = datetime.fromtimestamp(twenty_five_hours, tz=timezone.utc)
    # The script formats with second precision; tolerate <2s drift from the
    # truncation + subprocess startup.
    drift = abs((parsed - expected).total_seconds())
    assert drift < 2, f"since={parsed} expected≈{expected} drift={drift}s"


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
    # The diagnostic now goes to the home-fallback log
    # (test_bad_stdin_logs_to_home_fallback covers the log content); stderr
    # stays empty.
    assert result.stderr == ""


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


# ---------- robustness (in-process) ----------
#
# These tests import the module directly so we can monkeypatch internals
# (Path.stat, log_diagnostic) — something subprocess tests cannot do. The
# subprocess tests above cover the stdin→stdout contract; these cover the
# narrow internal behaviors that the docstring claims load-bearing.


@pytest.fixture
def hook_module():
    sys.path.insert(0, str(SCRIPT.parent))
    try:
        import stop_learning_candidate as mod

        yield mod
    finally:
        sys.path.remove(str(SCRIPT.parent))


def test_latest_candidate_mtime_handles_empty_and_missing(tmp_path, hook_module):
    ghost_dir = tmp_path / "ghost"
    ghost_dir.mkdir()
    assert hook_module.latest_candidate_mtime(ghost_dir) is None
    assert hook_module.latest_candidate_mtime(tmp_path / "nope") is None


def test_latest_candidate_mtime_swallows_stat_race(tmp_path, monkeypatch, hook_module):
    """If `stat()` raises mid-scan, return the surviving mtimes, never propagate."""
    mem_dir = tmp_path / "memory"
    mem_dir.mkdir()
    survivor = mem_dir / "learning-candidate-2026-05-17.md"
    doomed = mem_dir / "learning-candidate-2026-05-16.md"
    survivor.write_text("")
    doomed.write_text("")
    survivor_mtime = time.time() - (25 * 60 * 60)
    os.utime(survivor, (survivor_mtime, survivor_mtime))

    real_stat = Path.stat

    def fake_stat(self, *a, **kw):
        if self.name == doomed.name:
            raise OSError("simulated disappearance between iterdir and stat")
        return real_stat(self, *a, **kw)

    monkeypatch.setattr(Path, "stat", fake_stat)

    result = hook_module.latest_candidate_mtime(mem_dir)
    assert result == pytest.approx(survivor_mtime, abs=1.0)


def test_latest_candidate_mtime_logs_when_all_stats_fail(tmp_path, monkeypatch, hook_module):
    """Pattern matched files but every stat() failed → log so a permissions
    storm is debuggable, and still return None (treated as no-candidate)."""
    mem_dir = tmp_path / "memory"
    mem_dir.mkdir()
    (mem_dir / "learning-candidate-2026-05-17.md").write_text("")
    (mem_dir / "learning-candidate-2026-05-16.md").write_text("")

    monkeypatch.setattr(
        Path,
        "stat",
        lambda self, *a, **kw: (_ for _ in ()).throw(PermissionError("denied")),
    )

    logged: list[tuple[Path | None, str]] = []
    monkeypatch.setattr(
        hook_module,
        "log_diagnostic",
        lambda mem, msg: logged.append((mem, msg)),
    )

    result = hook_module.latest_candidate_mtime(mem_dir)
    assert result is None
    assert len(logged) == 1
    assert "every stat() raised OSError" in logged[0][1]


def test_log_diagnostic_rotates_when_exceeds_cap(tmp_path, hook_module):
    """Pre-existing log over LOG_BYTE_CAP gets truncated; new line is the only
    content. Guards against a regression that drops rotation and lets the log
    grow unbounded under recurring crashes."""
    mem_dir = tmp_path / "memory"
    mem_dir.mkdir()
    log_path = mem_dir / ".karak-meta-hook.log"
    # Seed > LOG_BYTE_CAP bytes
    log_path.write_text("x" * (hook_module.LOG_BYTE_CAP + 10))
    assert log_path.stat().st_size > hook_module.LOG_BYTE_CAP

    hook_module.log_diagnostic(mem_dir, "post-rotation marker")

    content = log_path.read_text()
    # The old "xxxx…" payload must be gone; only the new line remains.
    assert "x" * 100 not in content
    assert "post-rotation marker" in content
    assert content.count("\n") == 1


def test_log_diagnostic_falls_back_to_home_when_mem_dir_is_none(tmp_path, monkeypatch, hook_module):
    """When the hook crashes before parsing cwd, log_diagnostic must still
    leave a breadcrumb at ~/.claude/karak-meta-hook.log — otherwise the most
    likely real-world failure modes (bad stdin, non-dict payload) leave no
    trace."""
    fake_home = tmp_path / "home"
    fake_home.mkdir()
    # Re-point the module-level constant at our temp home.
    fallback = fake_home / ".claude" / "karak-meta-hook.log"
    monkeypatch.setattr(hook_module, "HOME_FALLBACK_LOG", fallback)

    hook_module.log_diagnostic(None, "homeless diagnostic")

    assert fallback.exists()
    assert "homeless diagnostic" in fallback.read_text()


def test_unhandled_exception_logs_traceback(tmp_path, monkeypatch, hook_module):
    """Force a crash after mem_dir_for_log is set; assert main returns 0 AND
    the per-project log captures the traceback. The docstring promises both
    halves — exit 0 alone is not enough."""
    cwd = "/Users/x/proj"
    encoded = encoded_dir(tmp_path, cwd)
    monkeypatch.setenv("HOME", str(tmp_path))

    def boom(_mem_dir):
        raise RuntimeError("simulated post-cwd crash")

    monkeypatch.setattr(hook_module, "latest_candidate_mtime", boom)
    monkeypatch.setattr(
        "sys.stdin",
        _StringIOStdin(json.dumps({"cwd": cwd, "transcript_path": "/x/y.jsonl"})),
    )

    assert hook_module.main() == 0

    log_path = encoded / ".karak-meta-hook.log"
    assert log_path.exists(), "expected per-project log file"
    content = log_path.read_text()
    assert "simulated post-cwd crash" in content
    assert "unhandled exception" in content


def test_bad_stdin_logs_to_home_fallback(tmp_path, monkeypatch, hook_module):
    """Malformed JSON happens before cwd is parsed → must land in the
    home-rooted fallback log, not silently vanish."""
    fallback = tmp_path / ".claude" / "karak-meta-hook.log"
    monkeypatch.setattr(hook_module, "HOME_FALLBACK_LOG", fallback)
    monkeypatch.setattr("sys.stdin", _StringIOStdin("{not json"))

    rc = hook_module.main()
    assert rc == 0
    assert fallback.exists()
    assert "bad stdin" in fallback.read_text()


def test_non_dict_payload_logs_to_home_fallback(tmp_path, monkeypatch, hook_module):
    """Valid JSON but not an object (null, list, scalar) → bail before
    payload.get() would AttributeError, log to home fallback."""
    fallback = tmp_path / ".claude" / "karak-meta-hook.log"
    monkeypatch.setattr(hook_module, "HOME_FALLBACK_LOG", fallback)
    monkeypatch.setattr("sys.stdin", _StringIOStdin("null"))

    rc = hook_module.main()
    assert rc == 0
    assert fallback.exists()
    assert "not a JSON object" in fallback.read_text()


class _StringIOStdin:
    """Minimal stdin stand-in: we only need .read()."""

    def __init__(self, payload: str):
        self._payload = payload

    def read(self) -> str:
        return self._payload
