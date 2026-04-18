#!/usr/bin/env python3
"""Build a codex CLI command with proper model specification.

Avoids the model refresh hang in codex-cli 0.111.0+ by explicitly
specifying the model via -m flag (default: gpt-5.4).
"""
import argparse
import os
import shlex
import sys


DEFAULT_MODEL = "gpt-5.4"
RECOMMENDED_TIMEOUT_MS = 180000  # minimum Bash tool timeout to avoid hang
SCRIPTS_DIR = os.path.dirname(os.path.abspath(__file__))


def build_command(prompt, model=None, target=None, description=None):
    """Build the full codex exec command string."""
    m = model or DEFAULT_MODEL
    parts = [
        "codex exec",
        "--json",
        "--sandbox danger-full-access",
        f"-m {shlex.quote(m)}",
        shlex.quote(prompt),
    ]
    cmd = " ".join(parts)

    # Always tee the JSONL output
    cmd += " 2>&1 | tee /tmp/codex-review-output.jsonl"

    # If target and description are given, pipe through extract_and_save_session
    if bool(target) != bool(description):
        print(
            "Warning: --target and --description must be provided together; extract pipeline omitted.",
            file=sys.stderr,
        )
    if target and description:
        extract_script = os.path.join(SCRIPTS_DIR, "extract_and_save_session.py")
        cmd += (
            f" | python3 {extract_script}"
            f" - {shlex.quote(target)} {shlex.quote(description)}"
        )

    return cmd


def main():
    parser = argparse.ArgumentParser(description="Build codex review command")
    parser.add_argument("--prompt", required=True, help="Review prompt text")
    parser.add_argument("--model", default=None, help=f"Model to use (default: {DEFAULT_MODEL})")
    parser.add_argument("--target", default=None, help="Review target (branch/PR)")
    parser.add_argument("--description", default=None, help="Session description")
    args = parser.parse_args()

    cmd = build_command(args.prompt, args.model, args.target, args.description)
    print(cmd)


if __name__ == "__main__":
    main()
