# Derived in idea from CharlesLadera/disk-cleanup tests/test_safety.py (MIT, Copyright (c) 2026 Charles Ladera).
from pathlib import Path

import pytest

import policy

SCRIPTS = Path(__file__).resolve().parent.parent / "scripts"


def test_analysis_scripts_contain_no_way_to_delete_move_or_rename_files():
    offenders = {}
    for src in SCRIPTS.rglob("*.py"):
        found = policy.source_violations(src.read_text(encoding="utf-8"))
        if found:
            offenders[src.name] = found
    assert offenders == {}


@pytest.mark.parametrize("snippet", [
    "import shutil\nshutil.rmtree(p)",
    "os.remove(p)",
    "os.unlink(p)",
    "Path(p).unlink()",
    "os.rename(a, b)",
    "shutil.move(a, b)",
    "send2trash(p)",
    "windll.shell32.SHFileOperationW(op)",
    "subprocess.run(['pwsh', '-c', 'Remove-Item x'])",
    "subprocess.run('cmd /c del /q x')",
    "subprocess.run(['cmd', '/c', 'rd', '/s', 'x'])",
])
def test_the_guard_recognises_each_deletion_primitive(snippet):
    assert policy.source_violations(snippet) != []


@pytest.mark.parametrize("command", [
    "npm cache verify",
    "npm cache clean --force",
    "pnpm store prune",
    "uv cache prune",
    "dotnet nuget locals http-cache --clear",
    "nvm uninstall 22.22.0",
    "docker builder prune -f",
    "docker image prune -f",
])
def test_vetted_cache_commands_are_allowed(command):
    assert policy.command_violations(command) == []


@pytest.mark.parametrize("command", [
    "docker system prune -f",
    "docker image prune -a -f",
    "docker volume prune --volumes",
    "pnputil /delete-driver oem7.inf",
    "rm -rf C:/Users",
    "npm cache verify & del /q C:\\x",
    "pwsh -c Remove-Item x",
    "format C:",
])
def test_destructive_broad_or_unknown_commands_are_rejected(command):
    assert policy.command_violations(command) != []


def test_driver_removal_is_only_offered_as_an_admin_handoff_without_force():
    assert policy.handoff_violations("pnputil /delete-driver oem374.inf") == []
    assert policy.handoff_violations("pnputil /delete-driver oem374.inf /force") != []
    assert policy.handoff_violations("Dism /Online /Cleanup-Image /StartComponentCleanup") == []
    assert policy.handoff_violations("Dism /Online /Cleanup-Image /StartComponentCleanup /ResetBase") != []


def test_every_command_in_the_catalog_is_allowed(catalog):
    problems = {}
    for e in catalog["entries"]:
        m = e["method"]
        if m["kind"] == "command":
            v = policy.command_violations(m["command"])
        elif m["kind"] == "handoff_admin":
            v = policy.handoff_violations(m["command"])
        else:
            continue
        if v:
            problems[e["id"]] = v
    assert problems == {}


@pytest.mark.parametrize("command", [
    "dotnet nuget locals global-packages --clear",
    "dotnet nuget locals temp --clear",
    "dotnet nuget locals plugins-cache --clear",
])
def test_nuget_cleanup_is_limited_to_the_http_cache(command):
    assert policy.command_violations(command) != []


@pytest.mark.parametrize("command", [
    "npm cache clean --force --cache=C:/Users/x",
    "uv cache prune --cache-dir=../../x",
    "nvm uninstall 22.22.0 extra",
    "pnpm store prune --force",
    "docker image prune -af",
    "dotnet nuget locals http-cache --clear global-packages",
])
def test_vetted_commands_cannot_carry_extra_options_or_arguments(command):
    assert policy.command_violations(command) != []
