---
name: codex-review
description: |
  Execute comprehensive code reviews using OpenAI Codex CLI. Use when: (1) reviewing git commits by ID or range, (2) reviewing pull requests by number, (3) requesting thorough code quality analysis. Triggers on phrases like "codex review", "review commit", "review PR", "レビュー". Requires codex CLI to be installed and authenticated.
---

# Codex Review

Execute code reviews via OpenAI Codex CLI with comprehensive analysis.

## Prerequisites Check

Before proceeding, verify codex CLI availability:

```bash
which codex && codex --version
```

If codex is not found, inform the user and abort.

## Workflow

### Step 1: Collect Review Context

Run the context collection script or gather information manually:

```bash
# Using script
scripts/prepare_review_context.sh <target>

# Or manually for commits:
git log -1 --format="%H%n%s%n%b" <commit_id>
git diff-tree --no-commit-id --name-status -r <commit_id>
git show <commit_id>

# For PRs:
gh pr view <number> --json title,body,files
gh pr diff <number>
```

### Step 2: Prepare Review Prompt

Structure the prompt with these sections:

```
以下のコードをレビューしてください。

## 1. 対象ファイル
- コミットID/PR: <id>
- 変更ファイル:
  - <file1>
  - <file2>

## 2. セッションのゴールと受入基準
<what success looks like>

## 3. 解決しようとした課題
<problems being addressed>

## 4. 成果と変更点
<summary of changes>
```

### Step 3: Execute Codex Review

```bash
codex exec --sandbox read-only "<prepared_prompt>"
```

**Critical notes:**
- Always use `exec` subcommand (not interactive mode)
- Always use `--sandbox read-only` for safety
- Command runs in background; may take 2-5 minutes
- Output includes thinking traces and final findings

### Step 4: Interpret Results

Codex outputs contain:
- `thinking` - reasoning traces (can be skipped)
- `exec` - commands executed by codex
- `codex` or final text - actual review findings

Extract and summarize:
1. **Findings** - issues found (or "None" if clean)
2. **Residual Risks** - potential future problems
3. **Recommendations** - actionable improvements

## Review Perspectives

For comprehensive reviews, ensure codex examines these areas. See [references/review-perspectives.md](references/review-perspectives.md) for detailed checklist.

| Category | Key Points |
|----------|------------|
| Correctness | Logic errors, edge cases, null handling |
| Security | Input validation, auth, secrets |
| Performance | N+1 queries, memory leaks, blocking ops |
| Maintainability | Duplication, naming, complexity |
| Testing | Coverage, isolation, assertions |

## Error Handling

| Error | Cause | Solution |
|-------|-------|----------|
| `stdout is not a terminal` | Using interactive mode | Use `codex exec` instead |
| `command not found` | codex not installed | Install via npm/brew |
| Timeout | Large diff or slow network | Increase timeout, split review |
| Auth error | Token expired | Run `codex login` |

## Example Session

```
User: codex で最新コミットをレビューして

Claude:
1. Check codex availability: `which codex && codex --version`
2. Collect context:
   - git log -1 --format="%H%n%s%n%b" HEAD
   - git diff-tree --no-commit-id --name-status -r HEAD
   - git show HEAD
3. Prepare prompt with 4 sections
4. Execute: codex exec --sandbox read-only "<prompt>"
5. Summarize findings for user
```

## Scripts

- `scripts/prepare_review_context.sh <target>` - Collects git context for commit/range/PR