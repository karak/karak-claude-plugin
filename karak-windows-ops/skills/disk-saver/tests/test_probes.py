import subprocess
import pytest
import json
import os
from pathlib import Path

from conftest import write_file
import probes

FIX = Path(__file__).parent / "fixtures"


def size(path):
    return sum(f.stat().st_size for f in Path(path).rglob("*") if f.is_file())


def item_names(result):
    return sorted(os.path.basename(i["path"]) for i in result["items"])


# --- nvm -------------------------------------------------------------------

NVM_LIST = """
  * 24.22.1 (Currently using 64-bit executable)
    24.18.0
    22.23.4
    22.22.0
    20.11.0
"""


def make_nvm(tmp_path):
    for v in ("24.22.1", "24.18.0", "22.23.4", "22.22.0", "20.11.0"):
        write_file(tmp_path / f"v{v}" / "node.exe", 100)
    return tmp_path


def test_node_version_in_use_and_newest_of_each_major_are_kept(tmp_path):
    result = probes.nvm_unused(NVM_LIST, str(make_nvm(tmp_path)), pins=set(), size_fn=size)

    assert item_names(result) == ["v22.22.0", "v24.18.0"]


def test_node_version_pinned_by_a_project_is_kept(tmp_path):
    result = probes.nvm_unused(NVM_LIST, str(make_nvm(tmp_path)), pins={"22.22.0"}, size_fn=size)

    assert "v22.22.0" not in item_names(result)


def test_only_installed_major_version_is_kept_even_when_old(tmp_path):
    result = probes.nvm_unused(NVM_LIST, str(make_nvm(tmp_path)), pins=set(), size_fn=size)

    assert "v20.11.0" not in item_names(result)


def test_each_unused_node_version_gets_its_own_uninstall_command(tmp_path):
    result = probes.nvm_unused(NVM_LIST, str(make_nvm(tmp_path)), pins=set(), size_fn=size)

    commands = sorted(i["command"] for i in result["items"])
    assert commands == ["nvm uninstall 22.22.0", "nvm uninstall 24.18.0"]
    assert result["bytes"] == 200


def test_project_pins_are_read_from_nvmrc_and_node_version_files(tmp_path):
    (tmp_path / "app").mkdir()
    (tmp_path / "app" / ".nvmrc").write_text("v22.22.0\n")
    (tmp_path / "svc").mkdir()
    (tmp_path / "svc" / ".node-version").write_text("20.11.0")

    assert probes.find_node_pins([str(tmp_path)]) == {"22.22.0", "20.11.0"}


# --- Playwright --------------------------------------------------------------

def make_playwright(tmp_path, live_revisions, dead_revisions):
    root = tmp_path / "ms-playwright"
    for rev in ("1223", "1234", "1254"):
        write_file(root / f"chromium-{rev}" / "chrome.exe", 1000)
        write_file(root / f"chromium_headless_shell-{rev}" / "shell.exe", 500)
    links = root / ".links"
    links.mkdir(parents=True)
    for i, rev in enumerate(live_revisions):
        core = tmp_path / f"proj{i}" / "node_modules" / "playwright-core"
        core.mkdir(parents=True)
        (core / "browsers.json").write_text(json.dumps({"browsers": [
            {"name": "chromium", "revision": rev},
            {"name": "chromium-headless-shell", "revision": rev}]}))
        (links / f"live{i}").write_text(str(core))
    for i, rev in enumerate(dead_revisions):
        (links / f"dead{i}").write_text(str(tmp_path / f"gone{i}" / "playwright-core"))
    return root


def test_browser_revisions_used_by_an_existing_project_are_kept(tmp_path):
    root = make_playwright(tmp_path, live_revisions=["1234", "1254"], dead_revisions=[])

    result = probes.playwright_unused(str(root), size_fn=size)

    assert item_names(result) == ["chromium-1223", "chromium_headless_shell-1223"]
    assert result["bytes"] == 1500


def test_browser_revisions_referenced_only_by_deleted_projects_are_proposed(tmp_path):
    root = make_playwright(tmp_path, live_revisions=["1254"], dead_revisions=["1234"])

    result = probes.playwright_unused(str(root), size_fn=size)

    assert "chromium-1234" in item_names(result)
    assert "chromium-1254" not in item_names(result)


def test_without_any_readable_project_link_nothing_is_proposed(tmp_path):
    root = make_playwright(tmp_path, live_revisions=[], dead_revisions=["1234"])

    result = probes.playwright_unused(str(root), size_fn=size)

    assert result["items"] == []


# --- VS Code ---------------------------------------------------------------

