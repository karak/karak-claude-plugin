"""Classify a scan against the catalog, score it and render a Japanese report.

Pure analysis: never deletes, moves or renames anything.
Usage: python classify.py scan.json --report report.md --plan plan.json [--probes probes.json]
"""
import argparse
import csv
import datetime as dt
import hashlib
import io
import json
import os
import subprocess
import sys
import time
from pathlib import Path

from scan import expand_vars  # noqa: F401  (re-exported for callers/tests)

GB = 1024 ** 3
BASE_CONFIDENCE = {"FREE": 0.95, "CHEAP": 0.85, "COSTLY": 0.70, "PROJECT": 0.50}
ACTIONABLE = set(BASE_CONFIDENCE)
COST_LABEL = {1: "なし（自動で再生成）", 1.5: "小（必要分だけ再ダウンロード）", 3: "中（大きな再ダウンロード）",
              5: "大（再ビルドが必要）"}

_USER_DIRS = ("Documents", "Desktop", "Pictures", "Downloads", "Videos", "Music")
_CREDENTIAL_DIRS = (".ssh", ".gnupg", ".aws", ".azure", ".kube", ".docker\\contexts")
_HISTORY_DIRS = (".codex\\sessions", ".claude\\projects")
_SYSTEM_FILES = ("pagefile.sys", "swapfile.sys", "hiberfil.sys")
_VIRTUAL_DISKS = (".vhdx", ".vhd", ".vmdk", ".qcow2")


def _norm(path):
    return os.path.normcase(os.path.normpath(path))


def _under(path, root):
    p, r = _norm(path), _norm(root)
    return p == r or p.startswith(r.rstrip("\\") + "\\")


def protected_reason(path, env):
    """Why a path must never be proposed for removal, or None."""
    home = env.get("USERPROFILE", "")
    n = _norm(path)
    for d in _USER_DIRS:
        if home and _under(path, os.path.join(home, d)):
            return f"ユーザーの {d} フォルダー"
    for key in ("ONEDRIVE", "ONEDRIVECOMMERCIAL", "ONEDRIVECONSUMER"):
        root = env.get(key) or env.get(key.title())
        if root and _under(path, root):
            return "OneDrive の同期フォルダー"
    if home and _under(path, home):
        rel = os.path.relpath(n, _norm(home))
        if rel.split("\\", 1)[0].startswith("onedrive"):
            return "OneDrive の同期フォルダー"
        for d in _CREDENTIAL_DIRS:
            if _under(path, os.path.join(home, d)):
                return "認証情報"
        for d in _HISTORY_DIRS:
            if _under(path, os.path.join(home, d)):
                return "AI ツールの会話履歴"
    pd = env.get("PROGRAMDATA")
    if pd and _under(path, os.path.join(pd, "P-Pointer4")):
        return "セキュリティソフトのデータ"
    if "\\trend micro" in n:
        return "セキュリティソフトのデータ"
    if "\\system volume information" in n:
        return "システムの復元領域"
    base = os.path.basename(n)
    if base in _SYSTEM_FILES:
        return "システムファイル"
    if base.endswith(_VIRTUAL_DISKS):
        return "仮想ディスク（削除せず縮小のみ）"
    if base.endswith(".ppkg"):
        return "PC のプロビジョニングパッケージ"
    return None


def method_label(method):
    kind = method["kind"]
    if kind == "delete":
        return "ごみ箱を経由せず完全削除"
    if kind == "recycle":
        return "ごみ箱へ移動"
    if kind == "command":
        return f"コマンド `{method['command']}`"
    if kind == "handoff_admin":
        return f"管理者として実行 `{method['command']}`"
    if kind == "advice":
        return "助言のみ"
    return "対象外"


def _age_multiplier(age_days):
    if age_days is None:
        return 1.0
    if age_days < 7:
        return 0.6
    if age_days < 30:
        return 0.8
    if age_days < 90:
        return 0.9
    return 1.0


def _gate_block(entry, running):
    gated = [g for g in entry.get("gates", []) if g.startswith("process_not_running:")]
    if gated and running is None:
        return "起動中のアプリを確認できないため保留"
    for gate in entry.get("gates", []):
        kind, _, arg = gate.partition(":")
        if kind == "process_not_running" and arg.lower() in running:
            return f"{arg} が起動中のため保留（終了後に再スキャン）"
    return None


