# Codex Review Skill 改善履歴

## v2 改善 (2026-03-06): 速度最適化

### 変更内容

1. **再レビューの自動再開** — ユーザー確認 ("再開しますか？") を排除し、セッション検出時は即座に resume
2. **ワークフロー簡素化** — 6ステップ分岐フロー → 2パス明確分離 (Initial Review 3ステップ / Fast Re-review 1ステップ)
3. **パイプライン統合** — `extract_and_save_session.py` で extract + save を1コマンドに
4. **SKILL.md 短縮** — 290行 → 170行（冗長な例示・重複説明を削除）

### ベンチマーク結果

4並列サブエージェントによるワークフロートレース比較 (2026-03-06実施)

#### 再レビュー (主要最適化対象)

| 指標 | 旧スキル | 新スキル | 改善 |
|------|---------|---------|------|
| Tool calls | 7 | 5 | -29% |
| ユーザー確認待ち | 1回 | 0回 | 排除 |
| エージェント消費トークン | 21,975 | 14,988 | -32% |
| エージェント実行時間 | 72.7s | 55.3s | -24% |

#### 初回レビュー

| 指標 | 旧スキル | 新スキル | 改善 |
|------|---------|---------|------|
| Tool calls | 10 | 8 | -20% |
| Post-codex commands | 3 | 2 | -33% |
| エージェント消費トークン | 16,112 | 15,451 | -4% |

#### アサーション結果

| テスト項目 | 旧 | 新 |
|-----------|---|---|
| 再レビューで確認を求めない | FAIL | PASS |
| codex exec resume 実行 | PASS | PASS |
| session_manager.py lookup 実行 | PASS | PASS |
| codex exec --json 実行（初回） | PASS | PASS |
| セッションID保存 | PASS | PASS |

**結論:** 精度変化なし、再レビュー速度 -29% tool calls / -32% tokens / 確認待ち排除

### エビデンス

- トレースファイル: `codex-review-workspace/iteration-1/eval-*/trace.md`
- ベンチマーク: `codex-review-workspace/iteration-1/benchmark.md`
- ユニットテスト: 29件全通過 (test_extract_session_id + test_session_manager + test_extract_and_save_session)

---

## v1 既知の問題 (発見日: 2026-01-18 ~ 2026-03-04)

### 問題 1: シェル初期化によるタイムアウト（CRITICAL → v2で対応済み）

codex 内部で `bash -lc` を使用。yarn/pyenv/nvm の初期化でタイムアウト。
回避策: `--sandbox danger-full-access` (v2でデフォルト化)

### 問題 2: `find .. -name AGENTS.md` によるタイムアウト（HIGH → v2で対応済み）

codex が自動実行する `find ..` がホームディレクトリを走査。
回避策: プロンプトに「AGENTS.md は存在しません」を追加 (v2で組込済み)

### 問題 3: 大量出力時の切り詰め

8ファイル同時レビュー等で出力がClaude Code側で切り詰められる。
回避策: ファイルを分割してレビュー、timeout を 600000ms に設定
