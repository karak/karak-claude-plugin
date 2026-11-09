"""Execute approved rows of a disk-saver plan. The only module allowed to remove files.

Usage:
  python execute.py --plan plan.json --hash <plan_hash shown at approval> --ids id1,id2 --out result.json

Rules (see SKILL.md): only rows in the proposal section, not held back, with method kind
delete / recycle / command; every path re-checked against the protected list; process gates
re-checked right before each row and treated as closed when the process list is unavailable;
commands must pass the allowlist. Never kills processes and never elevates.
"""
import argparse
import ctypes
import json
import os
import shutil
import stat
import subprocess
import sys
import time
from ctypes import wintypes
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent / "scripts"))

import classify  # noqa: E402
import policy  # noqa: E402
import scan  # noqa: E402

MAX_PLAN_AGE_S = 3600
EXECUTABLE_KINDS = {"delete", "recycle", "command"}


def _free(env):
    try:
        return scan._disk(env)["free"]
    except OSError:
        return 0


def _delete_tree(path):
    """Remove a regenerable cache permanently; skips files in use. Returns error text or ''."""
    errors = []

    def onexc(func, p, exc):
        if isinstance(exc, PermissionError):
            try:
                os.chmod(p, stat.S_IWRITE)
                func(p)
                return
            except OSError as again:
                exc = again
        errors.append(f"{p}: {exc}")

    st = os.stat(path, follow_symlinks=False)
    if stat.S_ISDIR(st.st_mode) and not (st.st_file_attributes & stat.FILE_ATTRIBUTE_REPARSE_POINT):
        shutil.rmtree(path, onexc=onexc)
    else:
        try:
            os.remove(path)
        except OSError as exc:
            errors.append(f"{path}: {exc}")
    return "; ".join(errors[:3]) + (f" ほか {len(errors) - 3} 件" if len(errors) > 3 else "")


class _SHFILEOPSTRUCTW(ctypes.Structure):
    _fields_ = [("hwnd", wintypes.HWND), ("wFunc", wintypes.UINT), ("pFrom", wintypes.LPCWSTR),
                ("pTo", wintypes.LPCWSTR), ("fFlags", ctypes.c_uint16), ("fAnyOperationsAborted", wintypes.BOOL),
                ("hNameMappings", ctypes.c_void_p), ("lpszProgressTitle", wintypes.LPCWSTR)]


def recycle(path):
    """Move a path to the Recycle Bin (undoable)."""
    FO_DELETE, FOF_SILENT, FOF_NOCONFIRMATION, FOF_ALLOWUNDO, FOF_NOERRORUI = 3, 0x4, 0x10, 0x40, 0x400
    op = _SHFILEOPSTRUCTW(wFunc=FO_DELETE, pFrom=os.path.abspath(path) + "\0",
                          fFlags=FOF_SILENT | FOF_NOCONFIRMATION | FOF_ALLOWUNDO | FOF_NOERRORUI)
    rc = ctypes.windll.shell32.SHFileOperationW(ctypes.byref(op))
    if rc != 0 or op.fAnyOperationsAborted:
        raise OSError(f"ごみ箱への移動に失敗（コード {rc:#x}）")
    return 0, ""


def find_tool(name):
    """Absolute path of a tool found on PATH only (never the current folder), or None."""
    found = shutil.which(name, path=os.environ.get("PATH", ""))
    return found if found and os.path.isabs(found) else None


def run_command(argv):
    cp = subprocess.run(argv, capture_output=True, text=True, encoding="mbcs", errors="replace", timeout=1800,
                        cwd=os.path.dirname(argv[0]))
    return cp.returncode, (cp.stdout + cp.stderr)[-2000:]


def _gate_problem(row, running_fn):
    gates = [g.partition(":")[2] for g in row.get("gates", []) if g.startswith("process_not_running:")]
    if not gates:
        return None
    running = running_fn()
    if running is None:
        return "起動中のアプリを確認できないため実行しない"
    running = {r.lower() for r in running}
    busy = [g for g in gates if g.lower() in running]
    return f"{'、'.join(busy)} が起動中のため実行しない（終了してから再スキャン）" if busy else None


def _size(path):
    return scan.size_tree(path)["bytes"] if os.path.lexists(path) else 0


def recycle_bin_problem(path, size):
    """Why moving `path` to the Recycle Bin would not be undoable, or None (read-only check)."""
    import winreg
    root = os.path.splitdrive(os.path.abspath(path))[0] + "\\"
    buf = ctypes.create_unicode_buffer(64)
    if not ctypes.windll.kernel32.GetVolumeNameForVolumeMountPointW(root, buf, 64):
        return "ごみ箱の設定を確認できないため移動しない"
    guid = buf.value[buf.value.find("{"):buf.value.find("}") + 1]
    key = r"Software\Microsoft\Windows\CurrentVersion\Explorer\BitBucket\Volume" + "\\" + guid
    try:
        with winreg.OpenKey(winreg.HKEY_CURRENT_USER, key) as k:
            nuke = winreg.QueryValueEx(k, "NukeOnDelete")[0]
            cap_mb = winreg.QueryValueEx(k, "MaxCapacity")[0]
    except OSError:
        return "ごみ箱の設定を確認できないため移動しない"
    if nuke:
        return "このドライブのごみ箱は「すぐに削除」に設定されているため移動しない"
    if size > cap_mb * 1024 * 1024:
        return "ごみ箱の最大サイズを超えるため（完全削除になる）移動しない"
    return None