def make_extensions(tmp_path, referenced):
    ext = tmp_path / "extensions"
    for d in ("ms-python.python-2026.1.0", "ms-python.python-2026.2.0",
              "foo.bar-1.0.0", "baz.qux-0.1.0-win32-x64", "baz.qux-0.2.0-win32-x64"):
        write_file(ext / d / "package.json", 300)
    (ext / "extensions.json").write_text(json.dumps(
        [{"identifier": {"id": d.rsplit("-", 1)[0]}, "relativeLocation": d} for d in referenced]))
    return ext


def test_older_copy_of_an_extension_whose_newer_copy_is_installed_is_proposed(tmp_path):
    ext = make_extensions(tmp_path, ["ms-python.python-2026.2.0", "foo.bar-1.0.0", "baz.qux-0.2.0-win32-x64"])

    result = probes.vscode_old_extensions(str(ext), size_fn=size)

    assert item_names(result) == ["baz.qux-0.1.0-win32-x64", "ms-python.python-2026.1.0"]


def test_extension_listed_as_installed_is_never_proposed(tmp_path):
    ext = make_extensions(tmp_path, ["ms-python.python-2026.1.0", "ms-python.python-2026.2.0",
                                     "foo.bar-1.0.0", "baz.qux-0.1.0-win32-x64", "baz.qux-0.2.0-win32-x64"])

    result = probes.vscode_old_extensions(str(ext), size_fn=size)

    assert result["items"] == []


def test_unlisted_extension_without_an_installed_newer_copy_is_left_alone(tmp_path):
    ext = make_extensions(tmp_path, ["ms-python.python-2026.2.0", "baz.qux-0.2.0-win32-x64"])

    result = probes.vscode_old_extensions(str(ext), size_fn=size)

    assert "foo.bar-1.0.0" not in item_names(result)


def file_uri(path):
    p = str(path).replace("\\", "/")
    drive, rest = p[0], p[2:]
    return f"file:///{drive.lower()}%3A{rest.replace(' ', '%20')}"


def make_workspace(ws, name, content):
    write_file(ws / name / "state.vscdb", 400)
    (ws / name / "workspace.json").write_text(json.dumps(content))


def test_workspace_data_for_a_folder_that_no_longer_exists_is_proposed(tmp_path):
    ws = tmp_path / "workspaceStorage"
    alive = tmp_path / "alive project"
    alive.mkdir()
    make_workspace(ws, "a", {"folder": file_uri(alive)})
    make_workspace(ws, "b", {"folder": file_uri(tmp_path / "deleted project")})

    result = probes.vscode_stale_workspaces(str(ws), onedrive_roots=[], size_fn=size)

    assert item_names(result) == ["b"]


def test_remote_and_multi_root_workspaces_are_never_treated_as_stale(tmp_path):
    ws = tmp_path / "workspaceStorage"
    make_workspace(ws, "remote", {"folder": "vscode-remote://wsl%2Bubuntu/home/x"})
    make_workspace(ws, "multi", {"workspace": file_uri(tmp_path / "gone.code-workspace")})
    make_workspace(ws, "empty", {})

    result = probes.vscode_stale_workspaces(str(ws), onedrive_roots=[], size_fn=size)

    assert result["items"] == []


def test_missing_onedrive_folder_counts_as_stale_only_while_onedrive_is_available(tmp_path):
    onedrive = tmp_path / "OneDrive - Org"
    ws = tmp_path / "workspaceStorage"
    make_workspace(ws, "c", {"folder": file_uri(onedrive / "Desktop" / "old")})

    offline = probes.vscode_stale_workspaces(str(ws), onedrive_roots=[str(onedrive)], size_fn=size)
    onedrive.mkdir()
    online = probes.vscode_stale_workspaces(str(ws), onedrive_roots=[str(onedrive)], size_fn=size)

    assert offline["items"] == []
    assert item_names(online) == ["c"]


# --- drivers ---------------------------------------------------------------

def test_superseded_driver_packages_not_bound_to_any_device_are_listed():
    devices = (FIX / "pnputil_enum_devices_display.txt").read_text(encoding="utf-8")

    in_use, candidates = probes.superseded_drivers(devices)

    assert {"oem66.inf", "oem71.inf"} <= in_use
    assert sorted(c["name"] for c in candidates) == ["oem12.inf", "oem374.inf", "oem377.inf", "oem7.inf"]


def test_drivers_in_use_and_inbox_windows_drivers_are_never_listed():
    devices = (FIX / "pnputil_enum_devices_display.txt").read_text(encoding="utf-8")

    _, candidates = probes.superseded_drivers(devices)

    names = {c["name"] for c in candidates}
    assert not names & {"oem66.inf", "oem71.inf", "display.inf", "rdpidd.inf"}


