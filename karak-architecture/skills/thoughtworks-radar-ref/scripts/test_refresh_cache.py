"""Tests for refresh_cache.py.

Covers fetch() error paths including retry on transient failures
(HTTP 5xx, TimeoutError), the extract_blip_summary fallback chain,
the refresh_blips/refresh_themes empty-ratio gate, and the
--limit / --refetch flags.

Network is fully mocked via monkeypatch on urllib.request.urlopen and
on time.sleep (so retries don't burn wall-clock).
"""

from __future__ import annotations

import io
import sys
from pathlib import Path
from urllib.error import HTTPError, URLError

import pytest

SCRIPT_DIR = Path(__file__).resolve().parent

sys.path.insert(0, str(SCRIPT_DIR))
import cache_helpers as ch  # noqa: E402
import refresh_cache as rc  # noqa: E402


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------


@pytest.fixture
def fake_cache_home(tmp_path, monkeypatch):
    monkeypatch.setenv("XDG_CACHE_HOME", str(tmp_path))
    return tmp_path


@pytest.fixture(autouse=True)
def _no_sleep(monkeypatch):
    """Suppress time.sleep in both refresh_cache (politeness + retry) so the
    suite stays sub-second. Each test that cares about retry count asserts
    via the urlopen call counter instead.
    """
    monkeypatch.setattr(rc.time, "sleep", lambda *_a, **_kw: None)


class FakeResponse:
    """Minimal urlopen() context manager double."""

    def __init__(self, body: bytes, status: int = 200, content_type: str = "text/html", charset: str = "utf-8"):
        self._body = body
        self.status = status
        self._content_type = content_type
        self._charset = charset

    # urlopen response API used by _fetch_once
    @property
    def headers(self):
        ct = self._content_type
        cs = self._charset
        class _H:
            def get_content_type(self_inner):
                return ct
            def get_content_charset(self_inner):
                return cs
        return _H()

    def read(self):
        return self._body

    def __enter__(self):
        return self

    def __exit__(self, *_a):
        return False


def _install_urlopen(monkeypatch, side_effects):
    """side_effects is a list of either FakeResponse or Exception. Each
    urlopen() call consumes the next one. A counter is returned so tests
    can assert attempt counts.
    """
    calls = {"n": 0}
    queue = list(side_effects)

    def fake_urlopen(req, timeout=None):
        calls["n"] += 1
        if not queue:
            raise AssertionError("urlopen called more times than side_effects provided")
        nxt = queue.pop(0)
        if isinstance(nxt, BaseException):
            raise nxt
        return nxt

    monkeypatch.setattr(rc.urllib.request, "urlopen", fake_urlopen)
    return calls


# ---------------------------------------------------------------------------
# fetch() — happy + error paths
# ---------------------------------------------------------------------------


def test_fetch_returns_body_on_200_html(monkeypatch):
    html = b"<html><body><article>hello</article></body></html>"
    calls = _install_urlopen(monkeypatch, [FakeResponse(html)])
    body = rc.fetch("https://example.com/x")
    assert "<article>hello</article>" in body
    assert calls["n"] == 1


def test_fetch_raises_fetcherror_for_non_html_content_type_without_retry(monkeypatch):
    calls = _install_urlopen(
        monkeypatch,
        [FakeResponse(b"{}", content_type="application/json")],
    )
    with pytest.raises(rc.FetchError, match="non-HTML"):
        rc.fetch("https://example.com/x")
    assert calls["n"] == 1, "FetchError must not trigger retry"


def test_fetch_raises_fetcherror_for_interstitial_body_without_retry(monkeypatch):
    body = b"<html><body>Please verify you are human before continuing</body></html>"
    calls = _install_urlopen(monkeypatch, [FakeResponse(body)])
    with pytest.raises(rc.FetchError, match="interstitial"):
        rc.fetch("https://example.com/x")
    assert calls["n"] == 1


def _httperror(code: int) -> HTTPError:
    return HTTPError(
        url="https://example.com/x",
        code=code,
        msg="boom",
        hdrs=None,  # type: ignore[arg-type]
        fp=io.BytesIO(b""),
    )


def test_fetch_does_not_retry_on_4xx(monkeypatch):
    calls = _install_urlopen(monkeypatch, [_httperror(404)])
    with pytest.raises(HTTPError):
        rc.fetch("https://example.com/x")
    assert calls["n"] == 1


def test_fetch_retries_on_5xx_and_eventually_raises(monkeypatch):
    calls = _install_urlopen(
        monkeypatch,
        [_httperror(503), _httperror(503), _httperror(503)],
    )
    with pytest.raises(HTTPError):
        rc.fetch("https://example.com/x")
    assert calls["n"] == rc.MAX_FETCH_ATTEMPTS == 3


