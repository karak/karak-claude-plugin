"""Read-only evidence probes: decide which items inside a tool's store are unused.

Each probe returns {"bytes", "items": [{"path", "bytes", ...}], "evidence": [...]}.
Pure parsing functions take text/paths so they can be tested on fixtures; `run_all`
gathers the real inputs (read-only commands only) for this machine.
Usage: python probes.py --out probes.json
"""
import argparse
import json
import os
import re
import subprocess
import sys
import urllib.parse
from pathlib import Path

GB = 1024 ** 3
MB = 1024 ** 2


def _result(items, evidence=None):
    return {"bytes": sum(i["bytes"] for i in items), "items": items, "evidence": evidence or []}


def _ver(v, parts=3):
    return tuple(int(x) for x in re.findall(r"\d+", v)[:parts])


# --- nvm ---------------------------------------------------------------------

def nvm_unused(list_text, nvm_root, pins, size_fn, pins_complete=True):
    """Installed Node versions that are not current, not pinned, not newest of their major."""
    if not pins_complete:
        result = _result([], ["クラウド上にしかない、または読めない .nvmrc / .node-version があり、"
                              "プロジェクトが固定した版を確認できないため今回は提案しない"])
        result["skip"] = True
        return result
    versions, current = [], None
    for line in list_text.splitlines():
        m = re.match(r"\s*(\*)?\s*v?(\d+\.\d+\.\d+)", line)
        if m:
            versions.append(m.group(2))
            if m.group(1):
                current = m.group(2)
    newest_per_major = {}
    for v in versions:
        major = _ver(v)[0]
        if major not in newest_per_major or _ver(v) > _ver(newest_per_major[major]):
            newest_per_major[major] = v
    pinned = set()
    for p in pins:
        p = p.lstrip("v")
        if re.fullmatch(r"\d+\.\d+\.\d+", p):
            pinned.add(p)
        elif re.fullmatch(r"\d+(\.\d+)?", p):
            matching = [v for v in versions if v.startswith(p + ".")]
            if matching:
                pinned.add(max(matching, key=_ver))
    keep = {current} | set(newest_per_major.values()) | pinned
    items = []
    for v in versions:
        if v in keep:
            continue
        path = os.path.join(nvm_root, "v" + v)
        if os.path.isdir(path):
            items.append({"path": path, "bytes": size_fn(path), "command": f"nvm uninstall {v}"})
    evidence = [f"使用中 {current}"] if current else []
    if items:
        evidence.append("各メジャー版の最新と .nvmrc 指定版は残す")
    return _result(items, evidence)


_SKIP_DIRS = {"node_modules", ".git", "appdata", ".cache", ".vscode", ".nuget", ".cargo", ".rustup"}


_ALIASES = re.compile(r"^(lts(/[\w*-]+)?|node|latest|stable|current|iojs)$", re.IGNORECASE)
_CLOUD = 0x1000 | 0x40000 | 0x400000


def _read_pin(path):
    """Version text of a pin file, '' for an alias, None when it cannot be understood."""
    data = Path(path).read_bytes()[:4096]
    if data[:2] in (b"\xff\xfe", b"\xfe\xff"):
        text = data.decode("utf-16", errors="replace")
    else:
        text = data.decode("utf-8-sig", errors="replace")
    token = text.strip().split()[0] if text.strip() else ""
    if _ALIASES.match(token):
        return ""
    m = re.fullmatch(r"v?(\d+(?:\.\d+){0,2})", token)
    return m.group(1) if m else None


def find_node_pins(roots, max_depth=64, unreadable=None):
    """Node versions pinned by .nvmrc / .node-version files under the given roots.

    Pin files that cannot be read locally or understood are appended to `unreadable`.
    """
    pins = set()

    def lost(path):
        if unreadable is not None:
            unreadable.append(path)

    for root in roots:
        stack = [(root, 0)]
        while stack:
            current, depth = stack.pop()
            try:
                entries = list(os.scandir(current))
            except OSError:
                continue
            for e in entries:
                try:
                    if e.is_symlink():
                        continue
                    if e.is_dir():
                        if depth < max_depth and e.name.lower() not in _SKIP_DIRS:
                            stack.append((e.path, depth + 1))
                        continue
                    if e.name not in (".nvmrc", ".node-version"):
                        continue
                    if e.stat(follow_symlinks=False).st_file_attributes & _CLOUD:
                        lost(e.path)
                        continue
                    version = _read_pin(e.path)
                except OSError:
                    lost(e.path)
                    continue
                if version is None:
                    lost(e.path)
                elif version:
                    pins.add(version)
    return pins


