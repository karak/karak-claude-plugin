#!/usr/bin/env python3
"""Manage codex review session IDs.

Usage:
    python3 session_manager.py save   <target> <session_id> <description>
    python3 session_manager.py lookup <target>
    python3 session_manager.py list
    python3 session_manager.py delete <target>

Environment:
    CODEX_SESSIONS_DIR  Override the directory for codex-sessions.md
"""
import os
import re
import sys
from datetime import date

SESSIONS_FILENAME = "codex-sessions.md"

# Entry format: - <target>: <session_id> (<date>, <description>)
ENTRY_RE = re.compile(r"^- (.+?): (\S+) \((\d{4}-\d{2}-\d{2}), (.+)\)$")


def _sessions_path():
    d = os.environ.get("CODEX_SESSIONS_DIR", "")
    if not d:
        print("Error: CODEX_SESSIONS_DIR not set", file=sys.stderr)
        sys.exit(1)
    return os.path.join(d, SESSIONS_FILENAME)


def _read_entries(path):
    """Return list of (target, session_id, date_str, description) tuples."""
    if not os.path.exists(path):
        return []
    entries = []
    with open(path) as f:
        for line in f:
            m = ENTRY_RE.match(line.strip())
            if m:
                entries.append((m.group(1), m.group(2), m.group(3), m.group(4)))
    return entries


def _write_entries(path, entries):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w") as f:
        f.write("# Codex Review Sessions\n")
        for target, sid, d, desc in entries:
            f.write(f"- {target}: {sid} ({d}, {desc})\n")


def cmd_save(args):
    if len(args) < 3:
        print("Usage: session_manager.py save <target> <session_id> <description>", file=sys.stderr)
        sys.exit(1)
    target, session_id, description = args[0], args[1], args[2]
    path = _sessions_path()
    entries = _read_entries(path)
    # Update existing or append
    updated = False
    new_entries = []
    for t, sid, d, desc in entries:
        if t == target:
            new_entries.append((target, session_id, date.today().isoformat(), description))
            updated = True
        else:
            new_entries.append((t, sid, d, desc))
    if not updated:
        new_entries.append((target, session_id, date.today().isoformat(), description))
    _write_entries(path, new_entries)
    print(f"Saved: {target} -> {session_id}")


def cmd_lookup(args):
    if len(args) < 1:
        print("Usage: session_manager.py lookup <target>", file=sys.stderr)
        sys.exit(1)
    target = args[0]
    path = _sessions_path()
    entries = _read_entries(path)
    for t, sid, d, desc in entries:
        if t == target:
            print(sid)
            return
    print(f"Error: no session found for target: {target}", file=sys.stderr)
    sys.exit(1)


def cmd_list(args):
    path = _sessions_path()
    entries = _read_entries(path)
    if not entries:
        print("No sessions found", file=sys.stderr)
        sys.exit(1)
    for target, sid, d, desc in entries:
        print(f"- {target}: {sid} ({d}, {desc})")


def cmd_delete(args):
    if len(args) < 1:
        print("Usage: session_manager.py delete <target>", file=sys.stderr)
        sys.exit(1)
    target = args[0]
    path = _sessions_path()
    entries = _read_entries(path)
    new_entries = [(t, sid, d, desc) for t, sid, d, desc in entries if t != target]
    if len(new_entries) == len(entries):
        print(f"Error: no session found for target: {target}", file=sys.stderr)
        sys.exit(1)
    _write_entries(path, new_entries)
    print(f"Deleted: {target}")


COMMANDS = {
    "save": cmd_save,
    "lookup": cmd_lookup,
    "list": cmd_list,
    "delete": cmd_delete,
}


def main():
    if len(sys.argv) < 2 or sys.argv[1] not in COMMANDS:
        print(f"Usage: session_manager.py <{'|'.join(COMMANDS)}> [args...]", file=sys.stderr)
        sys.exit(1)
    COMMANDS[sys.argv[1]](sys.argv[2:])


if __name__ == "__main__":
    main()
