"""Tests for extract_and_save_session.py — combined extract + save pipeline."""
import os
import subprocess
import sys
import tempfile
import unittest

SCRIPT = os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
    "scripts",
    "extract_and_save_session.py",
)

VALID_JSONL = (
    '{"type":"thread.started","thread_id":"abc-123-def"}\n'
    '{"type":"item.completed","item":{"type":"agent_message","text":"review"}}\n'
)

NO_THREAD_JSONL = '{"type":"item.completed","item":{"type":"agent_message","text":"hi"}}\n'


class TestExtractAndSaveSession(unittest.TestCase):
    def setUp(self):
        self.tmpdir = tempfile.mkdtemp()
        self.sessions_dir = os.path.join(self.tmpdir, "memory")
        os.makedirs(self.sessions_dir)
        self.env = {**os.environ, "CODEX_SESSIONS_DIR": self.sessions_dir}

    def _run(self, args, stdin_data=None):
        return subprocess.run(
            [sys.executable, SCRIPT] + args,
            input=stdin_data,
            capture_output=True,
            text=True,
            env=self.env,
        )

    def _sessions_content(self):
        path = os.path.join(self.sessions_dir, "codex-sessions.md")
        if not os.path.exists(path):
            return None
        with open(path) as f:
            return f.read()

    # --- Success cases ---

    def test_extracts_and_saves_from_file(self):
        jsonl_path = os.path.join(self.tmpdir, "output.jsonl")
        with open(jsonl_path, "w") as f:
            f.write(VALID_JSONL)

        result = self._run([jsonl_path, "feature/login", "Login review"])
        self.assertEqual(result.returncode, 0)
        self.assertEqual(result.stdout.strip(), "abc-123-def")

        content = self._sessions_content()
        self.assertIn("feature/login", content)
        self.assertIn("abc-123-def", content)
        self.assertIn("Login review", content)

    def test_extracts_and_saves_from_stdin(self):
        result = self._run(["-", "PR-42", "PR review"], stdin_data=VALID_JSONL)
        self.assertEqual(result.returncode, 0)
        self.assertEqual(result.stdout.strip(), "abc-123-def")

        content = self._sessions_content()
        self.assertIn("PR-42", content)
        self.assertIn("abc-123-def", content)

    def test_updates_existing_target(self):
        jsonl1 = (
            '{"type":"thread.started","thread_id":"old-session-id"}\n'
        )
        jsonl2 = (
            '{"type":"thread.started","thread_id":"new-session-id"}\n'
        )
        self._run(["-", "main", "first"], stdin_data=jsonl1)
        result = self._run(["-", "main", "second"], stdin_data=jsonl2)

        self.assertEqual(result.returncode, 0)
        self.assertEqual(result.stdout.strip(), "new-session-id")

        content = self._sessions_content()
        self.assertIn("new-session-id", content)
        self.assertNotIn("old-session-id", content)
        self.assertEqual(content.count("main"), 1)

    def test_multiple_targets(self):
        jsonl1 = '{"type":"thread.started","thread_id":"sess-1"}\n'
        jsonl2 = '{"type":"thread.started","thread_id":"sess-2"}\n'
        self._run(["-", "branch-a", "review a"], stdin_data=jsonl1)
        self._run(["-", "branch-b", "review b"], stdin_data=jsonl2)

        content = self._sessions_content()
        self.assertIn("branch-a", content)
        self.assertIn("sess-1", content)
        self.assertIn("branch-b", content)
        self.assertIn("sess-2", content)

    # --- Error cases ---

    def test_missing_args(self):
        result = self._run([])
        self.assertNotEqual(result.returncode, 0)

    def test_no_thread_started_event(self):
        result = self._run(["-", "target", "desc"], stdin_data=NO_THREAD_JSONL)
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("no thread.started", result.stderr)

    def test_missing_file(self):
        result = self._run(["/nonexistent/file.jsonl", "target", "desc"])
        self.assertNotEqual(result.returncode, 0)

    def test_no_sessions_dir_warns_but_still_prints(self):
        env_no_dir = {k: v for k, v in os.environ.items() if k != "CODEX_SESSIONS_DIR"}
        result = subprocess.run(
            [sys.executable, SCRIPT, "-", "target", "desc"],
            input=VALID_JSONL,
            capture_output=True,
            text=True,
            env=env_no_dir,
        )
        self.assertEqual(result.returncode, 0)
        self.assertEqual(result.stdout.strip(), "abc-123-def")
        self.assertIn("Warning", result.stderr)


if __name__ == "__main__":
    unittest.main()
