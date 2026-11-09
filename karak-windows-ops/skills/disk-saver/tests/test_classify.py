import os
import time

import pytest

import classify

GB = 1024 ** 3
DAY = 86400
NOW = 1_800_000_000.0


def entry(id, cls="FREE", cost=1, kind="delete", gates=(), admin=False, paths=None, **extra):
    method = {"kind": kind}
    if kind in ("command", "handoff_admin"):
        method["command"] = extra.pop("command", "npm cache verify")
    return {
        "id": id, "title_ja": f"対象{id}", "why_ja": "理由", "regen_ja": "再生成",
        "class": cls, "rebuild_cost": cost, "method": method,
        "gates": list(gates), "admin": admin,
        "paths": paths or [rf"%LOCALAPPDATA%\{id}"], **extra,
    }


def scanned(id, bytes_, age_days=200, files=10, path=None):
    return {"id": id, "bytes": bytes_, "files": files, "partial": False,
            "newest_mtime": NOW - age_days * DAY,
            "items": [{"path": path or f"C:/x/{id}", "bytes": bytes_}] if bytes_ else []}


def rows_for(entries, scans, fake_env, running=()):
    catalog = {"entries": entries}
    scan = {"scanned_at": NOW, "disk": {"free": 10 * GB, "total": 100 * GB}, "entries": scans}
    return classify.build_rows(catalog, scan, env=fake_env, running=set(running), now=NOW)


def by_id(rows):
    return {r["id"]: r for r in rows}


@pytest.mark.parametrize("rel", [
    r"OneDrive - Org\Desktop\proj",
    r"Documents\report.docx",
    r"Desktop\a",
    r"Downloads\setup.exe",
    r".ssh\id_ed25519",
])
def test_user_documents_credentials_and_cloud_folders_are_protected(fake_env, rel):
    path = os.path.join(fake_env["USERPROFILE"], rel)
    assert classify.protected_reason(path, fake_env)


def test_security_software_data_is_protected(fake_env):
    path = os.path.join(fake_env["PROGRAMDATA"], "P-Pointer4", "scanner.db")
    assert classify.protected_reason(path, fake_env)


def test_ordinary_cache_folder_is_not_protected(fake_env):
    path = os.path.join(fake_env["LOCALAPPDATA"], "npm-cache", "_npx")
    assert classify.protected_reason(path, fake_env) is None


def test_item_owned_by_a_running_app_is_held_back_with_the_reason(fake_env):
    rows = rows_for([entry("vsix", gates=["process_not_running:Code.exe"])],
                    [scanned("vsix", 2 * GB)], fake_env, running={"code.exe"})

    row = by_id(rows)["vsix"]
    assert row["blocked"] and "Code.exe" in row["blocked"]
    assert row["confidence"] == 0
    assert classify.totals(rows)["proposed"] == 0


def test_items_are_ranked_by_reclaimable_size_times_confidence_over_rebuild_cost(fake_env):
    rows = rows_for([entry("big", cost=3), entry("small", cost=1)],
                    [scanned("big", 6 * GB), scanned("small", 3 * GB)], fake_env)

    proposals = [r["id"] for r in rows if r["section"] == "propose"]
    assert proposals == ["small", "big"]


def test_equal_priority_prefers_items_that_need_no_administrator(fake_env):
    rows = rows_for([entry("adm", admin=True, kind="handoff_admin",
                           command="pnputil /delete-driver oem1.inf"),
                     entry("usr")],
                    [scanned("adm", 2 * GB), scanned("usr", 2 * GB)], fake_env)

    proposals = [r["id"] for r in rows if r["section"] == "propose"]
    assert proposals == ["usr", "adm"]


def test_recently_used_data_gets_lower_confidence_than_long_untouched_data(fake_env):
    rows = rows_for([entry("fresh"), entry("stale")],
                    [scanned("fresh", GB, age_days=2), scanned("stale", GB, age_days=200)], fake_env)

    r = by_id(rows)
    assert r["fresh"]["confidence"] < r["stale"]["confidence"]
    assert any("日前" in ev for ev in r["fresh"]["evidence"])


def test_decisions_and_advice_are_listed_separately_and_never_counted_as_savings(fake_env):
    rows = rows_for([entry("vm", cls="DECISION", kind="advice"),
                     entry("pf", cls="ADVICE", kind="advice"),
                     entry("c")],
                    [scanned("vm", 8 * GB), scanned("pf", 20 * GB), scanned("c", GB)], fake_env)

    r = by_id(rows)
    assert r["vm"]["section"] == "decision"
    assert r["pf"]["section"] == "advice"
    assert classify.totals(rows)["proposed"] == GB


def test_empty_targets_are_not_proposed(fake_env):
    rows = rows_for([entry("none")], [scanned("none", 0)], fake_env)

    assert all(r["section"] != "propose" for r in rows)


def test_target_resolving_into_a_protected_folder_is_never_proposed(fake_env):
    docs = os.path.join(fake_env["USERPROFILE"], "Documents", "cache")
    rows = rows_for([entry("bad", paths=[r"~\Documents\cache"])],
                    [scanned("bad", 5 * GB, path=docs)], fake_env)

    row = by_id(rows)["bad"]
    assert row["section"] == "protected"
    assert classify.totals(rows)["proposed"] == 0


def test_permanent_deletion_is_spelled_out_in_the_method(fake_env):
    rows = rows_for([entry("d", kind="delete"), entry("r", kind="recycle")],
                    [scanned("d", GB), scanned("r", GB)], fake_env)

    r = by_id(rows)
    assert "ごみ箱を経由せず完全削除" in r["d"]["method_label"]
    assert "ごみ箱" in r["r"]["method_label"] and "完全削除" not in r["r"]["method_label"]


def test_rows_found_by_a_usage_probe_name_each_concrete_item(fake_env):
    probe = {"nv": {"bytes": 2 * GB, "evidence": ["使用中 24.22.1"], "items": [
        {"path": r"C:\nvm\v22.22.0", "bytes": GB, "command": "nvm uninstall 22.22.0"},
        {"path": r"C:\nvm\v24.18.0", "bytes": GB, "command": "nvm uninstall 24.18.0"}]}}
    catalog = {"entries": [entry("nv", cls="COSTLY", kind="command", command="nvm uninstall", paths=[])]}
    scan = {"scanned_at": NOW, "disk": {}, "entries": []}

    rows = classify.build_rows(catalog, scan, env=fake_env, running=set(), now=NOW, probes=probe)

    row = by_id(rows)["nv"]
    assert row["section"] == "propose" and row["bytes"] == 2 * GB
    text = " ".join(row["evidence"])
    assert "v22.22.0" in text and "v24.18.0" in text and "使用中 24.22.1" in text


def test_rows_owned_by_apps_are_held_when_running_apps_cannot_be_listed(fake_env):
    catalog = {"entries": [entry("vsix", gates=["process_not_running:Code.exe"])]}
    scan = {"scanned_at": NOW, "disk": {}, "entries": [scanned("vsix", 2 * GB)]}

    rows = classify.build_rows(catalog, scan, env=fake_env, running=None, now=NOW)

    assert rows[0]["blocked"] and classify.totals(rows)["proposed"] == 0
