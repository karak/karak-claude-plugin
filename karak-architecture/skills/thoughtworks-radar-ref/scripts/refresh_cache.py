"""Bulk-populate the per-user cache for thoughtworks-radar-ref.

Usage::

    python scripts/refresh_cache.py [--volume 34] [--blips-only|--themes-only] [--limit N]

Iterates over the structural index for a volume, fetches the canonical
Thoughtworks page for each entry, extracts the summary/narrative text, and
writes it to the per-user cache. Existing cache entries are skipped by default;
pass ``--refetch`` to force overwrite.

Stdlib only — uses urllib for HTTP and a minimal HTML stripper. If the
extraction is unsatisfactory (HTML structure changes), prefer running the
Claude Code WebFetch tool interactively instead; both write to the same
cache via cache_helpers.

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


def fetch(url: str, timeout: float = 20.0) -> str:
    req = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        charset = resp.headers.get_content_charset() or "utf-8"
        return resp.read().decode(charset, errors="replace")


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


def refresh_blips(volume: int, refetch: bool, limit: int | None) -> int:
    blips = load_blips(volume)
    if limit:
        blips = blips[:limit]
    updated = 0
    for i, blip in enumerate(blips, 1):
        name = blip["name"]
        url = blip["radar_url"]
        if not refetch and get_cached_summary(name, volume) is not None:
            continue
        try:
            html = fetch(url)
        except (urllib.error.URLError, TimeoutError) as exc:
            print(f"  [{i}/{len(blips)}] SKIP {name}: {exc}", file=sys.stderr)
            continue
        summary = extract_blip_summary(html)
        if not summary:
            print(f"  [{i}/{len(blips)}] EMPTY {name}: no extractable summary", file=sys.stderr)
            continue
        write_cached_summary(name, summary, volume)
        updated += 1
        print(f"  [{i}/{len(blips)}] {name}: cached ({len(summary)} chars)")
        time.sleep(0.5)  # be polite to the origin
    return updated


def refresh_themes(volume: int, refetch: bool) -> int:
    themes = load_themes(volume)
    updated = 0
    for theme in themes:
        tid = theme["id"]
        if not refetch and get_cached_theme_narrative(tid, volume) is not None:
            continue
        # Themes are inline on /radar — fetch the landing page once is enough.
        # For best-effort extraction, store the whole landing page text per theme,
        # caller (model) can locate the right section by title.
        try:
            html = fetch(theme["source_url"])
        except (urllib.error.URLError, TimeoutError) as exc:
            print(f"  THEME SKIP {tid}: {exc}", file=sys.stderr)
            continue
        text = strip_html(html)
        # Try to slice around the title for a tighter narrative
        title = theme["title"]
        idx = text.lower().find(title.lower())
        if idx >= 0:
            narrative = text[idx : idx + 3000]
        else:
            narrative = text[:3000]
        write_cached_theme_narrative(tid, narrative, volume)
        updated += 1
        print(f"  THEME {tid}: cached ({len(narrative)} chars)")
        time.sleep(0.5)
    return updated


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

    blips_n = themes_n = 0
    if not args.themes_only:
        print("Blips:")
        blips_n = refresh_blips(volume, args.refetch, args.limit)
    if not args.blips_only:
        print("Themes:")
        themes_n = refresh_themes(volume, args.refetch)

    print(f"Done. Updated: {blips_n} blip(s), {themes_n} theme(s).")
    return 0


if __name__ == "__main__":
    sys.exit(main())