# --- Playwright ----------------------------------------------------------------

def playwright_unused(root, size_fn):
    """Browser revisions that no existing project's playwright-core refers to."""
    links = os.path.join(root, ".links")
    pinned, live = set(), 0
    try:
        link_files = list(os.scandir(links))
    except OSError:
        link_files = []
    for lf in link_files:
        try:
            core = Path(lf.path).read_text(encoding="utf-8").strip()
            data = json.loads(Path(core, "browsers.json").read_text(encoding="utf-8"))
        except (OSError, ValueError):
            continue
        live += 1
        for b in data.get("browsers", []):
            pinned.add((b["name"].replace("-", "_"), str(b["revision"])))
    if live == 0:
        return _result([], ["参照元のプロジェクトを確認できないため提案しない"])
    revisions = []
    for d in os.scandir(root):
        m = re.fullmatch(r"(.+)-(\d+)", d.name)
        if d.is_dir() and m:
            revisions.append((m.group(1), int(m.group(2)), d))
    newest = {}
    for name, rev, _ in revisions:
        newest[name] = max(newest.get(name, rev), rev)
    items = []
    for name, rev, d in revisions:
        if (name, str(rev)) not in pinned and rev != newest[name]:
            items.append({"path": d.path, "bytes": size_fn(d.path)})
    return _result(items, [f"既存プロジェクト {live} 件が参照する版と、各ブラウザーの最新版は残す"])


# --- VS Code -------------------------------------------------------------------

_EXT_DIR = re.compile(r"^(?P<id>[^-]+(?:-[^-\d][^-]*)*?)-(?P<ver>\d+\.\d+\.\d+[^-]*)(?:-(?P<plat>.+))?$")


