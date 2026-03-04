---
name: codex-review
description: |
  Execute comprehensive code reviews using OpenAI Codex CLI. Use when: (1) reviewing git commits by ID or range, (2) reviewing pull requests by number, (3) requesting thorough code quality analysis. Triggers on phrases like "codex review", "review commit", "review PR", "レビュー". Requires codex CLI to be installed and authenticated.
---

# Codex Review

Execute code reviews via OpenAI Codex CLI with comprehensive analysis.
Supports session resume for efficient re-reviews.

## Prerequisites Check

Before proceeding, verify codex CLI availability:

```bash
which codex && codex --version
```

If codex is not found, inform the user and abort.

## Session Management

Codex sessions can be resumed to avoid re-scanning the codebase on re-reviews.

**Key concept:** After an initial review, extract and store the `session id` (UUID).
On subsequent reviews of the same scope, use `codex exec resume` to continue
from where the previous session left off.

### Session ID Storage

Store session IDs as a Claude Code auto memory so they persist across conversations:

```
File: ~/.claude/projects/<project>/memory/codex-sessions.md

# Codex Review Sessions
- <branch/PR>: <session_id> (<date>, <brief description>)
```

## Workflow

### Step 0: Check for Existing Session

Before starting a new review, check if there is an existing session to resume:

1. Check for existing session:
   ```bash
   export CODEX_SESSIONS_DIR=~/.claude/projects/<project>/memory
   python3 scripts/session_manager.py lookup "<target>"
   ```
2. If a session ID is returned for the current review target (branch, PR, or commit range):
   - Ask the user: "前回のセッション `<session_id>` を再開しますか？ それとも新規レビューを開始しますか？"
   - If resume → go to **Step 3b (Resume Review)**
   - If new → go to **Step 1**
3. If no existing session → go to **Step 1**

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

### Step 3a: Execute Initial Review

Use `--json` to capture the session ID from the JSONL output:

```bash
# 初回レビュー: --json で実行しセッション ID を取得
codex exec --json --sandbox danger-full-access "<prepared_prompt>" 2>&1 | tee /tmp/codex-review-output.jsonl
```

**After execution, extract the session ID:**

```bash
# JSONL 出力からセッション ID を抽出（Python3 スクリプト使用）
SESSION_ID=$(python3 scripts/extract_session_id.py /tmp/codex-review-output.jsonl)
echo "Session ID: $SESSION_ID"
```

**Save the session ID** to the project memory file for future re-reviews:

```bash
# メモリファイルにセッション ID を保存（Python3 スクリプト使用）
export CODEX_SESSIONS_DIR=~/.claude/projects/<project>/memory
python3 scripts/session_manager.py save "<branch/PR>" "$SESSION_ID" "<brief description>"
```

Also report the session ID to the user:
```
Codex セッション ID: <session_id>
再レビュー時はこの ID でセッションを再開できます。
```

**Critical notes for initial review:**
- Always use `exec` subcommand (not interactive mode)
- `--json` outputs JSONL; the first event `thread.started` contains `thread_id`
- `--sandbox danger-full-access` でシェル初期化タイムアウトを回避
- Claude Code の Bash ツールから実行する場合、timeout を 300000ms 以上に設定
- Command runs in background; may take 2-5 minutes

### Step 3b: Resume Review (Re-review)

When resuming with an existing session ID, codex retains full context from
the previous session—no codebase re-scanning needed:

```bash
# 再レビュー: セッション再開で前回のコンテキストを引き継ぐ
codex exec resume "<session_id>" "<follow_up_prompt>"
```

**Re-review prompt examples:**

```
# 修正後の再レビュー
前回のレビューで指摘された問題を修正しました。以下の変更を確認してください。
<git diff or summary of fixes>

# 追加観点でのレビュー
前回のレビューに加えて、セキュリティの観点から追加レビューをお願いします。

# 特定ファイルの深掘り
前回レビューした中で <filename> をより詳細にレビューしてください。
```