def test_fetch_retries_on_5xx_then_succeeds(monkeypatch):
    html = b"<html><article>ok</article></html>"
    calls = _install_urlopen(
        monkeypatch,
        [_httperror(503), FakeResponse(html)],
    )
    body = rc.fetch("https://example.com/x")
    assert "ok" in body
    assert calls["n"] == 2


def test_fetch_retries_on_timeout_then_succeeds(monkeypatch):
    html = b"<html><article>ok</article></html>"
    calls = _install_urlopen(
        monkeypatch,
        [TimeoutError("slow"), TimeoutError("slow"), FakeResponse(html)],
    )
    body = rc.fetch("https://example.com/x")
    assert "ok" in body
    assert calls["n"] == 3


def test_fetch_backoff_sequence_is_exponential(monkeypatch):
    """Pin the exponential schedule (1s, 2s, ...) so a refactor that
    accidentally flattens the curve or doubles the base is caught. The
    autouse no-sleep fixture is overridden here by re-patching last.
    """
    sleeps: list[float] = []
    monkeypatch.setattr(rc.time, "sleep", lambda s: sleeps.append(s))
    _install_urlopen(
        monkeypatch,
        [_httperror(503), _httperror(503), _httperror(503)],
    )
    with pytest.raises(HTTPError):
        rc.fetch("https://example.com/x")
    # Sleeps happen between attempts: after attempt 1 and after attempt 2.
    # The final (3rd) attempt re-raises without sleeping.
    assert sleeps == [1.0, 2.0], f"expected exponential 1s→2s, got {sleeps}"


def test_fetch_does_not_retry_on_non_timeout_urlerror(monkeypatch):
    """A bare URLError (e.g. DNS failure) is not in the retry whitelist —
    surface it immediately rather than masking config issues with backoff.
    """
    calls = _install_urlopen(monkeypatch, [URLError("dns dead")])
    with pytest.raises(URLError):
        rc.fetch("https://example.com/x")
    assert calls["n"] == 1


# ---------------------------------------------------------------------------
# extract_blip_summary
# ---------------------------------------------------------------------------


def test_extract_blip_summary_returns_empty_when_no_article_or_main():
    html = "<html><body><div>just a div</div></body></html>"
    assert rc.extract_blip_summary(html) == ""


def test_extract_blip_summary_prefers_article_over_main():
    html = "<html><article>article wins</article><main>main loses</main></html>"
    assert "article wins" in rc.extract_blip_summary(html)
    assert "main loses" not in rc.extract_blip_summary(html)


def test_extract_blip_summary_falls_back_to_main_when_no_article():
    html = "<html><main>main text</main></html>"
    assert "main text" in rc.extract_blip_summary(html)


# ---------------------------------------------------------------------------
# refresh_blips — exit code on broken extractor
# ---------------------------------------------------------------------------


def test_refresh_blips_returns_exit_2_when_empty_ratio_exceeds_threshold(
    fake_cache_home, monkeypatch
):
    """If most fetched HTML lacks <article>/<main>, the empty ratio gate
    must trip and main() must return 2. Otherwise a structural break on
    the Thoughtworks side silently produces a zero-updates cache.
    """
    # Fetch always succeeds but returns content with no extractable region.
    monkeypatch.setattr(rc, "fetch", lambda url, timeout=20.0: "<div>nothing here</div>")

    # Run blips-only against v34 with a small cap so the test stays fast.
    rc_main_rc = rc.main(["--volume", "34", "--blips-only", "--limit", "6"])
    assert rc_main_rc == 2


def test_refresh_blips_below_floor_all_skipped_returns_zero(fake_cache_home, monkeypatch):
    """Below the gate floor (``attempted < 5``), a fully-failed run still
    returns 0. The floor is a noise-suppression heuristic — a tiny smoke
    test that runs offline shouldn't trip the gate. The zero-update gate
    catches the real concern (``attempted >= 5 and updated == 0``); see
    ``test_refresh_blips_all_skipped_at_floor_returns_exit_2``.
    """
    monkeypatch.setattr(
        rc,
        "fetch",
        lambda url, timeout=20.0: (_ for _ in ()).throw(URLError("offline")),
    )
    rc_main_rc = rc.main(["--volume", "34", "--blips-only", "--limit", "3"])
    assert rc_main_rc == 0


def test_refresh_blips_all_skipped_at_floor_returns_exit_2(fake_cache_home, monkeypatch):
    """When ``attempted >= 5`` and every fetch raises a recoverable error
    (URLError / TimeoutError / FetchError), main() must return 2. The
    empty-ratio gate stays silent here (empties=0, so extractor is fine),
    but no work was done — without this gate, an all-offline run looks
    indistinguishable from a successful no-op by exit code.
    """
    monkeypatch.setattr(
        rc,
        "fetch",
        lambda url, timeout=20.0: (_ for _ in ()).throw(URLError("offline")),
    )
    rc_main_rc = rc.main(["--volume", "34", "--blips-only", "--limit", "5"])
    assert rc_main_rc == 2