def build_rows(catalog, scan, env, running, now, probes=None):
    probes = probes or {}
    running = None if running is None else {r.lower() for r in running}
    scanned = {e["id"]: e for e in scan.get("entries", [])}
    rows = []
    for entry in catalog["entries"]:
        s = scanned.get(entry["id"], {"bytes": 0, "files": 0, "items": [], "newest_mtime": 0, "partial": False})
        probe = probes.get(entry["id"], {})
        cls = entry["class"]
        nbytes = probe.get("bytes", s["bytes"])
        items = probe.get("items", s.get("items", []))
        newest = s.get("newest_mtime") or 0
        age_days = (now - newest) / 86400 if newest else None
        evidence = list(probe.get("evidence", []))
        named = [i.get("label") or os.path.basename(i["path"]) for i in probe.get("items", [])]
        if named and not any(n in " ".join(evidence) for n in named):
            shown = "、".join(named[:8]) + (f" ほか {len(named) - 8} 件" if len(named) > 8 else "")
            evidence.append(f"対象: {shown}")
        if age_days is not None:
            evidence.append(f"最終更新 {int(age_days)}日前")
        if s.get("partial"):
            evidence.append("計測が途中で打ち切られたため実際はこれ以上")
        row = {
            "id": entry["id"], "title_ja": entry["title_ja"], "class": cls,
            "why_ja": entry.get("why_ja", ""), "regen_ja": entry.get("regen_ja", "-"),
            "advice_ja": entry.get("advice_ja", ""), "bytes": nbytes, "files": s.get("files", 0),
            "admin": bool(entry.get("admin")), "method": entry["method"],
            "method_label": method_label(entry["method"]), "rebuild_cost": entry.get("rebuild_cost"),
            "items": [i["path"] for i in items], "evidence": evidence, "blocked": None,
            "item_details": [{k: i[k] for k in ("path", "bytes", "command", "label") if k in i} for i in items],
            "gates": list(entry.get("gates", [])),
            "confidence": 0.0, "priority": 0.0, "newest_mtime": newest,
        }
        reason = next((r for r in (protected_reason(p, env) for p in row["items"]) if r), None)
        if cls in ACTIONABLE and reason:
            row["section"] = "protected"
            row["protected_reason"] = reason
        elif cls == "PRESERVE":
            row["section"] = "protected"
            row["protected_reason"] = entry.get("why_ja", "保持")
        elif cls == "DECISION":
            row["section"] = "decision"
        elif cls == "ADVICE":
            row["section"] = "advice"
        elif probe.get("skip"):
            row["section"] = "skipped"
        elif nbytes <= 0:
            row["section"] = "empty"
        else:
            row["section"] = "propose"
            row["blocked"] = _gate_block(entry, running)
            conf = BASE_CONFIDENCE[cls] * _age_multiplier(age_days) * probe.get("confidence_multiplier", 1.0)
            row["confidence"] = 0.0 if row["blocked"] else round(min(conf, 1.0), 3)
            row["priority"] = nbytes / GB * row["confidence"] / entry["rebuild_cost"]
            if row["blocked"]:
                row["evidence"].append(row["blocked"])
        rows.append(row)

    def key(r):
        if r["section"] == "propose":
            return (0, -r["priority"], r["admin"], r["files"], r["newest_mtime"])
        order = {"decision": 1, "advice": 2, "skipped": 3, "protected": 4, "empty": 5}[r["section"]]
        return (order, -r["bytes"], False, 0, 0)

    rows.sort(key=key)
    return rows


def totals(rows):
    proposed = sum(r["bytes"] for r in rows if r["section"] == "propose" and not r["blocked"])
    held = sum(r["bytes"] for r in rows if r["section"] == "propose" and r["blocked"])
    return {"proposed": proposed, "held": held}


def _gb(n):
    return f"{n / GB:.1f} GB"


def _cell(text):
    return str(text).replace("|", "／").replace("\n", " ")


