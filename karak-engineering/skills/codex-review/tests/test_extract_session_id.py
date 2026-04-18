#!/usr/bin/env python3
"""Tests for extract_session_id.py"""
import json
import os
import subprocess
import sys
import tempfile
import unittest

SCRIPT = os.path.join(os.path.dirname(__file__), '..', 'scripts', 'extract_session_id.py')


class TestExtractSessionId(unittest.TestCase):

    def _run(self, *args, stdin_data=None):
        """Run the script and return (stdout, stderr, returncode)."""
        result = subprocess.run(
            [sys.executable, SCRIPT, *args],
            capture_output=True, text=True,
            input=stdin_data,
        )
        return result.stdout.strip(), result.stderr.strip(), result.returncode

    def _write_jsonl(self, lines):
        """Write JSONL lines to a temp file and return its path."""
        f = tempfile.NamedTemporaryFile(mode='w', suffix='.jsonl', delete=False)
        for line in lines:
            f.write(json.dumps(line) + '\n')
        f.close()
        return f.name

    def test_extracts_thread_id_from_valid_jsonl(self):
        path = self._write_jsonl([
            {"type": "thread.started", "thread_id": "019cb904-2065-7fa1-9202-84f133d1ba4d"},
            {"type": "turn.started"},
            {"type": "item.completed", "item": {"id": "item_0", "type": "reasoning"}},
            {"type": "turn.completed", "usage": {"input_tokens": 100}},
        ])
        stdout, _, rc = self._run(path)
        os.unlink(path)
        self.assertEqual(rc, 0)
        self.assertEqual(stdout, "019cb904-2065-7fa1-9202-84f133d1ba4d")

    def test_exits_nonzero_without_args(self):
        _, _, rc = self._run()
        self.assertNotEqual(rc, 0)

    def test_exits_nonzero_for_missing_file(self):
        _, _, rc = self._run('/tmp/nonexistent_codex_review_test.jsonl')
        self.assertNotEqual(rc, 0)

    def test_exits_nonzero_when_no_thread_started_event(self):
        path = self._write_jsonl([
            {"type": "turn.started"},
            {"type": "item.completed", "item": {"id": "item_0"}},
        ])
        _, _, rc = self._run(path)
        os.unlink(path)
        self.assertNotEqual(rc, 0)

    def test_exits_nonzero_for_empty_file(self):
        f = tempfile.NamedTemporaryFile(mode='w', suffix='.jsonl', delete=False)
        f.close()
        _, _, rc = self._run(f.name)
        os.unlink(f.name)
        self.assertNotEqual(rc, 0)

    def test_extracts_different_uuid(self):
        path = self._write_jsonl([
            {"type": "thread.started", "thread_id": "aaaaaaaa-bbbb-cccc-dddd-eeeeeeeeeeee"},
        ])
        stdout, _, rc = self._run(path)
        os.unlink(path)
        self.assertEqual(rc, 0)
        self.assertEqual(stdout, "aaaaaaaa-bbbb-cccc-dddd-eeeeeeeeeeee")

    def test_output_is_single_line(self):
        path = self._write_jsonl([
            {"type": "thread.started", "thread_id": "019cb904-2065-7fa1-9202-84f133d1ba4d"},
            {"type": "turn.completed", "usage": {}},
        ])
        stdout, _, _ = self._run(path)
        os.unlink(path)
        self.assertEqual(len(stdout.splitlines()), 1)

    def test_reads_from_stdin_when_dash_argument(self):
        jsonl = json.dumps({"type": "thread.started", "thread_id": "stdin-uuid-1234"}) + '\n'
        stdout, _, rc = self._run('-', stdin_data=jsonl)
        self.assertEqual(rc, 0)
        self.assertEqual(stdout, "stdin-uuid-1234")


if __name__ == '__main__':
    unittest.main()