def test_refresh_themes_all_skipped_at_floor_returns_exit_2(fake_cache_home, monkeypatch):
    """Symmetric to the blip-side zero-update gate. With themes_attempted
    >= 2 and every fetch failing, the empty-ratio gate cannot fire (no
    empties to count) but the run produced zero updates — exit 2.
    """
    two_themes = [
        {
            "id": "first-theme",
            "title": "First Theme",
            "source_url": "https://example.com/radar#first",
            "volume": 34,
            "related_blip_names": [],
        },
        {
            "id": "second-theme",
            "title": "Second Theme",
            "source_url": "https://example.com/radar#second",
            "volume": 34,
            "related_blip_names": [],
        },
    ]
    monkeypatch.setattr(rc, "load_themes", lambda v: two_themes)
    monkeypatch.setattr(
        rc,
        "fetch",
        lambda url, timeout=20.0: (_ for _ in ()).throw(URLError("offline")),
    )
    rc_main_rc = rc.main(["--volume", "34", "--themes-only"])
    assert rc_main_rc == 2


def test_refresh_themes_returns_exit_2_when_titles_missing(
    fake_cache_home, monkeypatch
):
    """Symmetric to the blip-side gate: if Thoughtworks restructures the
    themes page so theme titles no longer appear in the served HTML, every
    extraction empties and main() must return 2 instead of silently
    caching nav-chrome.
    """
    monkeypatch.setattr(
        rc, "fetch", lambda url, timeout=20.0: "<html><body>unrelated content</body></html>"
    )
    rc_main_rc = rc.main(["--volume", "34", "--themes-only"])
    assert rc_main_rc == 2


def test_refresh_themes_single_theme_below_attempted_threshold_returns_zero(
    fake_cache_home, monkeypatch
):
    """The gate requires ``themes_attempted >= 2`` to avoid tripping on a
    single transient miss. Stub load_themes to return exactly one record
    and verify a 1/1 empty ratio does NOT return 2.
    """
    one_theme = [
        {
            "id": "x-only",
            "title": "Definitely Not Present",
            "source_url": "https://example.com/radar",
            "volume": 34,
            "related_blip_names": [],
        }
    ]
    monkeypatch.setattr(rc, "load_themes", lambda v: one_theme)
    monkeypatch.setattr(
        rc, "fetch", lambda url, timeout=20.0: "<html><body>no match here</body></html>"
    )
    rc_main_rc = rc.main(["--volume", "34", "--themes-only"])
    assert rc_main_rc == 0


def test_refresh_blips_refetch_overwrites_existing_entry(fake_cache_home, monkeypatch):
    """--refetch must replace an existing cached value, not be a no-op."""
    blips = ch.load_blips(34)
    target = blips[0]["name"]
    ch.write_cached_summary(target, "old value", volume=34)

    monkeypatch.setattr(
        rc,
        "fetch",
        lambda url, timeout=20.0: f"<article>fresh content for {target}</article>",
    )
    rc_main_rc = rc.main(
        ["--volume", "34", "--blips-only", "--limit", "1", "--refetch"]
    )
    assert rc_main_rc == 0
    fresh = ch.get_cached_summary(target, volume=34)
    assert fresh is not None
    assert "fresh content" in fresh
    assert fresh != "old value"


# ---------------------------------------------------------------------------
# --limit boundary values
# ---------------------------------------------------------------------------


def _counting_fetch(monkeypatch):
    calls = {"n": 0}

    def fake_fetch(url, timeout=20.0):
        calls["n"] += 1
        return "<article>ok content</article>"

    monkeypatch.setattr(rc, "fetch", fake_fetch)
    return calls


def test_limit_zero_processes_nothing(fake_cache_home, monkeypatch):
    calls = _counting_fetch(monkeypatch)
    rc.main(["--volume", "34", "--blips-only", "--limit", "0"])
    assert calls["n"] == 0


def test_limit_one_processes_first_only(fake_cache_home, monkeypatch):
    calls = _counting_fetch(monkeypatch)
    rc.main(["--volume", "34", "--blips-only", "--limit", "1"])
    assert calls["n"] == 1


def test_limit_above_total_processes_all_blips(fake_cache_home, monkeypatch):
    calls = _counting_fetch(monkeypatch)
    total = len(ch.load_blips(34))
    rc.main(["--volume", "34", "--blips-only", "--limit", str(total + 100)])
    assert calls["n"] == total
