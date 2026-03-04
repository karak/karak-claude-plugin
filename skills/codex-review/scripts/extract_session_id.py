#!/usr/bin/env python3
"""Extract session ID (thread_id) from codex exec --json JSONL output.

Usage:
    python3 extract_session_id.py <jsonl_file>
    python3 extract_session_id.py -              # read from stdin
"""
import json
import sys


def extract(lines):
    """Return thread_id from the first thread.started event, or None."""
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


def main():
    if len(sys.argv) < 2:
        print("Usage: extract_session_id.py <jsonl_file | ->", file=sys.stderr)
        sys.exit(1)

    path = sys.argv[1]
    if path == "-":
        lines = sys.stdin
    else:
        try:
            lines = open(path)
        except FileNotFoundError:
            print(f"Error: file not found: {path}", file=sys.stderr)
            sys.exit(1)

    thread_id = extract(lines)
    if thread_id is None:
        print("Error: no thread.started event found", file=sys.stderr)
        sys.exit(1)

    print(thread_id)


if __name__ == "__main__":
    main()
