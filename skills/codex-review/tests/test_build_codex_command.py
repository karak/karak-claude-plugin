"""Tests for build_codex_command.py — codex CLI command builder with model specification."""
import os
import subprocess
import sys
import unittest

SCRIPT = os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
    "scripts",
    "build_codex_command.py",
)


class TestBuildCodexCommand(unittest.TestCase):
    """Test that the command builder produces correct codex CLI invocations."""

    def _run(self, args):
        result = subprocess.run(
            [sys.executable, SCRIPT] + args,
            capture_output=True,
            text=True,
        )
        return result.stdout.strip(), result.stderr.strip(), result.returncode

    # --- Model specification ---

    def test_default_model_is_gpt_5_4(self):
        """Without -m, the built command must include -m gpt-5.4."""
        stdout, _, rc = self._run(["--prompt", "Review this code"])
        self.assertEqual(rc, 0)
        self.assertIn("-m gpt-5.4", stdout)

    def test_custom_model_overrides_default(self):
        """User-specified model overrides the default."""
        stdout, _, rc = self._run(["--prompt", "Review", "--model", "o3"])
        self.assertEqual(rc, 0)
        self.assertIn("-m o3", stdout)
        self.assertNotIn("gpt-5.4", stdout)

    # --- Command structure ---

    def test_includes_exec_json_sandbox(self):
        """Built command must include exec, --json, and --sandbox flags."""
        stdout, _, rc = self._run(["--prompt", "Review this"])
        self.assertEqual(rc, 0)
        self.assertIn("codex exec", stdout)
        self.assertIn("--json", stdout)
        self.assertIn("--sandbox danger-full-access", stdout)

    def test_prompt_is_quoted_in_command(self):
        """The prompt text must appear in the command."""
        prompt = "Review the login feature changes"
        stdout, _, rc = self._run(["--prompt", prompt])
        self.assertEqual(rc, 0)
        self.assertIn(prompt, stdout)

    # --- Pipeline integration ---

    def test_includes_tee_and_pipeline(self):
        """Built command should include tee for JSONL capture."""
        stdout, _, rc = self._run(["--prompt", "Review"])
        self.assertEqual(rc, 0)
        self.assertIn("tee /tmp/codex-review-output.jsonl", stdout)

    def test_includes_extract_pipeline_when_target_given(self):
        """When target and description are given, pipeline includes extract_and_save_session."""
        stdout, _, rc = self._run([
            "--prompt", "Review",
            "--target", "feature/auth",
            "--description", "Auth review",
        ])
        self.assertEqual(rc, 0)
        self.assertIn("extract_and_save_session.py", stdout)
        self.assertIn("feature/auth", stdout)
        self.assertIn("Auth review", stdout)

    def test_no_extract_pipeline_without_target(self):
        """Without target, pipeline should not include extract_and_save_session."""
        stdout, _, rc = self._run(["--prompt", "Review"])
        self.assertEqual(rc, 0)
        self.assertNotIn("extract_and_save_session.py", stdout)

    # --- Error cases ---

    def test_missing_prompt_fails(self):
        """Must fail when no prompt is provided."""
        _, _, rc = self._run([])
        self.assertNotEqual(rc, 0)

    # --- Timeout constant ---

    def test_recommended_timeout_is_180s_or_more(self):
        """RECOMMENDED_TIMEOUT_MS must be >= 180000."""
        from scripts.build_codex_command import RECOMMENDED_TIMEOUT_MS
        self.assertGreaterEqual(RECOMMENDED_TIMEOUT_MS, 180000)


if __name__ == "__main__":
    unittest.main()
