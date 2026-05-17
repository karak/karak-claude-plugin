#!/usr/bin/env python3
"""karak-meta Stop hook: gate the learning-candidate flow on a 24h cadence.

Reads Claude Code's Stop-hook JSON envelope from stdin and decides whether to
inject a one-line instruction telling the agent to run the
`record-learning-candidate` skill. The instruction includes:

  - the absolute transcript path (passed through from the hook input)
  - today's local date (YYYY-MM-DD)
  - the ISO-8601 timestamp of the most recent learning-candidate-*.md found in
    the project's auto-memory directory (or `null` if none).

We fire if-and-only-if:
  - `stop_hook_active` is falsy (otherwise we would infinite-loop), AND
  - no learning-candidate-*.md file exists yet for this project, OR the most
    recent one has an mtime older than 24h.

The 24h check intentionally uses file mtime rather than parsing the date out of
the filename: filenames are local-date-bucketed and a date-rollover at 00:01
should NOT immediately trigger a second record. mtime gives us a strict
rolling window.

Exit behavior:
  - Print the JSON decision to stdout, exit 0.
  - On unexpected errors, log to stderr and exit 0 (a hook crash must never
    block the user's Stop).
"""

from __future__ import annotations

import json
import os
import re
import sys
from datetime import datetime, timezone
from pathlib import Path

WINDOW_SECONDS = 24 * 60 * 60


def encode_cwd(cwd: str) -> str:
    """Mirror Claude Code's project-dir encoding: '/foo/bar' -> '-foo-bar'."""
    return "-" + cwd.lstrip("/").replace("/", "-")


def memory_dir(cwd: str) -> Path:
    home = Path(os.path.expanduser("~"))
    return home / ".claude" / "projects" / encode_cwd(cwd) / "memory"


def latest_candidate_mtime(mem_dir: Path) -> float | None:
    if not mem_dir.is_dir():
        return None
    pattern = re.compile(r"^learning-candidate-\d{4}-\d{2}-\d{2}\.md$")
    candidates = [p for p in mem_dir.iterdir() if pattern.match(p.name)]
    if not candidates:
        return None
    return max(p.stat().st_mtime for p in candidates)


def build_reason(transcript_path: str, today: str, since_iso: str | None) -> str:
    since_clause = since_iso if since_iso else "null (no prior record found)"
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


def main() -> int:
    try:
        raw = sys.stdin.read()
        if not raw.strip():
            return 0
        payload = json.loads(raw)
    except (json.JSONDecodeError, OSError) as exc:
        print(f"karak-meta stop hook: bad stdin: {exc}", file=sys.stderr)
        return 0

    # Loop guard: if Claude already ran us once this turn and blocked, do not
    # block again — that produces an infinite stop/block ping-pong.
    if payload.get("stop_hook_active"):
        return 0

    cwd = payload.get("cwd") or os.getcwd()
    transcript_path = payload.get("transcript_path")
    if not transcript_path:
        # Without a transcript path the skill has nothing useful to record.
        return 0

    mem_dir = memory_dir(cwd)
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


if __name__ == "__main__":
    sys.exit(main())
