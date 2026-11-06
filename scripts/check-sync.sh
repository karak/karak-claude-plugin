#!/usr/bin/env bash
# Fail if any sub-plugin copy has drifted from its canonical source in root skills/ or agents/.
set -euo pipefail

REPO_ROOT="$(cd "$(dirname "$0")/.." && pwd)"

# FAILED is a deferred error flag. check_copy/check_agent_dir set it to 1 instead of
# exiting immediately so all drift is reported before the script exits.
FAILED=0

check_copy() {
    local canonical="$1"
    local copy="$2"
    if [ ! -e "$canonical" ]; then
        echo "ERROR: canonical source missing: $canonical"
        FAILED=1
        return
    fi
    if [ ! -e "$copy" ]; then
        echo "DRIFT: copy missing: $copy"
        FAILED=1
        return
    fi
    if ! diff -rq --exclude='*.pyc' --exclude='__pycache__' "$canonical" "$copy" >/dev/null 2>&1; then
        echo "DRIFT: $copy differs from $canonical"
        FAILED=1
    fi
}

# check_agent_dir CANONICAL_DIR COPY_DIR [PLUGIN_ONLY...]
# PLUGIN_ONLY lists agent files that exist only in COPY_DIR by design (no root copy);
# they are skipped. Any other file without a root counterpart is reported as ORPHAN.
check_agent_dir() {
    local canonical_dir="$1"
    local copy_dir="$2"
    shift 2
    local plugin_only=" $* "
    for f in "$copy_dir"/*.md; do
        [ -e "$f" ] || continue
        local filename
        filename="$(basename "$f")"
        local canonical_file="$canonical_dir/$filename"
        if [[ "$plugin_only" == *" $filename "* ]]; then
            if [ -e "$canonical_file" ]; then
                echo "STALE: $filename is listed as plugin-only but also exists in $canonical_dir"
                FAILED=1
            fi
            continue
        fi
        if [ ! -e "$canonical_file" ]; then
            echo "ORPHAN: $f has no canonical source in $canonical_dir"
            FAILED=1
        elif ! diff -q "$canonical_file" "$f" >/dev/null 2>&1; then
            echo "DRIFT: $f differs from $canonical_file"
            FAILED=1
        fi
    done
}

# karak-design
for skill in apple-design icon-design frontend-aesthetics \
             ux-psychologist material-design hifi-design-quality mobile-auth-screen-design \
             design-system; do
    check_copy "$REPO_ROOT/skills/$skill" "$REPO_ROOT/karak-design/skills/$skill"
done
check_agent_dir "$REPO_ROOT/agents" "$REPO_ROOT/karak-design/agents"

# karak-architecture
for skill in write-c4-diagram adr-architect; do
    check_copy "$REPO_ROOT/skills/$skill" "$REPO_ROOT/karak-architecture/skills/$skill"
done
check_agent_dir "$REPO_ROOT/agents" "$REPO_ROOT/karak-architecture/agents"

# karak-engineering
for skill in codex-review google-design-docs; do
    check_copy "$REPO_ROOT/skills/$skill" "$REPO_ROOT/karak-engineering/skills/$skill"
done
# nodejs-backend-engineer.md lives only in karak-engineering (docs/superpowers/specs/2026-04-29-nodejs-backend-skill-design.md)
check_agent_dir "$REPO_ROOT/agents" "$REPO_ROOT/karak-engineering/agents" nodejs-backend-engineer.md

# karak-product
check_agent_dir "$REPO_ROOT/agents" "$REPO_ROOT/karak-product/agents"

# marketplace.json: a plugin version bump must come with a bump of the top-level version.
# Compares against BASE_REF (default: main); skipped when the base is unavailable or equals HEAD.
BASE_REF="${BASE_REF:-main}"
MARKETPLACE=".claude-plugin/marketplace.json"
if command -v jq >/dev/null 2>&1 \
    && git -C "$REPO_ROOT" rev-parse --verify -q "$BASE_REF" >/dev/null \
    && [ "$(git -C "$REPO_ROOT" rev-parse "$BASE_REF")" != "$(git -C "$REPO_ROOT" rev-parse HEAD)" ]; then
    base_json="$(git -C "$REPO_ROOT" show "$BASE_REF:$MARKETPLACE" | tr -d '\r')"
    plugin_versions() { jq -c '[.plugins[] | {(.name): .version}] | add' | tr -d '\r'; }
    base_plugins="$(printf '%s' "$base_json" | plugin_versions)"
    head_plugins="$(plugin_versions < "$REPO_ROOT/$MARKETPLACE")"
    base_top="$(printf '%s' "$base_json" | jq -r '.metadata.version // .version' | tr -d '\r')"
    head_top="$(jq -r '.metadata.version // .version' < "$REPO_ROOT/$MARKETPLACE" | tr -d '\r')"
    if [ "$base_plugins" != "$head_plugins" ] && [ "$base_top" = "$head_top" ]; then
        echo "VERSION: plugin versions changed vs $BASE_REF but marketplace top-level version is still $head_top"
        FAILED=1
    fi
fi

if [ "$FAILED" -eq 1 ]; then
    echo "Sync check FAILED. Re-copy from canonical sources."
    exit 1
fi
echo "All sub-plugin copies are in sync."
