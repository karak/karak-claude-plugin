#!/usr/bin/env bash
# Scenario tests for scripts/check-release.sh. Each case builds a throwaway repo with a
# "main" commit, applies a change on top, and asserts the gate's exit code and message.
set -euo pipefail

GATE="$(cd "$(dirname "$0")/.." && pwd)/check-release.sh"
WORK="$(mktemp -d)"
trap 'rm -rf "$WORK"' EXIT
PASS=0
FAIL=0

marketplace() { # marketplace TOP A_VERSION [B_VERSION] [A_DESCRIPTION]
    local b=""
    [ -n "${3:-}" ] && b=",{\"name\":\"plug-b\",\"source\":\"./plug-b\",\"version\":\"$3\"}"
    printf '{"metadata":{"version":"%s"},"plugins":[{"name":"plug-a","source":"./plug-a","description":"%s","version":"%s"}%s]}\n' \
        "$1" "${4:-a}" "$2" "$b" > .claude-plugin/marketplace.json
}

setup() {
    local dir="$WORK/$1"
    mkdir -p "$dir" && cd "$dir"
    git init -q -b main
    git config user.email t@example.com && git config user.name t
    mkdir -p .claude-plugin plug-a docs
    echo one > plug-a/SKILL.md
    echo doc > docs/x.md
    marketplace 1.0.0 1.0.0
    git add -A && git commit -qm base
    git switch -qc develop
}

run_case() { # run_case NAME EXPECTED_EXIT EXPECTED_SUBSTRING [HEAD_BRANCH]
    git add -A && git commit -qm change --allow-empty
    local out code=0
    out="$(REPO_ROOT="$PWD" BASE_REF=main HEAD_BRANCH="${4-develop}" bash "$GATE" 2>&1)" || code=$?
    if [ "$code" -eq "$2" ] && [[ "$out" == *"$3"* ]]; then
        PASS=$((PASS + 1)); echo "ok   $1"
    else
        FAIL=$((FAIL + 1)); echo "FAIL $1 (exit $code, want $2; want text '$3')"; echo "$out" | sed 's/^/     /'
    fi
}

setup bump-ok;        echo two > plug-a/SKILL.md; marketplace 1.1.0 1.0.1
run_case "changed plugin with plugin and top-level bump passes" 0 "BUMPED: plug-a 1.0.0 -> 1.0.1"

setup no-plugin-bump; echo two > plug-a/SKILL.md; marketplace 1.1.0 1.0.0
run_case "changed plugin without its bump fails" 1 "VERSION: plug-a changed (files under plug-a)"

setup no-top-bump;    echo two > plug-a/SKILL.md; marketplace 1.0.0 1.0.1
run_case "plugin bump without top-level bump fails" 1 "metadata.version must increase"

setup docs-only;      echo doc2 > docs/x.md; marketplace 1.0.1 1.0.0
run_case "non-plugin change with top-level bump passes" 0 "Release gate passed: 1.0.0 -> 1.0.1"

setup docs-no-top;    echo doc2 > docs/x.md
run_case "release without top-level bump fails" 1 "metadata.version must increase"

setup decrease;       echo two > plug-a/SKILL.md; marketplace 1.1.0 0.9.0
run_case "plugin version decrease fails" 1 "VERSION: plug-a changed"

setup numeric;        echo two > plug-a/SKILL.md; marketplace 1.10.0 1.0.10
run_case "semver compares numerically" 0 "Release gate passed: 1.0.0 -> 1.10.0"

setup entry-only;     marketplace 1.0.1 1.0.0 "" "new description"
run_case "marketplace entry change without bump fails" 1 "VERSION: plug-a changed (marketplace entry)"

setup new-plugin;     mkdir plug-b && echo b > plug-b/SKILL.md; marketplace 1.1.0 1.0.0 0.1.0
run_case "new plugin passes" 0 "NEW: plug-b (0.1.0)"

setup wrong-branch;   echo two > plug-a/SKILL.md; marketplace 1.1.0 1.0.1
run_case "head branch other than develop fails" 1 "main only accepts merges from develop (got 'feat/x')" feat/x

setup no-branch;      echo two > plug-a/SKILL.md; marketplace 1.1.0 1.0.1
run_case "empty HEAD_BRANCH (push event) skips branch check" 0 "Release gate passed" ""

setup bad-format;     echo two > plug-a/SKILL.md; marketplace 1.1.0 1.0.1-beta
run_case "non MAJOR.MINOR.PATCH version fails" 1 "VERSION: plug-a changed"

setup no-plugins;     printf '{"metadata":{"version":"1.0.1"}}\n' > .claude-plugin/marketplace.json
run_case "marketplace without plugins fails instead of skipping checks" 1 "no plugins"

setup renamed;        echo two > plug-a/SKILL.md; marketplace 1.1.0 1.0.0; sed -i.bak 's/"name":"plug-a"/"name":"plug-a2"/' .claude-plugin/marketplace.json; rm .claude-plugin/marketplace.json.bak
run_case "renamed plugin with changed files and no bump fails" 1 "VERSION: plug-a2 changed"

echo "$PASS passed, $FAIL failed"
[ "$FAIL" -eq 0 ]
