---
name: codex-review
description: |
  Execute comprehensive code reviews using OpenAI Codex CLI. Use when: (1) reviewing git commits by ID or range, (2) reviewing pull requests by number, (3) requesting thorough code quality analysis. Triggers on phrases like "codex review", "review commit", "review PR", "レビュー". Requires codex CLI to be installed and authenticated.
---

# Codex Review

Execute code reviews via OpenAI Codex CLI with comprehensive analysis.
Session resume enables fast re-reviews without re-scanning the codebase.

## Prerequisites

```bash
which codex && codex --version
```

If codex is not found, inform the user and abort.

## Quick Reference: Two Paths

| Situation | Path | Typical time |
|-----------|------|-------------|
| First review of a target | **Initial Review** (Steps 1→2→3) | 2-5 min |
| Re-review after fixes | **Fast Re-review** (Step 4 only) | 30-90 sec |

Decide which path by checking for an existing session:

```bash
export CODEX_SESSIONS_DIR=~/.claude/projects/<project>/memory
python3 scripts/session_manager.py lookup "<target>" 2>/dev/null
```

- Session found → **Fast Re-review** (Step 4). Do NOT ask the user for confirmation — just resume.
- No session → **Initial Review** (Step 1).

---

## Initial Review

### Step 1: Collect Context

```bash
# Using script (commit, range, or PR number)
scripts/prepare_review_context.sh <target>
```

Or manually:
```bash
# Commits
git log -1 --format="%H%n%s%n%b" <commit_id>
git diff-tree --no-commit-id --name-status -r <commit_id>
git show <commit_id>

# PRs
gh pr view <number> --json title,body,files
gh pr diff <number>
```

### Step 2: Execute Review

Build the prompt and run codex in a single command. The session ID is extracted
and saved automatically via the pipeline script.

**Prompt template:**

```
シェルコマンドを使う場合は bash -c を使い、bash -lc は使わないでください。
AGENTS.md は存在しません。find .. は実行しないでください。

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

**Execute + extract + save in one pipeline:**

```bash
export CODEX_SESSIONS_DIR=~/.claude/projects/<project>/memory
codex exec --json --sandbox danger-full-access "<prompt>" 2>&1 \
  | tee /tmp/codex-review-output.jsonl \
  | python3 scripts/extract_and_save_session.py - "<target>" "<description>"
```

This single command: runs the review, extracts the session ID from the JSONL
stream, saves it to the memory file, and prints the session ID.

Set Bash tool timeout to **300000ms** or higher.

### Step 3: Summarize Findings

Extract the review from JSONL output:

```bash
python3 -c "
import sys, json
for line in open('/tmp/codex-review-output.jsonl'):
    evt = json.loads(line)
    if evt.get('type')=='item.completed' and evt.get('item',{}).get('type')=='agent_message':
        print(evt['item']['text'])
"
```

Summarize into three sections:
1. **Findings** — issues found (or "None")
2. **Residual Risks** — potential future problems
3. **Recommendations** — actionable improvements

Report the session ID: `Codex セッション ID: <uuid> — 再レビュー時に自動再開します。`

---

## Fast Re-review

When a session exists, skip all context collection. Codex already has full
context from the previous session — just send the new changes.

### Step 4: Resume and Review

```bash
# Collect only the new diff (minimal context)
DIFF=$(git diff HEAD~1 --stat && echo "---" && git diff HEAD~1)

# Resume — codex retains prior context, no re-scanning
codex exec resume "<session_id>" "前回のレビューで指摘された問題を修正しました。以下の変更を確認してください。

$DIFF"
```

That's it. Summarize the output and report findings.

**Re-review prompt variants:**

```
# Security-focused re-review
前回のレビューに加えて、セキュリティの観点から追加レビューをお願いします。

# Deep dive on specific file
前回レビューした中で <filename> をより詳細にレビューしてください。

# Verify fixes
以下の修正が前回の指摘を適切に解消しているか確認してください。
<diff>
```

**Notes on resume:**
- `codex exec resume` does not accept `--sandbox` or `--json` directly
- Use `-c 'sandbox_permissions=["disk-full-read-access"]'` if needed
- If session not found (expired/invalid), fall back to Initial Review

---

## Review Perspectives

For comprehensive reviews, ensure codex examines these areas.
See [references/review-perspectives.md](references/review-perspectives.md) for the full checklist.

| Category | Key Points |
|----------|------------|
| Correctness | Logic errors, edge cases, null handling |
| Security | Input validation, auth, secrets |
| Performance | N+1 queries, memory leaks, blocking ops |
| Maintainability | Duplication, naming, complexity |
| Testing | Coverage, isolation, assertions |

## Session Management

Sessions are stored in the project memory file for cross-conversation persistence:

```
File: ~/.claude/projects/<project>/memory/codex-sessions.md

# Codex Review Sessions
- <branch/PR>: <session_id> (<date>, <brief description>)
```

**Scripts:**
- `scripts/extract_and_save_session.py <jsonl|-> <target> <desc>` — Extract session ID from JSONL + save (combined)
- `scripts/session_manager.py <save|lookup|list|delete> [args]` — Manage session IDs
- `scripts/prepare_review_context.sh <target>` — Collect git context
- `scripts/extract_session_id.py <jsonl|->` — Extract session ID only (legacy)

## Error Handling

| Error | Cause | Solution |
|-------|-------|----------|
| `stdout is not a terminal` | Using interactive mode | Use `codex exec` instead |
| `command not found` | codex not installed | Install via npm/brew |
| Timeout | Large diff or slow network | Increase timeout to 600000ms, split review |
| Auth error | Token expired | Run `codex login` |
| `exited 124` + yarn/pyenv/nvm error | Login shell init timeout | `--sandbox danger-full-access` (already default) |
| `warning Skipping preferred cache folder` | yarn cache permission | Above, or `yarn config set cache-folder ~/.yarn-cache` |
| Output too large | Too many files | Split into smaller reviews |
| Session not found (resume) | Invalid/expired session ID | Fall back to Initial Review |

## Tests

```bash
cd <skill_dir> && python3 -m unittest tests.test_extract_session_id tests.test_session_manager -v
```
