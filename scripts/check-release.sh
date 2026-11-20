#!/usr/bin/env bash
# Release gate for merges into main (main is the release branch: a merge is a release).
#
# Checks, comparing HEAD against the tip of BASE_REF (default: origin/main):
#   1. HEAD_BRANCH, when set, must be "develop" (main only takes merges from develop).
#   2. metadata.version in marketplace.json is strictly greater (semver) than on BASE_REF.
#   3. Every plugin whose source directory or marketplace entry (ignoring "version")
#      changed has a strictly greater version. Plugins absent on BASE_REF are new and pass.
#
# Compares against the BASE_REF tip rather than the merge base so the result does not
# depend on the merge method used for earlier releases.
set -euo pipefail

REPO_ROOT="${REPO_ROOT:-$(git rev-parse --show-toplevel)}"
BASE_REF="${BASE_REF:-origin/main}"
HEAD_BRANCH="${HEAD_BRANCH:-}"
MARKETPLACE=".claude-plugin/marketplace.json"
FAILED=0

command -v jq >/dev/null 2>&1 || { echo "ERROR: jq is required"; exit 1; }

if [ -n "$HEAD_BRANCH" ] && [ "$HEAD_BRANCH" != "develop" ]; then
    echo "BRANCH: main only accepts merges from develop (got '$HEAD_BRANCH'). Target develop instead."
    FAILED=1
fi

base_commit="$(git -C "$REPO_ROOT" rev-parse --verify "$BASE_REF^{commit}")"

# semver_gt A B: true when A > B. Both must be MAJOR.MINOR.PATCH.
semver_gt() {
    local a="$1" b="$2" i
    local re='^[0-9]+\.[0-9]+\.[0-9]+$'
    [[ "$a" =~ $re && "$b" =~ $re ]] || return 1
    local -a x y
    IFS=. read -r -a x <<<"$a"
    IFS=. read -r -a y <<<"$b"
    for i in 0 1 2; do
        if ((10#${x[i]} > 10#${y[i]})); then return 0; fi
        if ((10#${x[i]} < 10#${y[i]})); then return 1; fi
    done
    return 1
}

base_json="$(git -C "$REPO_ROOT" show "$base_commit:$MARKETPLACE" | tr -d '\r')"
head_json="$(tr -d '\r' < "$REPO_ROOT/$MARKETPLACE")"

top() { jq -r '.metadata.version // .version'; }
base_top="$(printf '%s' "$base_json" | top)"
head_top="$(printf '%s' "$head_json" | top)"
if ! semver_gt "$head_top" "$base_top"; then
    echo "VERSION: marketplace metadata.version must increase on every release ($BASE_REF: $base_top, HEAD: $head_top)"
    FAILED=1
fi

while IFS=$'\t' read -r name source; do
    head_entry="$(printf '%s' "$head_json" | jq -cS --arg n "$name" '.plugins[] | select(.name == $n)')"
    base_entry="$(printf '%s' "$base_json" | jq -cS --arg n "$name" '.plugins[] | select(.name == $n)')"
    if [ -z "$base_entry" ]; then
        echo "NEW: $name ($(printf '%s' "$head_entry" | jq -r .version))"
        continue
    fi
    path="${source#./}"
    changed=""
    if ! git -C "$REPO_ROOT" diff --quiet "$base_commit" HEAD -- "$path"; then
        changed="files under $path"
    elif [ "$(printf '%s' "$head_entry" | jq -cS 'del(.version)')" != "$(printf '%s' "$base_entry" | jq -cS 'del(.version)')" ]; then
        changed="marketplace entry"
    fi
    [ -n "$changed" ] || continue
    base_v="$(printf '%s' "$base_entry" | jq -r .version)"
    head_v="$(printf '%s' "$head_entry" | jq -r .version)"
    if semver_gt "$head_v" "$base_v"; then
        echo "BUMPED: $name $base_v -> $head_v ($changed changed)"
    else
        echo "VERSION: $name changed ($changed) but its version did not increase ($BASE_REF: $base_v, HEAD: $head_v)"
        FAILED=1
    fi
done < <(printf '%s' "$head_json" | jq -r '.plugins[] | [.name, .source] | @tsv')

if [ "$FAILED" -eq 1 ]; then
    echo "Release gate FAILED. See CLAUDE.md \"Branching and releases\"."
    exit 1
fi
echo "Release gate passed: $base_top -> $head_top"
