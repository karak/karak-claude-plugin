"""Check that each blip's radar_url serves a page titled with the blip name.

HTTP status cannot tell: the site answers 200 for unknown slugs by serving the
quadrant page. A real blip page has ``<title>NAME | Technology Radar ...``.

Usage: python -X utf8 verify_urls.py [volume]   (default: latest_volume)
Prints one line per mismatch; exit 1 if any.
"""

from __future__ import annotations

import html
import re
import sys
import urllib.request
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import cache_helpers as ch  # noqa: E402

TITLE = re.compile(r"<title>\s*(.*?)\s*\|", re.S)


def page_title(url: str) -> str:
    req = urllib.request.Request(url, headers={"User-Agent": "karak-radar-verify"})
    with urllib.request.urlopen(req, timeout=30) as resp:
        m = TITLE.search(resp.read().decode("utf-8", "replace"))
    return html.unescape(m.group(1)) if m else ""


def check(blip: dict) -> str | None:
    try:
        title = page_title(blip["radar_url"])
    except Exception as exc:  # report any fetch failure as a mismatch
        return f"{blip['name']}: fetch failed ({exc})"
    if title.lower() != blip["name"].lower():
        return f"{blip['name']}: page title is {title!r}"
    return None


def main() -> int:
    vol = int(sys.argv[1]) if len(sys.argv) > 1 else ch.latest_volume()
    blips = ch.load_blips(vol)
    with ThreadPoolExecutor(8) as ex:
        problems = [p for p in ex.map(check, blips) if p]
    print("\n".join(problems) if problems else f"v{vol}: all {len(blips)} URLs verified")
    return 1 if problems else 0


if __name__ == "__main__":
    raise SystemExit(main())
