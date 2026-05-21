"""Bulk-populate the per-user cache for thoughtworks-radar-ref.

Usage::

    python scripts/refresh_cache.py [--volume 34] [--blips-only|--themes-only] [--limit N]

Iterates over the structural index for a volume, fetches the canonical
Thoughtworks page for each entry, and writes a coarse extraction (the entire
``<article>`` or ``<main>`` text, stripped of tags) into the per-user cache.
Existing cache entries are skipped by default; pass ``--refetch`` to force
overwrite.

The extraction is **intentionally coarse** — the model is expected to locate
the relevant summary paragraph at read time. The script is fail-loud: when
the HTML structure changes and most extractions return empty, the run exits
non-zero rather than silently reporting "Updated: 0". For per-blip
interactive refresh, the Claude Code WebFetch tool writes to the same cache
via :mod:`cache_helpers` and is usually preferable to bulk runs.

Stdlib only — uses urllib for HTTP and a minimal regex+HTML-unescape stripper.

Note on copyright: this script downloads Thoughtworks-authored text under
the same fair-use posture as a browser cache — the bytes never enter the
git repo. Do not commit the cache directory.
"""

from __future__ import annotations

import argparse
import html as html_mod
import re
import sys
import time
import urllib.error
import urllib.request
from typing import Iterable

from cache_helpers import (
    latest_volume,
    load_blips,
    load_themes,
    get_cached_summary,
    get_cached_theme_narrative,
    write_cached_summary,
    write_cached_theme_narrative,
)


USER_AGENT = "karak-claude-plugin/thoughtworks-radar-ref (+https://github.com/karak-developer/karak-claude-plugin)"

# Heuristic markers for bot-challenge / WAF interstitial pages that some CDNs
# return with HTTP 200. If any of these tokens appears in extracted text we
# refuse to cache the body — silently caching a CAPTCHA page as the canonical
# Thoughtworks summary would be worse than reporting a miss.
INTERSTITIAL_MARKERS = (
    "verify you are human",
    "verifying you are human",
    "checking your browser",
    "access denied",
    "request unsuccessful",
    "ddos protection",
    "captcha",
    "cf-chl-bypass",
)


class FetchError(Exception):
    """Raised when fetch() refuses to return a cacheable body."""


MAX_FETCH_ATTEMPTS = 3
RETRY_BACKOFF_BASE_SECONDS = 1.0


def _fetch_once(url: str, timeout: float) -> str:
    """Single fetch attempt.

    Raises ``FetchError`` for any non-200 status, non-HTML content-type,
    or body containing a known interstitial marker so callers never
    silently cache CAPTCHA pages or JSON error blobs as the canonical
    Thoughtworks summary.

    ``HTTPError`` / ``URLError`` / ``TimeoutError`` propagate untouched so
    the retry layer can decide whether to retry."""
    req = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        status = getattr(resp, "status", 200)
        if status != 200:
            raise FetchError(f"non-200 status: {status}")
        ctype = resp.headers.get_content_type() or ""
        if not ctype.startswith("text/html"):
            raise FetchError(f"non-HTML content-type: {ctype}")
        charset = resp.headers.get_content_charset() or "utf-8"
        body = resp.read().decode(charset, errors="replace")
    lowered = body.lower()
    for marker in INTERSTITIAL_MARKERS:
        if marker in lowered:
            raise FetchError(f"interstitial marker present: {marker!r}")
    return body