def vscode_old_extensions(ext_dir, size_fn):
    """Extension folders not in extensions.json whose same id has a newer listed folder."""
    try:
        listed = json.loads(Path(ext_dir, "extensions.json").read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return _result([], ["extensions.json を読めないため提案しない"])
    referenced = {e.get("relativeLocation", "").lower() for e in listed}
    listed_versions = {}
    for loc in referenced:
        m = _EXT_DIR.match(loc)
        if m:
            listed_versions.setdefault(m.group("id"), []).append(_ver(m.group("ver")))
    items = []
    for d in os.scandir(ext_dir):
        name = d.name.lower()
        m = _EXT_DIR.match(name)
        if not d.is_dir() or not m or name in referenced:
            continue
        newer = [v for v in listed_versions.get(m.group("id"), []) if v > _ver(m.group("ver"))]
        if newer:
            items.append({"path": d.path, "bytes": size_fn(d.path)})
    return _result(items, ["拡張一覧に登録された新しい版がある旧版のみ"])


def _uri_to_path(uri):
    parsed = urllib.parse.urlparse(uri)
    if parsed.scheme != "file":
        return None
    path = urllib.parse.unquote(parsed.path)
    if re.match(r"^/[A-Za-z]:", path):
        path = path[1:]
    if parsed.netloc:
        path = f"//{parsed.netloc}{path}"
    return os.path.normpath(path)


def vscode_stale_workspaces(ws_dir, onedrive_roots, size_fn):
    """workspaceStorage folders whose single local folder no longer exists."""
    items = []
    try:
        dirs = list(os.scandir(ws_dir))
    except OSError:
        return _result([])
    roots = [os.path.normcase(os.path.normpath(r)) for r in onedrive_roots]
    for d in dirs:
        try:
            meta = json.loads(Path(d.path, "workspace.json").read_text(encoding="utf-8"))
        except (OSError, ValueError):
            continue
        folder = meta.get("folder")
        if not folder:
            continue
        path = _uri_to_path(folder)
        if path is None or path.startswith("//") or os.path.exists(path):
            continue
        if not os.path.exists(os.path.splitdrive(path)[0] + os.sep):
            continue
        if any(Path(d.path, "chatSessions").glob("*")):
            continue
        norm = os.path.normcase(path)
        owner = next((r for r in roots if norm == r or norm.startswith(r + os.sep)), None)
        if owner is not None and not os.path.isdir(owner):
            continue
        items.append({"path": d.path, "bytes": size_fn(d.path), "folder": path, "label": path})
    return _result(items, ["開いていたフォルダーが存在しないものだけ"] if items else [])


# --- drivers -------------------------------------------------------------------

_LABELS = {
    "driver": ("Driver Name", "ドライバー名"),
    "ext": ("Extension Driver Names", "拡張ドライバー名"),
    "original": ("Original Name", "元の名前"),
    "version": ("Driver Version", "ドライバーのバージョン", "ドライバー バージョン"),
    "status": ("Driver Status", "ドライバーの状態"),
    "provider": ("Provider Name", "プロバイダー名"),
}


def _label(key):
    k = key.strip()
    for name, variants in _LABELS.items():
        if k in variants:
            return name
    return None


def superseded_drivers(devices_text):
    """(in_use, candidates) from `pnputil /enum-devices /drivers` output."""
    in_use, candidates, current = set(), {}, None
    newest = {}
    for raw in devices_text.splitlines():
        if ":" not in raw:
            if not raw.strip() and current is not None:
                current = None
            continue
        indented = raw.startswith((" ", "\t"))
        key, _, value = raw.partition(":")
        name, value = _label(key), value.strip()
        if not indented:
            if name in ("driver", "ext"):
                in_use.update(v.strip().lower() for v in re.split(r"[,\s]+", value) if v.strip())
            continue
        if name == "driver":
            current = {"name": value.lower()}
        elif current is not None and name:
            current[name] = value
            if name == "version" and current.get("original"):
                v = _ver(value.split()[-1], 4) if value.split() else ()
                o = current["original"].lower()
                newest[o] = max(newest.get(o, ()), v)
            if name == "status":
                s = value.lower()
                if ("outranked" in s or "上位" in s) and current["name"].startswith("oem"):
                    candidates[current["name"]] = dict(current)
    def superseded(c):
        o, v = c.get("original", "").lower(), c.get("version", "").split()
        return bool(o and v) and newest.get(o, ()) > _ver(v[-1], 4)

    result = [c for n, c in sorted(candidates.items()) if n not in in_use and superseded(c)]
    return in_use, result


def driver_store_folder(repo, original, version):
    """DriverStore folder holding `original` with DriverVer ending in `version`."""
    prefix = original.lower() + "_"
    try:
        dirs = [d for d in os.scandir(repo) if d.name.lower().startswith(prefix)]
    except OSError:
        return ""
    for d in dirs:
        inf = Path(d.path, original)
        try:
            data = inf.read_bytes()[:20000]
        except OSError:
            continue
        text = data.decode("utf-16", errors="ignore") if data[:2] in (b"\xff\xfe", b"\xfe\xff") \
            else data.decode("utf-8", errors="ignore")
        m = re.search(r"DriverVer\s*=\s*[^,\r\n]*,\s*([\d.]+)", text, re.IGNORECASE)
        if m and m.group(1) == version:
            return d.path
    return ""


def drivers_probe(devices_text, repo, size_fn):
    _, candidates = superseded_drivers(devices_text)
    items = []
    for c in candidates:
        version = c.get("version", "").split()[-1] if c.get("version") else ""
        folder = driver_store_folder(repo, c.get("original", ""), version) if c.get("original") else ""
        items.append({"path": folder or c["name"], "bytes": size_fn(folder) if folder else 0,
                      "command": f"pnputil /delete-driver {c['name']}",
                      "label": f"{c['name']}（{c.get('original', '?')} {version}）"})
    items.sort(key=lambda i: -i["bytes"])
    evidence = []
    if items:
        top = "、".join(f"{i['label']} {i['bytes'] / GB:.1f} GB" for i in items[:5])
        evidence.append(f"同じドライバーの新しい版が入っていて、どのデバイスにも使われていない旧版 {len(items)} 件（大きい順: {top}）")
    return _result(items, evidence)


# --- pagefile ------------------------------------------------------------------

def pagefile_summary(usage, ram_bytes, automatic):
    allocated = int(usage.get("AllocatedBaseSize", 0)) * MB
    peak = int(usage.get("PeakUsage", 0)) * MB
    evidence = [f"確保 {allocated / GB:.1f} GB", f"起動後の最大使用 {peak / GB:.1f} GB",
                f"搭載メモリ {ram_bytes / GB:.1f} GB"]
    if automatic:
        evidence.append("Windows の自動管理")
    return {"bytes": allocated, "items": [], "evidence": evidence}


# --- runner (real machine, read-only) ------------------------------------------

def _run(argv, timeout=120):
    try:
        cp = subprocess.run(argv, capture_output=True, timeout=timeout)
    except (OSError, subprocess.SubprocessError):
        return ""
    raw = cp.stdout
    for enc in ("utf-8", "mbcs"):
        try:
            return raw.decode(enc)
        except (UnicodeDecodeError, LookupError):
            continue
    return raw.decode("utf-8", errors="replace")


def _pwsh_json(command):
    out = _run(["powershell", "-NoProfile", "-NonInteractive", "-Command",
                f"[Console]::OutputEncoding=[Text.Encoding]::UTF8; {command} | ConvertTo-Json -Compress"])
    try:
        return json.loads(out) if out.strip() else None
    except ValueError:
        return None


def _recycle_bin_bytes():
    import ctypes
    from ctypes import wintypes

    class Info(ctypes.Structure):
        _fields_ = [("cbSize", wintypes.DWORD), ("i64Size", ctypes.c_longlong),
                    ("i64NumItems", ctypes.c_longlong)]

    info = Info()
    info.cbSize = ctypes.sizeof(Info)
    if ctypes.windll.shell32.SHQueryRecycleBinW(None, ctypes.byref(info)) != 0:
        return None
    return info.i64Size, info.i64NumItems


def run_all(env, size_fn):
    home = env.get("USERPROFILE", "")
    local = env.get("LOCALAPPDATA", "")
    roaming = env.get("APPDATA", "")
    out = {}

    nvm_home = env.get("NVM_HOME")
    if nvm_home and os.path.isdir(nvm_home):
        roots = [e.path for e in os.scandir(home) if e.is_dir() and not e.name.startswith(".")
                 and e.name.lower() not in ("appdata",)]
        unreadable = []
        pins = find_node_pins(roots, unreadable=unreadable)
        out["nvm-unused"] = nvm_unused(_run(["cmd", "/c", "nvm", "list"]), nvm_home, pins, size_fn,
                                       pins_complete=not unreadable)

    pw = os.path.join(local, "ms-playwright")
    if os.path.isdir(pw):
        out["playwright-browsers"] = playwright_unused(pw, size_fn)

    ext = os.path.join(home, ".vscode", "extensions")
    if os.path.isdir(ext):
        out["vscode-ext-old"] = vscode_old_extensions(ext, size_fn)

    ws = os.path.join(roaming, "Code", "User", "workspaceStorage")
    onedrive = [env[k] for k in ("OneDrive", "OneDriveCommercial", "OneDriveConsumer", "ONEDRIVE") if env.get(k)]
    if os.path.isdir(ws):
        out["vscode-stale-ws"] = vscode_stale_workspaces(ws, onedrive, size_fn)

    devices = _run(["pnputil", "/enum-devices", "/drivers"], timeout=300)
    if devices:
        repo = os.path.join(env.get("SYSTEMROOT", r"C:\Windows"), "System32", "DriverStore", "FileRepository")
        out["driverstore-old"] = drivers_probe(devices, repo, size_fn)

    usage = _pwsh_json("Get-CimInstance Win32_PageFileUsage | Select-Object Name,AllocatedBaseSize,PeakUsage")
    cs = _pwsh_json("Get-CimInstance Win32_ComputerSystem | Select-Object AutomaticManagedPagefile,TotalPhysicalMemory")
    if isinstance(usage, list):
        usage = usage[0] if usage else None
    if usage and cs:
        out["pagefile"] = pagefile_summary(usage, int(cs.get("TotalPhysicalMemory", 0)),
                                           bool(cs.get("AutomaticManagedPagefile")))

    rb = _recycle_bin_bytes()
    if rb:
        out["recycle-bin"] = {"bytes": rb[0], "items": [], "evidence": [f"{rb[1]} 項目"]}
    return out


def main(argv=None):
    sys.path.insert(0, str(Path(__file__).resolve().parent))
    import scan

    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--out", required=True)
    args = ap.parse_args(argv)
    result = run_all(dict(os.environ), lambda p: scan.size_tree(p)["bytes"])
    Path(args.out).write_text(json.dumps(result, ensure_ascii=False, indent=1), encoding="utf-8")
    print(f"probes: {', '.join(result)} -> {args.out}", file=sys.stderr)


if __name__ == "__main__":
    main()
