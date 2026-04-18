#!/bin/bash
# prepare_review_context.sh - Collect git context for code review
# Usage: ./prepare_review_context.sh [commit_id|commit_range|PR_number]

set -e

# Parse argument
TARGET="${1:-HEAD}"

# Detect target type
if [[ "$TARGET" =~ ^[0-9]+$ ]]; then
    # PR number
    TARGET_TYPE="pr"
elif [[ "$TARGET" =~ \.\. ]]; then
    # Commit range (e.g., abc123..def456)
    TARGET_TYPE="range"
else
    # Single commit ID
    TARGET_TYPE="commit"
fi

echo "## Review Target"
echo "- Type: $TARGET_TYPE"
echo "- Target: $TARGET"
echo ""

case "$TARGET_TYPE" in
    "pr")
        echo "## PR Information"
        gh pr view "$TARGET" --json title,body,files,commits 2>/dev/null || {
            echo "Error: Failed to fetch PR #$TARGET. Ensure gh CLI is authenticated."
            exit 1
        }
        echo ""
        echo "## PR Diff"
        gh pr diff "$TARGET" 2>/dev/null || exit 1
        ;;
    "range")
        echo "## Commit Range"
        git log --oneline "$TARGET" 2>/dev/null || {
            echo "Error: Invalid commit range: $TARGET"
            exit 1
        }
        echo ""
        echo "## Changed Files"
        git diff --stat "$TARGET" 2>/dev/null || exit 1
        echo ""
        echo "## Full Diff"
        git diff "$TARGET" 2>/dev/null || exit 1
        ;;
    "commit")
        # Validate commit exists
        git rev-parse --verify "$TARGET" >/dev/null 2>&1 || {
            echo "Error: Invalid commit: $TARGET"
            exit 1
        }
        echo "## Commit Information"
        git log -1 --format="- Hash: %H%n- Author: %an <%ae>%n- Date: %ai%n- Subject: %s%n%n### Message%n%b" "$TARGET" 2>/dev/null
        echo ""
        echo "## Changed Files"
        git diff-tree --no-commit-id --name-status -r "$TARGET" 2>/dev/null
        echo ""
        echo "## Diff Statistics"
        git show --stat "$TARGET" 2>/dev/null | tail -1
        echo ""
        echo "## Full Diff"
        git show "$TARGET" --format="" 2>/dev/null
        ;;
esac