ENGLISH_DEVICES = """Microsoft PnP Utility

Instance ID:                PCI\\VEN_8086
Device Description:         Intel(R) Graphics
Status:                     Started
Driver Name:                oem66.inf
Extension Driver Names:     oem71.inf
Matching Drivers:
    Driver Name:            oem66.inf
    Original Name:          iigd_dch.inf
    Driver Version:         08/24/2026 32.0.101.8991
    Driver Status:          Best Ranked / Installed

    Driver Name:            oem7.inf
    Original Name:          iigd_dch.inf
    Driver Version:         05/29/2026 32.0.101.8826
    Driver Status:          Outranked
"""


def test_driver_listing_is_understood_in_english_as_well():
    in_use, candidates = probes.superseded_drivers(ENGLISH_DEVICES)

    assert in_use == {"oem66.inf", "oem71.inf"}
    assert [c["name"] for c in candidates] == ["oem7.inf"]


def test_driver_package_size_is_found_from_its_driver_store_folder(tmp_path):
    repo = tmp_path / "FileRepository"
    write_file(repo / "iigd_dch.inf_amd64_aaa" / "big.bin", 5000)
    (repo / "iigd_dch.inf_amd64_aaa" / "iigd_dch.inf").write_text(
        "[Version]\nDriverVer = 05/29/2026,32.0.101.8826\n", encoding="utf-16")
    write_file(repo / "iigd_dch.inf_amd64_bbb" / "big.bin", 7000)
    (repo / "iigd_dch.inf_amd64_bbb" / "iigd_dch.inf").write_text(
        "[Version]\nDriverVer=08/24/2026,32.0.101.8991\n", encoding="utf-8")

    folder = probes.driver_store_folder(str(repo), "iigd_dch.inf", "32.0.101.8826")

    assert os.path.basename(folder) == "iigd_dch.inf_amd64_aaa"


# --- pagefile --------------------------------------------------------------

def test_pagefile_report_compares_allocated_size_with_peak_use_and_memory():
    usage = {"Name": "C:\\pagefile.sys", "AllocatedBaseSize": 21504, "PeakUsage": 2867}
    result = probes.pagefile_summary(usage, ram_bytes=16 * 1024 ** 3, automatic=True)

    assert result["bytes"] == 21504 * 1024 ** 2
    joined = " ".join(result["evidence"])
    assert "21.0 GB" in joined and "2.8 GB" in joined and "自動管理" in joined


ORPHAN_ONLY = ENGLISH_DEVICES + """
Instance ID:                USB\\PRINTER
Device Description:         Printer
Driver Name:                prnms009.inf
Matching Drivers:
    Driver Name:            oem114.inf
    Original Name:          prnms009.inf
    Driver Version:         06/21/2006 10.0.22621.1
    Driver Status:          Outranked
"""


def test_outranked_driver_without_a_newer_version_of_the_same_package_is_not_listed():
    _, candidates = probes.superseded_drivers(ORPHAN_ONLY)

    assert [c["name"] for c in candidates] == ["oem7.inf"]


def test_driver_summary_names_the_largest_packages_and_the_count(tmp_path):
    devices = (FIX / "pnputil_enum_devices_display.txt").read_text(encoding="utf-8")

    result = probes.drivers_probe(devices, str(tmp_path / "missing-repo"), size_fn=size)

    assert len(result["items"]) == 4
    assert all(i["command"].startswith("pnputil /delete-driver oem") for i in result["items"])
    assert "4 件" in " ".join(result["evidence"])


def absent_drive_letter():
    import string
    return next(d for d in reversed(string.ascii_uppercase) if not os.path.exists(f"{d}:\\"))


def test_workspace_on_a_drive_that_is_not_connected_is_not_treated_as_gone(tmp_path):
    ws = tmp_path / "workspaceStorage"
    letter = absent_drive_letter().lower()
    make_workspace(ws, "ext", {"folder": f"file:///{letter}%3A/proj"})

    result = probes.vscode_stale_workspaces(str(ws), onedrive_roots=[], size_fn=size)

    assert result["items"] == []


def test_node_pins_inside_onedrive_folders_are_found(tmp_path):
    app = tmp_path / "OneDrive - Org" / "Desktop" / "app"
    app.mkdir(parents=True)
    (app / ".nvmrc").write_text("22.22.0")

    assert probes.find_node_pins([str(tmp_path)]) == {"22.22.0"}


