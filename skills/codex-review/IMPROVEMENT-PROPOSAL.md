# Codex Review Skill 改善提案

## 発見された問題

### 問題 1: シェル初期化によるタイムアウト（CRITICAL）

**症状:** `codex exec --sandbox read-only` 実行時、codex 内部で `bash -lc` を使用してコマンドを実行する。`-l`（ログインシェル）により `.bash_profile` / `.zshrc` 等が読み込まれ、以下のツールが初期化に時間を消費しタイムアウトする：

- **yarn**: キャッシュフォルダが書き込み不可の場合、10秒間ハングして `exited 124` (timeout)
- **pyenv**: `pyenv init -` の警告メッセージ出力で数秒遅延
- **nvm**: Node.js 環境の初期化で追加遅延

**影響:** codex の最初のシェルコマンドがタイムアウトし、レビューが進行不能になる。

**回避策（現在）:**
```bash
# sandbox を解除して実行（シェル初期化タイムアウトを回避）
codex exec --sandbox danger-full-access "..."
```

> **Warning:** `-c 'shell_environment_policy.inherit="none"'` は PATH 等の必要な環境変数まで消すため使用しないこと。codex が正常にコマンドを実行できなくなる。

**根本原因:** codex が `bash -lc` でコマンドを実行するため、ユーザーのシェルプロファイル全体が読み込まれる。

### 問題 2.5: `find .. -name AGENTS.md` によるタイムアウト（HIGH）

**症状:** codex は各セッション開始時に自動的に `find .. -name AGENTS.md -print` を実行してコンテキストを収集する。ホームディレクトリ直下のリポジトリでは `.subversion/auth`, `Pictures`, `Library` 等のアクセス不可ディレクトリに遭遇し、10秒のタイムアウトを消費する。これによりトークン予算を無駄遣いし、レビューが途中で打ち切られる。

**回避策:** codex の内部動作であり、ユーザー側での回避は困難。プロンプトに「AGENTS.md は存在しません。`find ..` は実行しないでください。」を追加することで軽減可能。

### 問題 2: `--sandbox read-only` でも `bash -lc` が使われる

**症状:** sandbox モードに関係なく、codex は常に `bash -lc` でコマンドを実行する。read-only sandbox でもログインシェル初期化が走り、同じタイムアウト問題が発生する。

### 問題 3: 大量出力時の切り詰め

**症状:** レビュー結果が大きい場合（8ファイル同時レビュー等）、Claude Code 側で出力が切り詰められる。`/Users/yasushi/.claude/.../tool-results/` に保存されるが、ユーザーが直接確認しづらい。

---

## 改善提案

### 1. skill.md のStep 3を修正

**現在:**
```bash
codex exec --sandbox read-only "<prepared_prompt>"
```

**改善案:**
```bash
# デフォルト（推奨）: sandbox解除 + シェル環境非継承でタイムアウト回避
codex exec --sandbox danger-full-access -c 'shell_environment_policy.inherit="none"' "<prepared_prompt>"

# シェル初期化が問題ない環境の場合:
codex exec --sandbox read-only "<prepared_prompt>"
```

### 2. Error Handling テーブルに追加

| Error | Cause | Solution |
|-------|-------|----------|
| `exited 124 in 10.01s` + yarn/pyenv/nvm エラー | ログインシェル初期化のタイムアウト | `--sandbox danger-full-access -c 'shell_environment_policy.inherit="none"'` を使用 |
| `warning Skipping preferred cache folder` | yarn キャッシュフォルダ権限不足 | 上記と同じ。または `yarn config set cache-folder ~/.yarn-cache` で修正 |
| `pyenv init - no longer sets PATH` | pyenv 設定の警告 | 上記と同じ |
| Output too large | レビュー対象が多い | ファイルを分割してレビュー、または `timeout` を 600000ms に設定 |

### 3. プロンプトにシェル指示を追加

レビュープロンプトの冒頭に以下を追加することで、codex が `bash -c` を優先使用するよう誘導する：

```
シェルコマンドを使う場合は bash -c を使い、bash -lc は使わないでください。
```

### 4. タイムアウト設定の明記

```bash
# Claude Code の Bash ツールから実行する場合、timeout を長めに設定
# デフォルト 120000ms → 300000ms (5分) 以上推奨
```

### 5. 出力解析のガイダンス強化

codex の出力は以下の構造を持つ：
```
thinking    → 推論過程（スキップ可）
Plan update → 進捗表示
exec        → 実行コマンドと結果
codex       → レビュー所見（最重要）
tokens used → トークン使用量
```

最終的な `codex` セクション（`tokens used` の直前）がレビュー結果本体。`thinking` と `exec` はデバッグ用。

---

## 推奨される skill.md の差分

```diff
 ### Step 3: Execute Codex Review

-```bash
-codex exec --sandbox read-only "<prepared_prompt>"
-```
+```bash
+# 推奨: シェル初期化タイムアウトを回避
+codex exec --sandbox danger-full-access \
+  -c 'shell_environment_policy.inherit="none"' \
+  "<prepared_prompt>"
+```

 **Critical notes:**
 - Always use `exec` subcommand (not interactive mode)
-- Always use `--sandbox read-only` for safety
+- `--sandbox danger-full-access` + `shell_environment_policy.inherit="none"` で
+  シェル初期化タイムアウトを回避（codex はレビュー専用なので書き込みリスクは低い）
+- プロンプト冒頭に「bash -c を使い、bash -lc は使わないでください」を追加
 - Command runs in background; may take 2-5 minutes
+- Claude Code の Bash ツールから実行する場合、timeout を 300000ms 以上に設定
 - Output includes thinking traces and final findings
```
