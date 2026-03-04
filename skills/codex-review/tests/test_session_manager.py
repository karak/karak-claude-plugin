#!/usr/bin/env python3
"""Tests for session_manager.py"""
import os
import subprocess
import sys
import tempfile
import unittest

SCRIPT = os.path.join(os.path.dirname(__file__), '..', 'scripts', 'session_manager.py')


class TestSessionManager(unittest.TestCase):

    def setUp(self):
        self.tmpdir = tempfile.mkdtemp()
        self.env = {**os.environ, 'CODEX_SESSIONS_DIR': self.tmpdir}
        self.sessions_file = os.path.join(self.tmpdir, 'codex-sessions.md')

    def tearDown(self):
        import shutil
        shutil.rmtree(self.tmpdir, ignore_errors=True)

    def _run(self, *args):
        result = subprocess.run(
            [sys.executable, SCRIPT, *args],
            capture_output=True, text=True, env=self.env,
        )
        return result.stdout.strip(), result.stderr.strip(), result.returncode

    # --- save ---

    def test_save_creates_file_and_entry(self):
        _, _, rc = self._run('save', 'feature/auth', '019cb904-2065-7fa1-9202-84f133d1ba4d', 'Initial review')
        self.assertEqual(rc, 0)
        self.assertTrue(os.path.exists(self.sessions_file))
        with open(self.sessions_file) as f:
            content = f.read()
        self.assertIn('019cb904-2065-7fa1-9202-84f133d1ba4d', content)
        self.assertIn('feature/auth', content)
        self.assertIn('Initial review', content)

    def test_save_appends_second_entry(self):
        self._run('save', 'feature/a', 'id-aaa', 'First')
        self._run('save', 'feature/b', 'id-bbb', 'Second')
        with open(self.sessions_file) as f:
            content = f.read()
        entry_lines = [l for l in content.splitlines() if l.startswith('- ')]
        self.assertEqual(len(entry_lines), 2)

    def test_save_updates_existing_target(self):
        self._run('save', 'feature/auth', 'old-id', 'Old review')
        self._run('save', 'PR#42', 'pr-id', 'PR review')
        self._run('save', 'feature/auth', 'new-id', 'New review')
        # Should have 2 entries, not 3
        with open(self.sessions_file) as f:
            content = f.read()
        entry_lines = [l for l in content.splitlines() if l.startswith('- ')]
        self.assertEqual(len(entry_lines), 2)
        # Lookup should return new ID
        stdout, _, _ = self._run('lookup', 'feature/auth')
        self.assertEqual(stdout, 'new-id')

    def test_save_missing_args(self):
        _, _, rc = self._run('save', 'target-only')
        self.assertNotEqual(rc, 0)

    # --- lookup ---

    def test_lookup_existing(self):
        self._run('save', 'main', 'session-abc', 'Review main')
        stdout, _, rc = self._run('lookup', 'main')
        self.assertEqual(rc, 0)
        self.assertEqual(stdout, 'session-abc')

    def test_lookup_nonexistent(self):
        self._run('save', 'main', 'session-abc', 'Review main')
        _, _, rc = self._run('lookup', 'nonexistent')
        self.assertNotEqual(rc, 0)

    def test_lookup_no_file(self):
        _, _, rc = self._run('lookup', 'anything')
        self.assertNotEqual(rc, 0)

    # --- list ---

    def test_list_shows_all_sessions(self):
        self._run('save', 'feature/a', 'id-aaa', 'Feature A')
        self._run('save', 'feature/b', 'id-bbb', 'Feature B')
        stdout, _, rc = self._run('list')
        self.assertEqual(rc, 0)
        self.assertIn('feature/a', stdout)
        self.assertIn('feature/b', stdout)

    def test_list_empty(self):
        _, _, rc = self._run('list')
        self.assertNotEqual(rc, 0)

    # --- delete ---

    def test_delete_removes_target(self):
        self._run('save', 'to-delete', 'id-del', 'Will delete')
        self._run('save', 'to-keep', 'id-keep', 'Will keep')
        _, _, rc = self._run('delete', 'to-delete')
        self.assertEqual(rc, 0)
        _, _, rc = self._run('lookup', 'to-delete')
        self.assertNotEqual(rc, 0)
        stdout, _, _ = self._run('lookup', 'to-keep')
        self.assertEqual(stdout, 'id-keep')

    def test_delete_nonexistent(self):
        _, _, rc = self._run('delete', 'nonexistent')
        self.assertNotEqual(rc, 0)

    # --- invalid usage ---

    def test_no_command(self):
        _, _, rc = self._run()
        self.assertNotEqual(rc, 0)

    def test_unknown_command(self):
        _, _, rc = self._run('unknown')
        self.assertNotEqual(rc, 0)


if __name__ == '__main__':
    unittest.main()