def fetch(url: str, timeout: float = 20.0) -> str:
    """Fetch a URL with retry on transient failures (5xx, TimeoutError).

    Up to ``MAX_FETCH_ATTEMPTS`` attempts with exponential backoff
    (1s, 2s, ...). Retries only on signals that suggest transient
    infrastructure problems:

    - ``TimeoutError`` — raised directly by ``urlopen(timeout=...)``.
      Since Python 3.10 ``socket.timeout`` is an alias for ``TimeoutError``
      and is a sibling of, not a subclass of, ``URLError``.
    - ``HTTPError`` with status in the 5xx range. ``HTTPError`` IS a
      ``URLError`` subclass, but only the 5xx branch is retried — see below.

    Surfaced immediately (no retry):

    - ``HTTPError`` with 4xx status — structural problem on the server side;
      retrying just delays the SKIP.
    - ``FetchError`` (non-HTML content-type or interstitial marker) — same
      reasoning; the body will not become cacheable on a retry.
    - ``URLError`` with any other ``.reason`` (e.g. DNS failure, connection
      refused). These are config / environment issues, not transient hiccups.

    The final exception is re-raised unchanged so callers can distinguish
    transient from structural failures by exception type.
    """
    last_exc: BaseException | None = None
    for attempt in range(1, MAX_FETCH_ATTEMPTS + 1):
        try:
            return _fetch_once(url, timeout)
        except urllib.error.HTTPError as exc:
            last_exc = exc
            is_retryable = 500 <= exc.code < 600
            is_last = attempt == MAX_FETCH_ATTEMPTS
            if not is_retryable or is_last:
                _log_fetch_give_up(url, exc, attempt, retryable=is_retryable)
                raise
        except TimeoutError as exc:
            last_exc = exc
            if attempt == MAX_FETCH_ATTEMPTS:
                _log_fetch_give_up(url, exc, attempt, retryable=True)
                raise
        # Non-retried: FetchError, non-HTTPError URLError, anything else —
        # let it propagate without entering the except clauses above.
        sleep_s = RETRY_BACKOFF_BASE_SECONDS * (2 ** (attempt - 1))
        print(
            f"  RETRY {url}: {last_exc!r} "
            f"(attempt {attempt}/{MAX_FETCH_ATTEMPTS}, sleeping {sleep_s}s)",
            file=sys.stderr,
        )
        time.sleep(sleep_s)
    # Unreachable — the loop either returns or raises.
    assert last_exc is not None
    raise last_exc


def _log_fetch_give_up(
    url: str, exc: BaseException, attempt: int, retryable: bool
) -> None:
    """Stderr log when fetch() exits via a terminal raise.

    Symmetric with the RETRY log so a reader of stderr always sees an
    explicit terminal line. Without this, a 5xx exhaustion looked like
    "RETRY 1/3 ... RETRY 2/3 ..." with the third failure invisible —
    only the caller's single-line SKIP appeared, without attempt count.
    """
    reason = "exhausted retries" if retryable else "non-retryable"
    print(
        f"  GIVE UP {url}: {exc!r} "
        f"(attempt {attempt}/{MAX_FETCH_ATTEMPTS}, {reason})",
        file=sys.stderr,
    )


_TAG_RE = re.compile(r"<[^>]+>")
_WS_RE = re.compile(r"\s+")


def strip_html(html: str) -> str:
    text = _TAG_RE.sub(" ", html)
    text = html_mod.unescape(text)
    return _WS_RE.sub(" ", text).strip()


def extract_blip_summary(html: str) -> str:
    """Best-effort extraction of a blip's summary paragraph.

    Thoughtworks blip pages typically wrap the description in a main content
    region. We grab text between common landmarks and trim. If extraction
    fails, return the empty string — caller can decide to skip.
    """
    # Try common patterns: <article>, <main>, or fall back to <body>
    for tag in ("article", "main"):
        m = re.search(rf"<{tag}\b[^>]*>(.*?)</{tag}>", html, flags=re.DOTALL | re.IGNORECASE)
        if m:
            return strip_html(m.group(1))[:4000]
    return ""


def refresh_blips(volume: int, refetch: bool, limit: int | None) -> tuple[int, int, int]:
    """Returns (updated, attempted, empties). The caller decides whether
    a high ratio of empties means the HTML structure changed and exits
    non-zero — silent zero-update on a broken extractor would be worse
    than a loud failure.
    """
    blips = load_blips(volume)
    if limit is not None:
        blips = blips[:limit]
    updated = attempted = empties = 0
    for i, blip in enumerate(blips, 1):
        name = blip["name"]
        url = blip["radar_url"]
        if not refetch and get_cached_summary(name, volume) is not None:
            continue
        attempted += 1
        if attempted > 1:
            time.sleep(0.5)  # politeness applies on every fetch attempt, not only successes
        try:
            html = fetch(url)
        except (urllib.error.URLError, TimeoutError, FetchError) as exc:
            print(f"  [{i}/{len(blips)}] SKIP {name}: {exc}", file=sys.stderr)
            continue
        summary = extract_blip_summary(html)
        if not summary:
            empties += 1
            print(f"  [{i}/{len(blips)}] EMPTY {name}: no extractable summary", file=sys.stderr)
            continue
        write_cached_summary(name, summary, volume)
        updated += 1
        print(f"  [{i}/{len(blips)}] {name}: cached ({len(summary)} chars)")
    return updated, attempted, empties


