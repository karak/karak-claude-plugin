#!/usr/bin/env python3
"""Extract session ID from codex JSONL output AND save it in one step.

Usage:
    python3 extract_and_save_session.py <jsonl_file> <target> <description>
    cat output.jsonl | python3 extract_and_save_session.py - <target> <description>

Environment:
    CODEX_SESSIONS_DIR  Directory for codex-sessions.md
"""
import json
import os
import re
import sys
from datetime import date

SESSIONS_FILENAME = "codex-sessions.md"
ENTRY_RE = re.compile(r"^- (.+?): (\S+) \((\d{4}-\d{2}-\d{2}), (.+)\)$")


def extract_thread_id(lines):
    for line in lines:
        line = line.strip()
        if not line:
            continue
        try:
            evt = json.loads(line)
        except json.JSONDecodeError:
            continue
        if evt.get("type") == "thread.started" and "thread_id" in evt:
            return evt["thread_id"]
    return None


def save_session(target, session_id, description):
    d = os.environ.get("CODEX_SESSIONS_DIR", "")
    if not d:
        print("Warning: CODEX_SESSIONS_DIR not set, skipping save", file=sys.stderr)
        return
    path = os.path.join(d, SESSIONS_FILENAME)
    entries = []
    if os.path.exists(path):
        with open(path) as f:
            for line in f:
                m = ENTRY_RE.match(line.strip())
                if m:
                    entries.append((m.group(1), m.group(2), m.group(3), m.group(4)))
    updated = False
    new_entries = []
    for t, sid, dt, desc in entries:
        if t == target:
            new_entries.append((target, session_id, date.today().isoformat(), description))
            updated = True
        else:
            new_entries.append((t, sid, dt, desc))
    if not updated:
        new_entries.append((target, session_id, date.today().isoformat(), description))
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w") as f:
        f.write("# Codex Review Sessions\n")
        for t, sid, dt, desc in new_entries:
            f.write(f"- {t}: {sid} ({dt}, {desc})\n")


def main():
    if len(sys.argv) < 4:
        print("Usage: extract_and_save_session.py <jsonl_file|-> <target> <description>", file=sys.stderr)
        sys.exit(1)

    path, target, description = sys.argv[1], sys.argv[2], sys.argv[3]
    lines = sys.stdin if path == "-" else open(path)

    thread_id = extract_thread_id(lines)
    if thread_id is None:
        print("Error: no thread.started event found", file=sys.stderr)
        sys.exit(1)

    save_session(target, thread_id, description)
    print(thread_id)


if __name__ == "__main__":
    main()