def test_stale_workspace_rows_name_the_folder_that_was_open(tmp_path, fake_env):
    import classify
    ws = tmp_path / "workspaceStorage"
    gone = tmp_path / "gone project"
    make_workspace(ws, "1a2b3c", {"folder": file_uri(gone)})
    probe = probes.vscode_stale_workspaces(str(ws), onedrive_roots=[], size_fn=size)
    catalog = {"entries": [{"id": "ws", "title_ja": "作業データ", "why_ja": "理由", "regen_ja": "不要",
                            "class": "PROJECT", "rebuild_cost": 1, "paths": [], "method": {"kind": "recycle"}}]}

    rows = classify.build_rows(catalog, {"entries": []}, env=fake_env, running=set(), now=0, probes={"ws": probe})

    assert "gone project" in " ".join(rows[0]["evidence"])


def test_workspace_data_holding_ai_chat_history_is_never_proposed(tmp_path):
    ws = tmp_path / "workspaceStorage"
    make_workspace(ws, "abc", {"folder": file_uri(tmp_path / "gone")})
    write_file(ws / "abc" / "chatSessions" / "session-1.json", 80)

    result = probes.vscode_stale_workspaces(str(ws), onedrive_roots=[], size_fn=size)

    assert result["items"] == []


def test_no_node_version_is_proposed_while_a_project_pin_exists_only_in_the_cloud(tmp_path):
    proj = tmp_path / "home" / "OneDrive - Org" / "proj"
    proj.mkdir(parents=True)
    pin = proj / ".nvmrc"
    pin.write_text("22.22.0")
    subprocess.run(["attrib", "+O", str(pin)], check=True, capture_output=True)
    if not os.stat(pin).st_file_attributes & 0x1000:
        pytest.skip("environment cannot mark a file offline")
    unreadable = []

    pins = probes.find_node_pins([str(tmp_path / "home")], unreadable=unreadable)
    result = probes.nvm_unused(NVM_LIST, str(make_nvm(tmp_path / "nvm")), pins=pins, size_fn=size,
                               pins_complete=not unreadable)

    assert result["items"] == []
    assert any("クラウド" in e for e in result["evidence"])


def test_node_pins_deep_inside_project_trees_are_found(tmp_path):
    deep = tmp_path / "Projects" / "a" / "b" / "c" / "d" / "e" / "f"
    deep.mkdir(parents=True)
    (deep / ".nvmrc").write_text("22.22.0")

    assert probes.find_node_pins([str(tmp_path)]) == {"22.22.0"}


@pytest.mark.parametrize("encoding,raw", [
    ("utf-8-sig", "22.22.0\r\n"),
    ("utf-16", "22.22.0\r\n"),
])
def test_node_pins_written_by_windows_editors_are_understood(tmp_path, encoding, raw):
    (tmp_path / "app").mkdir()
    (tmp_path / "app" / ".nvmrc").write_bytes(raw.encode(encoding))

    assert probes.find_node_pins([str(tmp_path)]) == {"22.22.0"}


def test_a_pin_file_without_a_recognisable_version_makes_the_pin_search_incomplete(tmp_path):
    (tmp_path / "app").mkdir()
    (tmp_path / "app" / ".nvmrc").write_bytes(b"\x00\x01garbage")
    unreadable = []

    probes.find_node_pins([str(tmp_path)], unreadable=unreadable)

    assert len(unreadable) == 1


def test_lts_style_aliases_are_not_treated_as_unreadable(tmp_path):
    (tmp_path / "app").mkdir()
    (tmp_path / "app" / ".nvmrc").write_text("lts/jod\n")
    unreadable = []

    pins = probes.find_node_pins([str(tmp_path)], unreadable=unreadable)

    assert unreadable == [] and pins == set()


def test_skipped_node_check_is_reported_with_its_reason_not_as_no_data(fake_env):
    import classify
    probe = probes.nvm_unused(NVM_LIST, "C:/nvm", pins=set(), size_fn=size, pins_complete=False)
    catalog = {"entries": [{"id": "nv", "title_ja": "nvm の使われていない Node.js", "why_ja": "理由", "regen_ja": "再",
                            "class": "COSTLY", "rebuild_cost": 1.5, "paths": [],
                            "method": {"kind": "command", "command": "nvm uninstall"}}]}
    scan_meta = {"scanned_at": 0, "disk": {"free": 1, "total": 2}, "entries": []}

    rows = classify.build_rows(catalog, scan_meta, env=fake_env, running=set(), now=0, probes={"nv": probe})
    text = classify.render_report(rows, scan_meta, now=0)

    assert rows[0]["section"] == "skipped"
    assert "該当データなし" not in text
    assert "クラウド上にしかない" in text


def test_newest_revision_of_each_browser_is_kept_even_when_its_project_needs_reinstalling(tmp_path):
    root = make_playwright(tmp_path, live_revisions=["1223"], dead_revisions=["1254"])

    result = probes.playwright_unused(str(root), size_fn=size)

    assert item_names(result) == ["chromium-1234", "chromium_headless_shell-1234"]
