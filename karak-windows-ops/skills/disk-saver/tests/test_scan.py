import ctypes
import os
import subprocess
import time

import pytest

from conftest import write_file
import scan

DAY = 86400


def test_tree_size_and_file_count_match_the_files_on_disk(tmp_path):
    write_file(tmp_path / "a.bin", 1000)
    write_file(tmp_path / "sub" / "b.bin", 2000)
    write_file(tmp_path / "sub" / "deep" / "c.bin", 3000)

    result = scan.size_tree(str(tmp_path))

    assert result["bytes"] == 6000
    assert result["files"] == 3
    assert result["partial"] is False


def test_newest_modification_time_of_a_tree_is_reported(tmp_path):
    now = time.time()
    write_file(tmp_path / "old.bin", 10, mtime=now - 100 * DAY)
    write_file(tmp_path / "sub" / "new.bin", 10, mtime=now - 2 * DAY)

    result = scan.size_tree(str(tmp_path))

    assert abs(result["newest_mtime"] - (now - 2 * DAY)) < 5


def test_junctions_are_not_followed_so_linked_data_is_not_counted(tmp_path):
    target = tmp_path / "elsewhere"
    write_file(target / "big.bin", 5000)
    root = tmp_path / "root"
    write_file(root / "own.bin", 100)
    subprocess.run(
        ["cmd", "/c", "mklink", "/J", str(root / "link"), str(target)],
        check=True, capture_output=True,
    )

    result = scan.size_tree(str(root))

    assert result["bytes"] == 100


def test_cloud_only_placeholder_files_occupy_no_local_space(tmp_path):
    write_file(tmp_path / "local.bin", 700)
    placeholder = write_file(tmp_path / "cloud.bin", 900)
    FILE_ATTRIBUTE_OFFLINE = 0x1000
    ok = ctypes.windll.kernel32.SetFileAttributesW(str(placeholder), FILE_ATTRIBUTE_OFFLINE)
    if not ok or not (os.stat(placeholder).st_file_attributes & FILE_ATTRIBUTE_OFFLINE):
        pytest.skip("environment cannot mark a file offline")

    result = scan.size_tree(str(tmp_path))

    assert result["bytes"] == 700
    assert result["cloud_files"] == 1


def test_a_scan_that_exceeds_its_time_budget_is_marked_partial(tmp_path):
    for i in range(20):
        write_file(tmp_path / f"d{i}" / "f.bin", 10)

    result = scan.size_tree(str(tmp_path), deadline=time.monotonic() - 1)

    assert result["partial"] is True


def test_environment_variables_and_home_are_expanded_and_globs_match_every_profile(fake_env):
    local = fake_env["LOCALAPPDATA"]
    for profile in ("Default", "Profile 1"):
        os.makedirs(os.path.join(local, "Browser", profile, "Cache"))
    os.makedirs(os.path.join(fake_env["USERPROFILE"], ".cache"))

    found = scan.expand(r"%LOCALAPPDATA%\Browser\*\Cache", fake_env)
    home = scan.expand(r"~\.cache", fake_env)

    assert sorted(found) == sorted(
        os.path.join(local, "Browser", p, "Cache") for p in ("Default", "Profile 1")
    )
    assert home == [os.path.join(fake_env["USERPROFILE"], ".cache")]


def test_absent_target_is_reported_with_zero_bytes_rather_than_failing(fake_env):
    entry = {"id": "missing", "paths": [r"%LOCALAPPDATA%\NoSuchTool\cache"]}

    result = scan.scan_entry(entry, fake_env)

    assert result["bytes"] == 0
    assert result["items"] == []


def test_temp_selection_counts_only_children_untouched_for_the_given_days(fake_env, tmp_path):
    now = time.time()
    temp = tmp_path / "Users" / "someone" / "AppData" / "Local" / "Temp"
    write_file(temp / "stale-dir" / "f.bin", 400, mtime=now - 30 * DAY)
    os.utime(temp / "stale-dir", (now - 30 * DAY, now - 30 * DAY))
    write_file(temp / "stale.log", 50, mtime=now - 30 * DAY)
    write_file(temp / "fresh-dir" / "f.bin", 999, mtime=now - 1 * DAY)
    write_file(temp / "claude" / "old.bin", 777, mtime=now - 30 * DAY)
    entry = {
        "id": "user-temp",
        "paths": [r"%TEMP%"],
        "select": {"children_older_than_days": 7, "exclude": ["claude"]},
    }

    result = scan.scan_entry(entry, fake_env, now=now)

    assert result["bytes"] == 450
    assert sorted(os.path.basename(i["path"]) for i in result["items"]) == ["stale-dir", "stale.log"]


def test_catalog_scan_reports_every_entry_and_the_drive_free_space(fake_env):
    write_file(__import__("pathlib").Path(fake_env["LOCALAPPDATA"]) / "toolA" / "x.bin", 123)
    catalog = {"entries": [
        {"id": "a", "paths": [r"%LOCALAPPDATA%\toolA"]},
        {"id": "b", "paths": [r"%LOCALAPPDATA%\toolB"]},
    ]}

    result = scan.scan_catalog(catalog, fake_env)

    by_id = {e["id"]: e for e in result["entries"]}
    assert by_id["a"]["bytes"] == 123
    assert by_id["b"]["bytes"] == 0
    assert result["disk"]["total"] > 0 and 0 <= result["disk"]["free"] <= result["disk"]["total"]
    assert "scanned_at" in result


def test_a_measured_path_that_is_itself_a_junction_is_not_counted(tmp_path):
    target = tmp_path / "elsewhere"
    write_file(target / "big.bin", 5000)
    subprocess.run(["cmd", "/c", "mklink", "/J", str(tmp_path / "link"), str(target)],
                   check=True, capture_output=True)

    result = scan.size_tree(str(tmp_path / "link"))

    assert result["bytes"] == 0
