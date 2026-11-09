import re

import classify

CLASSES = {"PRESERVE", "FREE", "CHEAP", "COSTLY", "PROJECT", "DECISION", "ADVICE"}
ACTIONABLE = {"FREE", "CHEAP", "COSTLY", "PROJECT"}
JAPANESE = re.compile(r"[぀-ヿ一-鿿]")


def test_entry_ids_are_unique(catalog):
    ids = [e["id"] for e in catalog["entries"]]
    assert len(ids) == len(set(ids))


def test_every_entry_explains_itself_in_japanese_with_a_class_and_rebuild_cost(catalog):
    for e in catalog["entries"]:
        assert e["class"] in CLASSES, e["id"]
        assert JAPANESE.search(e["title_ja"]), e["id"]
        assert JAPANESE.search(e["why_ja"]), e["id"]
        if e["class"] in ACTIONABLE:
            assert e["rebuild_cost"] >= 1, e["id"]
            assert JAPANESE.search(e["regen_ja"]), e["id"]


def test_method_matches_class(catalog):
    for e in catalog["entries"]:
        kind = e["method"]["kind"]
        if e["class"] in ACTIONABLE:
            assert kind in {"delete", "recycle", "command", "handoff_admin"}, e["id"]
        elif e["class"] in {"DECISION", "ADVICE"}:
            assert kind == "advice", e["id"]
            assert "command" not in e["method"], e["id"]
        else:
            assert kind == "none", e["id"]


def test_no_deletable_entry_points_into_protected_locations(catalog, fake_env):
    for e in catalog["entries"]:
        if e["class"] not in ACTIONABLE:
            continue
        for pattern in e["paths"]:
            path = classify.expand_vars(pattern, fake_env)
            assert classify.protected_reason(path, fake_env) is None, (e["id"], path)


def test_catalog_covers_browser_on_device_ai_models_and_developer_caches(catalog):
    ids = {e["id"] for e in catalog["entries"]}
    assert {"chrome-ondevice-model", "edge-ondevice-model"} <= ids
    assert {"npm-npx", "pnpm-store", "uv-cache", "vscode-vsix"} <= ids
