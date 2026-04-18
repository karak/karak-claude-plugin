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

check_agent_dir() {
    local canonical_dir="$1"
    local copy_dir="$2"
    for f in "$copy_dir"/*.md; do
        [ -e "$f" ] || continue
        local filename
        filename="$(basename "$f")"
        local canonical_file="$canonical_dir/$filename"
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
check_agent_dir "$REPO_ROOT/agents" "$REPO_ROOT/karak-engineering/agents"

# karak-product
check_agent_dir "$REPO_ROOT/agents" "$REPO_ROOT/karak-product/agents"

if [ "$FAILED" -eq 1 ]; then
    echo "Sync check FAILED. Re-copy from canonical sources."
    exit 1
fi
echo "All sub-plugin copies are in sync."
