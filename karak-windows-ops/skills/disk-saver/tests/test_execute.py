import os
import sys
import time
from pathlib import Path

import pytest

from conftest import write_file

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "apply"))
import execute  # noqa: E402
import classify  # noqa: E402
import policy  # noqa: E402

NOW = time.time()


def row(id, paths, kind="delete", section="propose", gates=(), blocked=None, command=None, item_commands=None):
    method = {"kind": kind}
    if command:
        method["command"] = command
    items = [{"path": str(p)} for p in paths]
    if item_commands:
        items = [{"path": str(p), "command": c} for p, c in zip(paths, item_commands)]
    return {"id": id, "title_ja": f"対象{id}", "section": section, "method": method, "gates": list(gates),
            "blocked": blocked, "items": [i["path"] for i in items], "item_details": items}


def make_plan(rows, created_at=NOW):
    return {"plan_hash": classify.plan_hash(rows), "created_at": created_at, "rows": rows}


class Recorder:
    def __init__(self, fail_on=()):
        self.calls, self.fail_on = [], set(fail_on)

    def __call__(self, arg):
        self.calls.append(arg)
        key = arg if isinstance(arg, str) else " ".join(arg)
        if any(f in key for f in self.fail_on):
            raise OSError("simulated failure: in use")
        return 0, "ok"


def run(plan, ids, env, running=frozenset(), runner=None, recycler=None, approved_hash=None, now=NOW):
    return execute.execute(
        plan, {"plan_hash": approved_hash or plan["plan_hash"], "ids": ids}, env=env,
        running_fn=lambda: set(running) if running is not None else None,
        runner=runner or Recorder(), recycler=recycler or Recorder(), now=now,
        recycle_check=lambda path, size: None, which=lambda tool: tool)


def status(result):
    return {(r["id"], os.path.basename(r.get("target", ""))): r["status"] for r in result["results"]}


def test_nothing_runs_when_the_approval_belongs_to_a_different_plan(fake_env, tmp_path):
    victim = write_file(tmp_path / "cache" / "a.bin", 10).parent
    plan = make_plan([row("c", [victim])])

    result = run(plan, ["c"], fake_env, approved_hash="0000")

    assert victim.exists()
    assert result["refused"] and "計画" in result["refused"]


def test_a_plan_older_than_an_hour_is_refused_so_a_fresh_scan_is_used(fake_env, tmp_path):
    victim = write_file(tmp_path / "cache" / "a.bin", 10).parent
    plan = make_plan([row("c", [victim])], created_at=NOW - 2 * 3600)

    result = run(plan, ["c"], fake_env)

    assert victim.exists()
    assert result["refused"]


def test_only_approved_rows_are_removed_and_others_are_left_untouched(fake_env, tmp_path):
    a = write_file(tmp_path / "a" / "f.bin", 10).parent
    b = write_file(tmp_path / "b" / "f.bin", 10).parent
    plan = make_plan([row("a", [a]), row("b", [b])])

    result = run(plan, ["a"], fake_env)

    assert not a.exists() and b.exists()
    assert status(result) == {("a", "a"): "done"}


def test_a_failing_item_is_reported_with_its_error_and_the_run_continues(fake_env, tmp_path):
    first, second = tmp_path / "one", tmp_path / "two"
    first.mkdir(); second.mkdir()
    recycler = Recorder(fail_on=["one"])
    plan = make_plan([row("r", [first, second], kind="recycle")])

    result = run(plan, ["r"], fake_env, recycler=recycler)

    by = {os.path.basename(r["target"]): r for r in result["results"]}
    assert by["one"]["status"] == "failed" and "in use" in by["one"]["error"]
    assert len(recycler.calls) == 2


def test_paths_in_protected_locations_are_refused_even_if_listed_in_the_plan(fake_env):
    docs = Path(fake_env["USERPROFILE"]) / "Documents" / "keep"
    write_file(docs / "report.docx", 10)
    plan = make_plan([row("x", [docs])])

    result = run(plan, ["x"], fake_env)

    assert docs.exists()
    assert status(result) == {("x", "keep"): "refused"}