def refresh_themes(volume: int, refetch: bool) -> tuple[int, int, int]:
    """Returns (updated, attempted, empties). A theme whose title is not
    findable on the source page is treated as an empty extraction and
    skipped — caching the first 3000 chars of nav chrome as the narrative
    would mislead downstream consumers.
    """
    themes = load_themes(volume)
    updated = attempted = empties = 0
    for theme in themes:
        tid = theme["id"]
        if not refetch and get_cached_theme_narrative(tid, volume) is not None:
            continue
        attempted += 1
        if attempted > 1:
            time.sleep(0.5)
        # Themes are inline on /radar — landing-page text is sliced around the
        # title token so the cached value is the section, not the whole page.
        try:
            html = fetch(theme["source_url"])
        except (urllib.error.URLError, TimeoutError, FetchError) as exc:
            print(f"  THEME SKIP {tid}: {exc}", file=sys.stderr)
            continue
        text = strip_html(html)
        title = theme["title"]
        idx = text.lower().find(title.lower())
        if idx < 0:
            empties += 1
            print(
                f"  THEME EMPTY {tid}: title {title!r} not present on source page — "
                "refusing to cache nav-chrome fallback",
                file=sys.stderr,
            )
            continue
        narrative = text[idx : idx + 3000]
        write_cached_theme_narrative(tid, narrative, volume)
        updated += 1
        print(f"  THEME {tid}: cached ({len(narrative)} chars)")
    return updated, attempted, empties


def main(argv: Iterable[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Refresh per-user cache for thoughtworks-radar-ref")
    parser.add_argument("--volume", type=int, default=None, help="Volume to refresh (default: latest)")
    parser.add_argument("--blips-only", action="store_true")
    parser.add_argument("--themes-only", action="store_true")
    parser.add_argument("--refetch", action="store_true", help="Overwrite existing cache entries")
    parser.add_argument("--limit", type=int, default=None, help="Cap number of blips processed (for smoke tests)")
    args = parser.parse_args(argv)

    volume = args.volume if args.volume is not None else latest_volume()
    print(f"Refreshing cache for volume v{volume} (refetch={args.refetch})")

    blips_updated = blips_attempted = blips_empties = 0
    themes_updated = themes_attempted = themes_empties = 0
    if not args.themes_only:
        print("Blips:")
        blips_updated, blips_attempted, blips_empties = refresh_blips(
            volume, args.refetch, args.limit
        )
    if not args.blips_only:
        print("Themes:")
        themes_updated, themes_attempted, themes_empties = refresh_themes(
            volume, args.refetch
        )

    print(
        f"Done. Blips: updated={blips_updated} attempted={blips_attempted} empties={blips_empties}. "
        f"Themes: updated={themes_updated} attempted={themes_attempted} empties={themes_empties}."
    )

    # Gate 1: extractor broke wholesale (most attempts returned empty) —
    # signals a Thoughtworks-side HTML structure change.
    EMPTY_RATIO_THRESHOLD = 0.5
    BLIPS_GATE_FLOOR = 5
    THEMES_GATE_FLOOR = 2
    if blips_attempted >= BLIPS_GATE_FLOOR and blips_empties / blips_attempted >= EMPTY_RATIO_THRESHOLD:
        print(
            f"ERROR: {blips_empties}/{blips_attempted} blip extractions were empty — "
            "Thoughtworks HTML structure likely changed. Update extract_blip_summary() "
            "before relying on this cache.",
            file=sys.stderr,
        )
        return 2
    if themes_attempted >= THEMES_GATE_FLOOR and themes_empties / themes_attempted >= EMPTY_RATIO_THRESHOLD:
        print(
            f"ERROR: {themes_empties}/{themes_attempted} theme extractions were empty — "
            "Thoughtworks themes page structure likely changed.",
            file=sys.stderr,
        )
        return 2

    # Gate 2: zero updates despite a non-trivial number of attempts. Catches
    # the all-offline / all-SKIP case the empty-ratio gate cannot see
    # (empties=0 means extractor is fine — but no work was done). Without
    # this, a fully-failed network run exits 0 and the operator assumes the
    # cache is fresh.
    if blips_attempted >= BLIPS_GATE_FLOOR and blips_updated == 0:
        blips_skips = blips_attempted - blips_empties - blips_updated
        print(
            f"ERROR: 0/{blips_attempted} blips were updated "
            f"(empties={blips_empties}, skips={blips_skips}) — "
            "all fetches failed or every extraction was empty. "
            "Check network and rerun.",
            file=sys.stderr,
        )
        return 2
    if themes_attempted >= THEMES_GATE_FLOOR and themes_updated == 0:
        themes_skips = themes_attempted - themes_empties - themes_updated
        print(
            f"ERROR: 0/{themes_attempted} themes were updated "
            f"(empties={themes_empties}, skips={themes_skips}) — "
            "all fetches failed or every extraction was empty. "
            "Check network and rerun.",
            file=sys.stderr,
        )
        return 2
    return 0


if __name__ == "__main__":
    sys.exit(main())
