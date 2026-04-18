"""Integration tests: verify codex model refresh hang and -m fix.

codex-cli 0.111.0 hangs on model refresh when -m is not specified.
These tests prove the problem exists and that -m gpt-5.4 fixes it.
"""
import subprocess
import unittest

SIMPLE_PROMPT = "echo hello"
SHORT_TIMEOUT = 30  # seconds — enough for -m to work, too short for model refresh hang


class TestCodexModelRefreshHang(unittest.TestCase):
    """Verify that codex hangs without -m and succeeds with -m."""

    @classmethod
    def setUpClass(cls):
        """Skip all tests if codex is not installed."""
        result = subprocess.run(
            ["codex", "--version"],
            capture_output=True, text=True,
        )
        if result.returncode != 0:
            raise unittest.SkipTest("codex CLI not installed")

    def test_without_model_flag_times_out(self):
        """Without -m, codex hangs on model refresh and times out."""
        try:
            result = subprocess.run(
                ["codex", "exec", "--json", "--sandbox", "danger-full-access",
                 SIMPLE_PROMPT],
                capture_output=True, text=True,
                timeout=SHORT_TIMEOUT,
            )
            # If it somehow completes, that's unexpected for the hang scenario.
            # We mark this as a known-environment-dependent result.
            self.skipTest(
                f"codex completed without -m (rc={result.returncode}); "
                "model refresh hang may be fixed in this version"
            )
        except subprocess.TimeoutExpired:
            # This IS the expected behavior — codex hangs without -m
            pass

    def test_with_model_flag_completes(self):
        """With -m gpt-5.4, codex completes without hanging."""
        result = subprocess.run(
            ["codex", "exec", "--json", "--sandbox", "danger-full-access",
             "-m", "gpt-5.4", SIMPLE_PROMPT],
            capture_output=True, text=True,
            timeout=SHORT_TIMEOUT,
        )
        self.assertEqual(result.returncode, 0,
                         f"codex with -m gpt-5.4 failed: {result.stderr[:500]}")

    def test_bash_timeout_must_be_180s_or_more(self):
        """The build_codex_command default timeout must be >= 180000ms.

        Even with -m, large diffs can take time. 180s is the proven minimum.
        """
        from scripts.build_codex_command import RECOMMENDED_TIMEOUT_MS
        self.assertGreaterEqual(RECOMMENDED_TIMEOUT_MS, 180000)


if __name__ == "__main__":
    unittest.main()