def _run_row(row, env, running_fn, runner, recycler, recycle_check=None, which=None):
    results = []
    kind = row["method"]["kind"]

    def out(target, status, error="", freed=0):
        results.append({"id": row["id"], "target": target, "status": status, "error": error, "freed": freed})

    if row.get("section") != "propose" or kind not in EXECUTABLE_KINDS:
        out(row["id"], "refused", "提案以外の行（助言・判断待ち・管理者向け・見送り）は実行しない")
        return results
    if row.get("blocked"):
        out(row["id"], "refused", row["blocked"])
        return results
    gate = _gate_problem(row, running_fn)
    if gate:
        out(row["id"], "refused", gate)
        return results

    details = row.get("item_details") or [{"path": p} for p in row.get("items", [])]
    if kind == "command":
        per_item = [d["command"] for d in details if d.get("command")]
        commands = per_item or [row["method"]["command"]]
        for command in commands:
            problems = policy.command_violations(command)
            if problems:
                out(command, "refused", "; ".join(problems))
                continue
            tokens = command.split(" ")
            tool = (which or find_tool)(tokens[0])
            if not tool:
                out(command, "refused", f"{tokens[0]} が PATH 上に見つからない")
                continue
            before = _free(env)
            try:
                rc, text = runner([tool] + tokens[1:])
            except (OSError, subprocess.SubprocessError) as exc:
                out(command, "failed", str(exc))
                continue
            freed = max(0, _free(env) - before)
            out(command, "done" if rc == 0 else "failed", "" if rc == 0 else text, freed)
        return results

    for d in details:
        path = d["path"]
        if not os.path.isabs(path):
            out(path, "refused", "絶対パスではない")
            continue
        reason = classify.protected_reason(path, env)
        if reason:
            out(path, "refused", f"保護対象: {reason}")
            continue
        if not os.path.lexists(path):
            out(path, "done", "既に存在しない")
            continue
        size = _size(path)
        if kind == "recycle":
            problem = (recycle_check or recycle_bin_problem)(path, size)
            if problem:
                out(path, "refused", problem)
                continue
        try:
            error = _delete_tree(path) if kind == "delete" else (recycler(path) and "")
        except OSError as exc:
            out(path, "failed", str(exc))
            continue
        remaining = _size(path)
        if os.path.lexists(path):
            out(path, "partial" if remaining < size else "failed",
                error or "削除後も残っている（使用中のファイルなど）", size - remaining)
        else:
            out(path, "done", "", size)
    return results


def execute(plan, approved, *, env, running_fn, runner, recycler, now=None, recycle_check=None, which=None):
    now = time.time() if now is None else now
    result = {"refused": None, "results": [], "free_before": _free(env), "free_after": 0}
    rows = plan.get("rows", [])
    if approved.get("plan_hash") != plan.get("plan_hash") or classify.plan_hash(rows) != plan.get("plan_hash"):
        result["refused"] = "承認した計画と実行しようとしている計画が一致しないため実行しない"
    elif now - plan.get("created_at", 0) > MAX_PLAN_AGE_S:
        result["refused"] = "計画が 1 時間以上前のもの。再スキャンしてから承認し直す"
    else:
        wanted = {i.strip() for i in approved.get("ids", []) if i.strip()}
        known = {r["id"] for r in rows}
        for unknown in sorted(wanted - known):
            result["results"].append({"id": unknown, "target": unknown, "status": "refused",
                                      "error": "計画にない id", "freed": 0})
        for row in rows:
            if row["id"] in wanted:
                result["results"].extend(_run_row(row, env, running_fn, runner, recycler, recycle_check, which))
    result["free_after"] = _free(env)
    return result


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--plan", required=True)
    ap.add_argument("--hash", required=True)
    ap.add_argument("--ids", required=True)
    ap.add_argument("--out", required=True)
    args = ap.parse_args(argv)
    plan = json.loads(Path(args.plan).read_text(encoding="utf-8"))
    approved = {"plan_hash": args.hash, "ids": [i for i in args.ids.split(",") if i]}
    result = execute(plan, approved, env=dict(os.environ), running_fn=classify.running_processes,
                     runner=run_command, recycler=recycle)
    Path(args.out).write_text(json.dumps(result, ensure_ascii=False, indent=1), encoding="utf-8")
    gb = 1024 ** 3
    print(f"free {result['free_before'] / gb:.1f} GB -> {result['free_after'] / gb:.1f} GB", file=sys.stderr)
    if result["refused"]:
        print("refused: " + result["refused"], file=sys.stderr)
    for r in result["results"]:
        print(f"[{r['status']}] {r['id']} {r['target']} {r['freed'] / gb:.2f} GB {r['error']}", file=sys.stderr)


if __name__ == "__main__":
    main()
