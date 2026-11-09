"""Read-only, catalog-driven disk usage scan for Windows.

Never deletes, moves or renames anything (enforced by tests/test_safety.py).
Usage: python scan.py --out scan.json [--catalog ../catalog/windows.json]
"""
import argparse
import concurrent.futures
import glob
import json
import os
import re
import shutil
import stat
import sys
import time
from pathlib import Path

REPARSE = stat.FILE_ATTRIBUTE_REPARSE_POINT          # 0x400
CLOUD = 0x1000 | 0x40000 | 0x400000                   # OFFLINE | RECALL_ON_OPEN | RECALL_ON_DATA_ACCESS

_VAR = re.compile(r"%([A-Za-z0-9_()]+)%")


def expand_vars(pattern, env):
    """Expand %VAR% (case-insensitive) and a leading ~ using the given env."""
    upper = {k.upper(): v for k, v in env.items()}

    def sub(m):
        return upper.get(m.group(1).upper(), m.group(0))

    out = _VAR.sub(sub, pattern)
    if out.startswith("~"):
        out = upper.get("USERPROFILE", "~") + out[1:]
    return out


def expand(pattern, env):
    """Expand a catalog path pattern to existing paths (globs allowed)."""
    path = expand_vars(pattern, env)
    if "%" in path:
        return []
    if glob.has_magic(path):
        return sorted(glob.glob(path))
    return [path] if os.path.lexists(path) else []


def size_tree(path, deadline=None):
    """Logical bytes of local data under path; does not follow reparse points."""
    total = files = cloud = 0
    newest = 0.0
    partial = False
    try:
        st = os.stat(path, follow_symlinks=False)
    except OSError:
        return {"bytes": 0, "files": 0, "cloud_files": 0, "newest_mtime": 0.0, "partial": True}
    if st.st_file_attributes & REPARSE:
        return {"bytes": 0, "files": 0, "cloud_files": 0, "newest_mtime": 0.0, "partial": False}
    if not stat.S_ISDIR(st.st_mode):
        if st.st_file_attributes & CLOUD:
            return {"bytes": 0, "files": 0, "cloud_files": 1, "newest_mtime": st.st_mtime, "partial": False}
        return {"bytes": st.st_size, "files": 1, "cloud_files": 0, "newest_mtime": st.st_mtime, "partial": False}

    stack = [path]
    while stack:
        if deadline is not None and time.monotonic() > deadline:
            partial = True
            break
        current = stack.pop()
        try:
            with os.scandir(current) as it:
                for entry in it:
                    try:
                        est = entry.stat(follow_symlinks=False)
                    except OSError:
                        partial = True
                        continue
                    attrs = est.st_file_attributes
                    if attrs & REPARSE:
                        continue
                    if stat.S_ISDIR(est.st_mode):
                        stack.append(entry.path)
                        continue
                    if est.st_mtime > newest:
                        newest = est.st_mtime
                    if attrs & CLOUD:
                        cloud += 1
                    else:
                        total += est.st_size
                        files += 1
        except OSError:
            partial = True
    return {"bytes": total, "files": files, "cloud_files": cloud, "newest_mtime": newest, "partial": partial}


def _children_older_than(root, days, exclude, now, deadline):
    cutoff = now - days * 86400
    items = []
    try:
        children = list(os.scandir(root))
    except OSError:
        return items, True
    partial = False
    excluded = {e.lower() for e in exclude}
    for child in children:
        if child.name.lower() in excluded:
            continue
        info = size_tree(child.path, deadline)
        partial |= info["partial"]
        try:
            own = child.stat(follow_symlinks=False).st_mtime
        except OSError:
            continue
        newest = max(info["newest_mtime"], own)
        if newest < cutoff and info["bytes"] > 0:
            items.append({"path": child.path, **info, "newest_mtime": newest})
    return items, partial


def scan_entry(entry, env, now=None, budget_s=60):
    now = time.time() if now is None else now
    deadline = time.monotonic() + budget_s
    items = []
    partial = False
    select = entry.get("select") or {}
    for pattern in entry.get("paths", []):
        for path in expand(pattern, env):
            if "children_older_than_days" in select:
                found, p = _children_older_than(
                    path, select["children_older_than_days"], select.get("exclude", []), now, deadline)
                items.extend(found)
                partial |= p
            else:
                info = size_tree(path, deadline)
                partial |= info["partial"]
                if info["bytes"] > 0 or info["files"] > 0:
                    items.append({"path": path, **info})
    return {
        "id": entry["id"],
        "bytes": sum(i["bytes"] for i in items),
        "files": sum(i["files"] for i in items),
        "newest_mtime": max((i["newest_mtime"] for i in items), default=0.0),
        "partial": partial,
        "items": items,
    }


def _disk(env):
    drive = env.get("SYSTEMDRIVE") or "C:"
    target = drive if os.path.exists(drive) else os.path.splitdrive(os.path.abspath(drive))[0] + "\\"
    if len(target) == 2 and target.endswith(":"):
        target += "\\"
    usage = shutil.disk_usage(target)
    return {"drive": target, "free": usage.free, "total": usage.total}


def scan_catalog(catalog, env, now=None, budget_s=60, workers=8):
    now = time.time() if now is None else now
    started = time.monotonic()
    entries = catalog["entries"]
    with concurrent.futures.ThreadPoolExecutor(max_workers=workers) as pool:
        results = list(pool.map(lambda e: scan_entry(e, env, now=now, budget_s=budget_s), entries))
    return {
        "scanned_at": now,
        "seconds": round(time.monotonic() - started, 1),
        "disk": _disk(env),
        "entries": results,
    }


def main(argv=None):
    here = Path(__file__).resolve().parent
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--catalog", default=str(here.parent / "catalog" / "windows.json"))
    ap.add_argument("--out", required=True)
    ap.add_argument("--budget", type=float, default=60)
    args = ap.parse_args(argv)
    catalog = json.loads(Path(args.catalog).read_text(encoding="utf-8"))
    env = dict(os.environ)
    result = scan_catalog(catalog, env, budget_s=args.budget)
    Path(args.out).write_text(json.dumps(result, ensure_ascii=False, indent=1), encoding="utf-8")
    print(f"scanned {len(result['entries'])} entries in {result['seconds']}s -> {args.out}", file=sys.stderr)


if __name__ == "__main__":
    main()
