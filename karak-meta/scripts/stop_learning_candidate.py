#!/usr/bin/env python3
"""karak-meta Stop hook: gate the learning-candidate flow on a 24h cadence.

Reads Claude Code's Stop-hook JSON envelope from stdin and decides whether to
inject a one-line instruction telling the agent to run the
`record-learning-candidate` skill. The instruction includes:

  - the absolute transcript path (passed through from the hook input)
  - today's local date (YYYY-MM-DD)
  - the ISO-8601 timestamp of the most recent learning-candidate-*.md found in
    the project's auto-memory directory, or the literal string ``null`` if no
    prior record exists. The literal ``null`` is a sentinel the skill matches
    on; it is not JSON.

We fire if-and-only-if BOTH of the following hold:

  - ``stop_hook_active`` is falsy (otherwise we would infinite-loop), AND
  - either no learning-candidate-*.md file exists yet for this project, OR
    the most recent one has an mtime whose age is ≥ 24h.

The 24h check intentionally uses file mtime rather than parsing the date out of
the filename: filenames are local-date-bucketed and a date-rollover at 00:01
should NOT immediately trigger a second record. mtime gives us a rolling
window with an inclusive upper bound — exactly-24h-old fires.

Exit behavior:
  - Print the JSON decision to stdout, exit 0.
  - On unexpected errors, append a diagnostic line to the per-project log file
    (``~/.claude/projects/<encoded-cwd>/memory/.karak-meta-hook.log``) and
    exit 0 (a hook crash must never block the user's Stop). Claude Code drops
    stderr on exit 0, so the log file is the only diagnostic side-channel.
"""

from __future__ import annotations

import json
import os
import re
import sys
import traceback
from datetime import datetime, timezone
from pathlib import Path

WINDOW_SECONDS = 24 * 60 * 60
LOG_BYTE_CAP = 100 * 1024  # rotate the diagnostic log at ~100 KB


def encode_cwd(cwd: str) -> str:
    """Mirror Claude Code's project-dir encoding.

    Claude Code replaces every non-alphanumeric character in the absolute
    cwd with a single ``-``. Existing hyphens are preserved. Verified against
    real entries under ``~/.claude/projects/`` (e.g. ``/Volumes/Mac external
    HDD/Projects`` → ``-Volumes-Mac-external-HDD-Projects``). A leading ``/``
    yields a leading ``-``.
    """
    return re.sub(r"[^A-Za-z0-9]", "-", cwd)


def memory_dir(cwd: str) -> Path:
    home = Path(os.path.expanduser("~"))
    return home / ".claude" / "projects" / encode_cwd(cwd) / "memory"


def latest_candidate_mtime(mem_dir: Path) -> float | None:
    if not mem_dir.is_dir():
        return None
    pattern = re.compile(r"^learning-candidate-\d{4}-\d{2}-\d{2}\.md$")
    mtimes: list[float] = []
    for p in mem_dir.iterdir():
        if not pattern.match(p.name):
            continue
        try:
            mtimes.append(p.stat().st_mtime)
        except OSError:
            # File disappeared between iterdir() and stat() — concurrent
            # cleanup or another session rewriting. Losing one file's mtime
            # is harmless; dropping the whole computation would drop the
            # breadcrumb.
            continue
    return max(mtimes) if mtimes else None


def build_reason(transcript_path: str, today: str, since_iso: str | None) -> str:
    since_clause = since_iso if since_iso else "null"
    return (
        "The karak-meta Stop hook fired its 24h learning-candidate gate. "
        "Use the `record-learning-candidate` skill to log a one-line pointer "
        "to the current session into auto-memory.\n\n"
        f"  transcript_path: {transcript_path}\n"
        f"  date: {today}\n"
        f"  since: {since_clause}\n\n"
        "Extract ≤31-char grep keywords from this session, write "
        f"`learning-candidate-{today}.md`, and update `MEMORY.md`. "
        "Keep the memory body to the four-bullet template — this is a "
        "breadcrumb, not a journal."
    )


def log_diagnostic(mem_dir: Path | None, message: str) -> None:
    """Append a diagnostic line to the per-project hook log.

    Never raises. The hook is silent-by-design under Claude Code (stderr is
    dropped on exit 0); this file is the only place a user can grep for
    "why didn't my hook fire today?".
    """
    if mem_dir is None:
        return
    try:
        mem_dir.mkdir(parents=True, exist_ok=True)
        log_path = mem_dir / ".karak-meta-hook.log"
        if log_path.exists() and log_path.stat().st_size > LOG_BYTE_CAP:
            # Truncate; lose old context to keep the file bounded.
            log_path.write_text("")
        ts = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
        with log_path.open("a", encoding="utf-8") as fh:
            fh.write(f"{ts} {message}\n")
    except OSError:
        # Last-resort: swallow. We cannot let the diagnostic path itself
        # crash the hook.
        pass


def main() -> int:
    mem_dir_for_log: Path | None = None
    try:
        try:
            raw = sys.stdin.read()
            if not raw.strip():
                return 0
            payload = json.loads(raw)
        except (json.JSONDecodeError, OSError) as exc:
            print(f"karak-meta stop hook: bad stdin: {exc}", file=sys.stderr)
            return 0

        # Loop guard: if Claude already ran us once this turn and blocked, do
        # not block again — that produces an infinite stop/block ping-pong.
        if payload.get("stop_hook_active"):
            return 0

        cwd = payload.get("cwd")
        if not cwd:
            # Malformed envelope. Do not guess with os.getcwd() — that would
            # mis-file the breadcrumb under whatever directory python3 was
            # spawned from.
            return 0

        transcript_path = payload.get("transcript_path")
        if not transcript_path:
            # Without a transcript path the skill has nothing useful to record.
            return 0

        mem_dir = memory_dir(cwd)
        mem_dir_for_log = mem_dir
        mtime = latest_candidate_mtime(mem_dir)
        now = datetime.now(timezone.utc).timestamp()

        if mtime is not None and (now - mtime) < WINDOW_SECONDS:
            # Within the 24h window — stay silent.
            return 0

        today_local = datetime.now().astimezone().strftime("%Y-%m-%d")
        since_iso = (
            datetime.fromtimestamp(mtime, tz=timezone.utc)
            .strftime("%Y-%m-%dT%H:%M:%SZ")
            if mtime is not None
            else None
        )

        decision = {
            "decision": "block",
            "reason": build_reason(transcript_path, today_local, since_iso),
        }
        json.dump(decision, sys.stdout)
        sys.stdout.write("\n")
        return 0
    except Exception:  # noqa: BLE001 — boundary swallow, see docstring
        # Honor the contract: a hook crash must never block the user's Stop.
        # Surface the traceback to the per-project log so a user with the
        # diagnosis question has somewhere to look.
        log_diagnostic(
            mem_dir_for_log,
            "unhandled exception:\n" + traceback.format_exc(),
        )
        return 0


if __name__ == "__main__":
    sys.exit(main())