def test_rows_whose_app_is_running_at_execution_time_are_refused(fake_env, tmp_path):
    cache = write_file(tmp_path / "Code" / "Cache" / "f", 10).parent
    plan = make_plan([row("v", [cache], gates=["process_not_running:Code.exe"])])

    result = run(plan, ["v"], fake_env, running={"code.exe"})

    assert cache.exists()
    assert "Code.exe" in result["results"][0]["error"]


def test_gated_rows_are_refused_when_running_apps_cannot_be_checked(fake_env, tmp_path):
    cache = write_file(tmp_path / "Code" / "Cache" / "f", 10).parent
    plan = make_plan([row("v", [cache], gates=["process_not_running:Code.exe"])])

    result = run(plan, ["v"], fake_env, running=None)

    assert cache.exists()
    assert result["results"][0]["status"] == "refused"


@pytest.mark.parametrize("section,kind", [
    ("advice", "advice"), ("decision", "advice"), ("propose", "handoff_admin"), ("skipped", "command"),
])
def test_advice_decision_admin_and_skipped_rows_are_never_executed(fake_env, tmp_path, section, kind):
    runner = Recorder()
    plan = make_plan([row("d", [tmp_path / "oem7.inf"], kind=kind, section=section,
                          item_commands=["pnputil /delete-driver oem7.inf"])])

    result = run(plan, ["d"], fake_env, runner=runner)

    assert runner.calls == []
    assert result["results"][0]["status"] == "refused"


def test_a_row_held_back_in_the_report_is_not_executed(fake_env, tmp_path):
    cache = write_file(tmp_path / "c" / "f", 10).parent
    plan = make_plan([row("h", [cache], blocked="msedge.exe が起動中")])

    run(plan, ["h"], fake_env)

    assert cache.exists()


def test_commands_outside_the_allowlist_are_refused_without_running(fake_env, tmp_path):
    runner = Recorder()
    plan = make_plan([row("n", [tmp_path / "x"], kind="command", command="dotnet nuget locals all --clear")])

    result = run(plan, ["n"], fake_env, runner=runner)

    assert runner.calls == []
    assert result["results"][0]["status"] == "refused"


def test_one_command_runs_per_item_when_items_carry_their_own_command(fake_env, tmp_path):
    runner = Recorder()
    v1, v2 = tmp_path / "v22.22.0", tmp_path / "v24.18.0"
    plan = make_plan([row("nvm", [v1, v2], kind="command", command="nvm uninstall",
                          item_commands=["nvm uninstall 22.22.0", "nvm uninstall 24.18.0"])])

    run(plan, ["nvm"], fake_env, runner=runner)

    assert [c[-3:] for c in runner.calls] == [["nvm", "uninstall", "22.22.0"], ["nvm", "uninstall", "24.18.0"]]


def test_a_cache_command_runs_once_for_the_row(fake_env, tmp_path):
    runner = Recorder()
    plan = make_plan([row("npm", [tmp_path / "_cacache"], kind="command", command="npm cache clean --force")])

    result = run(plan, ["npm"], fake_env, runner=runner)

    assert [c[-4:] for c in runner.calls] == [["npm", "cache", "clean", "--force"]]
    assert result["results"][0]["status"] == "done"


def test_deleting_a_cache_removes_its_files_and_reports_the_bytes(fake_env, tmp_path):
    cache = tmp_path / "cache"
    write_file(cache / "x" / "a.bin", 1000)
    write_file(cache / "b.bin", 500)
    plan = make_plan([row("c", [cache])])

    result = run(plan, ["c"], fake_env)

    assert not cache.exists()
    assert result["results"][0]["freed"] == 1500


def test_deleting_does_not_follow_junctions_out_of_the_target(fake_env, tmp_path):
    import subprocess
    outside = write_file(tmp_path / "precious" / "keep.bin", 100).parent
    cache = tmp_path / "cache"
    write_file(cache / "a.bin", 10)
    subprocess.run(["cmd", "/c", "mklink", "/J", str(cache / "link"), str(outside)], check=True, capture_output=True)
    plan = make_plan([row("c", [cache])])

    run(plan, ["c"], fake_env)

    assert (outside / "keep.bin").exists()