**Critical notes for resume:**
- `codex exec resume` は `--sandbox` や `--json` を直接受け付けない
- オプション指定は `-c` を使用: `-c 'sandbox_permissions=["disk-full-read-access"]'`
- セッションが見つからない場合はエラーになるので、その場合は Step 3a に切り替え
- テキスト出力のヘッダーに `session id:` が表示されるので確認可能

### Step 4: Interpret Results

**For `--json` (initial review) output:**

JSONL イベント構造:
- `{"type":"thread.started","thread_id":"..."}` — セッション ID
- `{"type":"item.completed","item":{"type":"reasoning",...}}` — 推論過程（スキップ可）
- `{"type":"item.completed","item":{"type":"command_execution",...}}` — 実行コマンドと結果
- `{"type":"item.completed","item":{"type":"agent_message",...}}` — レビュー所見
- `{"type":"turn.completed","usage":{...}}` — トークン使用量

最終的な `agent_message` イベントがレビュー結果本体。

```bash
# JSONL から agent_message のみ抽出
cat /tmp/codex-review-output.jsonl | python3 -c "
import sys, json
for line in sys.stdin:
    evt = json.loads(line)
    if evt.get('type') == 'item.completed' and evt.get('item',{}).get('type') == 'agent_message':
        print(evt['item']['text'])
"
```

**For text output (resume review):**

Codex outputs contain:
- `thinking` — reasoning traces (can be skipped)
- `exec` — commands executed by codex
- `codex` or final text — actual review findings
- `tokens used` — token consumption

Extract and summarize:
1. **Findings** — issues found (or "None" if clean)
2. **Residual Risks** — potential future problems
3. **Recommendations** — actionable improvements

### Step 5: Update Session Memory

After each review (initial or resumed), update the memory file:

```bash
# セッション情報を更新（最終レビュー日時など）
# codex-sessions.md のエントリを更新
```

If a review cycle is complete (all issues resolved), optionally archive the session:
```
# Completed: <session_id> (<date>, PR #123 approved)
```

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
| `exited 124` + yarn/pyenv/nvm エラー | ログインシェル初期化のタイムアウト | `--sandbox danger-full-access` を使用 |
| `warning Skipping preferred cache folder` | yarn キャッシュフォルダ権限不足 | 上記と同じ、または `yarn config set cache-folder ~/.yarn-cache` |
| Output too large | レビュー対象が多い | ファイルを分割してレビュー、または timeout を 600000ms に設定 |
| Session not found (resume) | セッション ID が無効/期限切れ | Step 3a で新規セッションを開始 |

## Example Sessions

### Initial Review
```
User: codex で最新コミットをレビューして

Claude:
1. Check for existing session in memory → none found
2. Check codex availability: `which codex && codex --version`
3. Collect context:
   - git log -1 --format="%H%n%s%n%b" HEAD
   - git diff-tree --no-commit-id --name-status -r HEAD
   - git show HEAD
4. Prepare prompt with 4 sections
5. Execute: codex exec --json --sandbox danger-full-access "<prompt>" | tee /tmp/codex-review-output.jsonl
6. Extract session ID from JSONL output
7. Save session ID to memory file
8. Summarize findings for user
9. Report: "Codex セッション ID: <uuid> — 再レビュー時に再開できます"
```

### Re-review (Resume)
```
User: 修正したので codex で再レビューして

Claude:
1. Check memory for existing session → found <session_id>
2. Ask user: "前回のセッション <session_id> を再開しますか？"
3. User: はい
4. Collect context of new changes: git diff HEAD~1
5. Execute: codex exec resume "<session_id>" "<re-review prompt>"
6. Summarize findings for user
```

## Scripts

- `scripts/prepare_review_context.sh <target>` - Collects git context for commit/range/PR
- `scripts/extract_session_id.py <jsonl_file | ->` - Extracts thread_id from codex JSONL output
- `scripts/session_manager.py <save|lookup|list|delete> [args]` - Manages session IDs in memory file

## Tests

```bash
cd <skill_dir> && python3 -m unittest tests.test_extract_session_id tests.test_session_manager -v
```
