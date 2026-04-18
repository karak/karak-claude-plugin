#!/usr/bin/env bash
# Fail if any sub-plugin copy has drifted from its canonical source in root skills/ or agents/.
set -euo pipefail

REPO_ROOT="$(cd "$(dirname "$0")/.." && pwd)"
FAILED=0

check_copy() {
    local canonical="$1"
    local copy="$2"
    if ! diff -rq "$canonical" "$copy" >/dev/null 2>&1; then
        echo "DRIFT: $copy differs from $canonical"
        FAILED=1
    fi
}

# karak-design
for skill in google-design-docs apple-design icon-design frontend-aesthetics \
             ux-psychologist material-design hifi-design-quality mobile-auth-screen-design; do
    check_copy "$REPO_ROOT/skills/$skill" "$REPO_ROOT/karak-design/skills/$skill"
done
check_copy "$REPO_ROOT/agents/ui-designer.md" "$REPO_ROOT/karak-design/agents/ui-designer.md"

# karak-architecture
check_copy "$REPO_ROOT/skills/write-c4-diagram" "$REPO_ROOT/karak-architecture/skills/write-c4-diagram"
check_copy "$REPO_ROOT/agents/system-designer.md" "$REPO_ROOT/karak-architecture/agents/system-designer.md"
check_copy "$REPO_ROOT/agents/gcp-infrastructure-engineer.md" "$REPO_ROOT/karak-architecture/agents/gcp-infrastructure-engineer.md"

# karak-engineering
check_copy "$REPO_ROOT/skills/codex-review" "$REPO_ROOT/karak-engineering/skills/codex-review"
check_copy "$REPO_ROOT/agents/code-refactorer.md" "$REPO_ROOT/karak-engineering/agents/code-refactorer.md"
check_copy "$REPO_ROOT/agents/quality-assurance-manager.md" "$REPO_ROOT/karak-engineering/agents/quality-assurance-manager.md"

# karak-product
check_copy "$REPO_ROOT/agents/requirements-analyst.md" "$REPO_ROOT/karak-product/agents/requirements-analyst.md"
check_copy "$REPO_ROOT/agents/agile-project-manager.md" "$REPO_ROOT/karak-product/agents/agile-project-manager.md"

if [ "$FAILED" -eq 1 ]; then
    echo "Sync check FAILED. Re-copy from canonical sources."
    exit 1
fi
echo "All sub-plugin copies are in sync."