def test_free_space_before_and_after_is_reported(fake_env, tmp_path):
    plan = make_plan([row("c", [write_file(tmp_path / "c" / "f", 10).parent])])

    result = run(plan, ["c"], fake_env)

    assert result["free_before"] > 0 and result["free_after"] > 0


def test_executor_never_kills_processes():
    text = (ROOT / "apply" / "execute.py").read_text(encoding="utf-8")
    kill = [w for w in ("task" + "kill", "Stop-" + "Process", "os." + "kill", "Terminate" + "Process", ".ki" + "ll(")
            if w in text]
    assert kill == []


def test_a_target_that_still_has_files_in_use_is_not_reported_as_done(fake_env, tmp_path):
    cache = tmp_path / "cache"
    write_file(cache / "real.bin", 100)
    lock = write_file(cache / "lock", 0)
    plan = make_plan([row("c", [cache])])

    with open(lock, "rb"):
        result = run(plan, ["c"], fake_env)

    r = result["results"][0]
    assert cache.exists()
    assert r["status"] in ("partial", "failed") and r["error"]


@pytest.mark.parametrize("ids", [["typo"], [" c"]])
def test_an_approved_id_that_is_not_in_the_plan_is_reported(fake_env, tmp_path, ids):
    cache = write_file(tmp_path / "c" / "f", 10).parent
    plan = make_plan([row("c", [cache])])

    result = run(plan, ids, fake_env)

    outcomes = {r["id"].strip(): r["status"] for r in result["results"]}
    if ids == [" c"]:
        assert outcomes == {"c": "done"}
    else:
        assert outcomes == {"typo": "refused"}


def test_recycle_rows_are_refused_when_the_recycle_bin_would_delete_permanently(fake_env, tmp_path):
    target = write_file(tmp_path / "proj" / "node_modules" / "x.js", 10).parent
    recycler = Recorder()
    plan = make_plan([row("p", [target], kind="recycle")])

    result = execute.execute(plan, {"plan_hash": plan["plan_hash"], "ids": ["p"]}, env=fake_env,
                             running_fn=lambda: set(), runner=Recorder(), recycler=recycler, now=NOW,
                             recycle_check=lambda path, size: "このドライブのごみ箱は完全削除に設定されている")

    assert recycler.calls == []
    assert target.exists()
    assert result["results"][0]["status"] == "refused"


def test_a_plan_whose_item_paths_were_changed_after_approval_is_refused(fake_env, tmp_path):
    cache = write_file(tmp_path / "cache" / "f", 10).parent
    other = write_file(tmp_path / "other" / "f", 10).parent
    rows = [row("c", [cache])]
    plan = make_plan(rows)
    plan["rows"][0]["item_details"][0]["path"] = str(other)

    result = run(plan, ["c"], fake_env)

    assert other.exists() and cache.exists()
    assert result["refused"]


def test_relative_item_paths_are_never_acted_on(fake_env, tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    write_file(tmp_path / "rel" / "f", 10)
    plan = make_plan([row("c", ["rel"])])

    result = run(plan, ["c"], fake_env)

    assert (tmp_path / "rel").exists()
    assert result["results"][0]["status"] == "refused"


def test_commands_run_the_tool_found_on_path_not_one_in_the_current_folder(fake_env, tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    (tmp_path / "uv.cmd").write_text("@echo planted")
    monkeypatch.setenv("PATH", str(tmp_path / "empty-path-dir"))
    runner = Recorder()
    plan = make_plan([row("u", [tmp_path / "uvcache"], kind="command", command="uv cache prune")])

    result = execute.execute(plan, {"plan_hash": plan["plan_hash"], "ids": ["u"]}, env=fake_env,
                             running_fn=lambda: set(), runner=runner, recycler=Recorder(), now=NOW,
                             recycle_check=lambda p, s: None)

    assert runner.calls == []
    assert result["results"][0]["status"] in ("refused", "failed")