def render_report(rows, scan, now):
    disk = scan.get("disk", {})
    free, total = disk.get("free", 0), disk.get("total", 0)
    t = totals(rows)
    when = dt.datetime.fromtimestamp(scan.get("scanned_at", now))
    out = ["# ディスク容量の診断レポート", ""]
    pct = f"（{free / total * 100:.0f}%）" if total else ""
    out.append(f"- 空き容量: **{_gb(free)}** / 合計 {_gb(total)}{pct}")
    out.append(f"- スキャン日時: {when:%Y-%m-%d %H:%M}" +
               (f"（所要 {scan['seconds']} 秒）" if "seconds" in scan else ""))
    age_h = (now - scan.get("scanned_at", now)) / 3600
    if age_h > 24:
        out.append(f"\n> ⚠ スキャン結果が古いです（{age_h:.0f} 時間前）。再スキャンしてから判断してください。")
    out.append("")

    props = [r for r in rows if r["section"] == "propose"]
    out.append(f"## 1. 提案（承認待ち） — 今すぐ回収できる見込み {_gb(t['proposed'])}")
    out.append("")
    if props:
        out.append("| # | 対象 | サイズ | 確度 | 方法 | 再取得の手間 | 根拠 |")
        out.append("|---|---|---|---|---|---|---|")
        for i, r in enumerate(props, 1):
            conf = "保留" if r["blocked"] else f"{r['confidence']:.2f}"
            admin = "（要管理者）" if r["admin"] else ""
            out.append(f"| {i} | {_cell(r['title_ja'])}{admin} | {_gb(r['bytes'])} | {conf} | "
                       f"{_cell(r['method_label'])} | {_cell(r['regen_ja'])} | "
                       f"{_cell('；'.join([r.get('why_ja', '')] + r['evidence']))} |")
        if t["held"]:
            out.append("")
            out.append(f"保留中（アプリ起動中など）: {_gb(t['held'])}。該当アプリを完全に終了してから再スキャンすると提案に入ります。")
    else:
        out.append("提案できる項目はありません。")
    out.append("")

    for section, title, note in (
        ("decision", "## 2. 判断が必要", "削除すると困る可能性があるため、使い方を確認してから決めてください。"),
        ("advice", "## 3. 助言のみ", "スキルからは実行しません。設定変更や管理者操作の手順だけを示します。"),
    ):
        part = [r for r in rows if r["section"] == section]
        out.append(title)
        out.append("")
        out.append(note)
        out.append("")
        if part:
            out.append("| 対象 | サイズ | 内容 | 選択肢・手順 |")
            out.append("|---|---|---|---|")
            for r in part:
                admin = "（要管理者）" if r["admin"] else ""
                detail = "；".join([r.get("why_ja", "")] + r["evidence"])
                out.append(f"| {_cell(r['title_ja'])}{admin} | {_gb(r['bytes'])} | {_cell(detail)} | "
                           f"{_cell(r.get('advice_ja', ''))} |")
        else:
            out.append("該当なし。")
        out.append("")

    skipped = [r for r in rows if r["section"] == "skipped"]
    if skipped:
        out.append("## 調査を見送った項目")
        out.append("")
        for r in skipped:
            out.append(f"- {r['title_ja']}: {'；'.join(r['evidence'])}")
        out.append("")
    prot = [r for r in rows if r["section"] == "protected"]
    if prot:
        out.append("## 4. 保護対象（提案しません）")
        out.append("")
        for r in prot:
            out.append(f"- {r['title_ja']}（{_gb(r['bytes'])}）: {r.get('protected_reason', '')}")
        out.append("")
    empty = [r["title_ja"] for r in rows if r["section"] == "empty"]
    if empty:
        out.append(f"<sub>該当データなし: {'、'.join(empty)}</sub>")
        out.append("")
    out.append("<sub>サイズは論理サイズです。ごみ箱へ移動した分は、ごみ箱を空にするまで空き容量に反映されません。</sub>")
    return "\n".join(out) + "\n"


def running_processes():
    """Image names of running processes (read-only, via tasklist); None when unavailable."""
    try:
        cp = subprocess.run(["tasklist", "/FO", "CSV", "/NH"], capture_output=True, text=True,
                            encoding="mbcs", errors="replace", timeout=30)
    except (OSError, subprocess.SubprocessError):
        return None
    names = {row[0].lower() for row in csv.reader(io.StringIO(cp.stdout)) if row}
    return names if cp.returncode == 0 and names else None


def plan_hash(rows):
    payload = json.dumps([[r["id"], r["section"], r["items"], r["method"],
                           [[i.get("path"), i.get("command")] for i in r.get("item_details", [])],
                           r.get("gates", []), r.get("blocked")] for r in rows if r["section"] == "propose"],
                         ensure_ascii=False, sort_keys=True)
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()[:16]


def main(argv=None):
    here = Path(__file__).resolve().parent
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("scan")
    ap.add_argument("--catalog", default=str(here.parent / "catalog" / "windows.json"))
    ap.add_argument("--probes")
    ap.add_argument("--report", required=True)
    ap.add_argument("--plan", required=True)
    args = ap.parse_args(argv)
    catalog = json.loads(Path(args.catalog).read_text(encoding="utf-8"))
    scan = json.loads(Path(args.scan).read_text(encoding="utf-8"))
    probes = json.loads(Path(args.probes).read_text(encoding="utf-8")) if args.probes else {}
    now = time.time()
    rows = build_rows(catalog, scan, env=dict(os.environ), running=running_processes(), now=now, probes=probes)
    Path(args.report).write_text(render_report(rows, scan, now), encoding="utf-8")
    plan = {"plan_hash": plan_hash(rows), "created_at": now, "rows": rows}
    Path(args.plan).write_text(json.dumps(plan, ensure_ascii=False, indent=1), encoding="utf-8")
    print(f"report -> {args.report}\nplan -> {args.plan} (hash {plan['plan_hash']})", file=sys.stderr)


if __name__ == "__main__":
    main()
