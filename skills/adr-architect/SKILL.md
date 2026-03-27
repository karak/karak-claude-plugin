---
name: adr-architect
description: |
  アーキテクチャ意思決定記録（ADR: Architecture Decision Record）の作成・更新・レビューを支援する統合スキル。
  Nygard / MADR / Y-Statement / AgDR の4テンプレートを状況に応じて使い分け、
  ビッグテック（AWS, Microsoft, Salesforce, Google）やOSS（Kubernetes KEP, Rust RFC, Backstage）の
  ベストプラクティスに基づいた高品質なADRを生成する。

  MUST trigger when: ADR作成、アーキテクチャ意思決定記録、設計判断の記録、ADRレビュー、ADR更新、
  技術選定の記録、アーキテクチャ決定、design decision record。
  Also triggers on: 「なぜこの技術を選んだか記録したい」「設計判断を残したい」「ADRテンプレート」
  「技術選定の比較表」「アーキテクチャレビュー」「decision log」「RFC作成」。
---

# ADR Architect

アーキテクチャ意思決定記録（ADR）の作成・更新・レビューを支援するスキル。
Martin Fowler が提唱した ADR の概念を基盤に、ビッグテックと OSS の実践知を統合した包括的フレームワーク。

---

## 核心原則: ADR は「なぜ」を残す

ADR の価値は「何を選んだか」ではなく「なぜその選択に至ったか」を記録することにある。
背景（Context）・検討した代替案（Alternatives）・トレードオフ・結果として生じる影響を、コードと共にバージョン管理する。

**Martin Fowler の3原則:**
1. **逆ピラミッド（Inverted Pyramid）**: 最も重要な情報を冒頭に書く。短く（数ページ）保つ
2. **不変性（Immutability）**: 決定が変わっても ADR を修正しない。新しい ADR で Supersede する
3. **二重の価値**: (1) 数ヶ月後・数年後に「なぜ」を理解するための歴史的記録、(2) 書く行為自体が思考を明確にし、異なる視点を浮かび上がらせる

---

## タスク判定

ユーザーの要求を以下の3つに分類し、対応するワークフローを実行する。

### 1. ADR を新規作成する

→ **`references/format-selection-guide.md` を読み**、最適なテンプレートを選定
→ **`references/templates.md` を読み**、選定したテンプレートで ADR を執筆

**プロンプトチェーン（段階的生成）を必ず適用する:**

1. **文脈の収集**: コードベース、既存 ADR、Issue/Discussion を確認
2. **Y-Statement の生成**: まず一文で意思決定の核を要約する
3. **評価基準の定義**: ビジネス目標・技術制約から評価軸をリストアップ
4. **代替案のリサーチ**: 各選択肢の長所・短所を比較表で整理
5. **ドラフト生成**: 選定テンプレートに従い ADR を執筆
6. **レビュー指摘**: 自己レビューを行い改善点を提示

### 2. 既存 ADR を更新する

→ 既存の ADR ファイルを読み、以下のルールに従って更新

**更新の原則（AWS Prescriptive Guidance に基づく）:**
- ADR は **不変（Immutable）** である — 既存の ADR を削除・上書きしてはならない
- 新しい決定が古い決定を置き換える場合:
  1. 古い ADR のステータスを `Superseded by [ADR-XXX]` に変更
  2. 新しい ADR を作成し、古い ADR へのリンクを含める
- ステータスの遷移: `Proposed` → `Accepted` → `Deprecated` / `Superseded`

### 3. ADR をレビューする

→ **`references/review-checklist.md` を読み**、チェックシートに基づいてレビュー
→ 必要に応じて **`references/bigtech-practices.md`** のガバナンスモデルを参照

---

## フォーマット選択の早見表

| 状況 | 推奨フォーマット | 理由 |
|------|-----------------|------|
| アジャイル開発での素早い記録 | **Nygard** | シンプルで因果関係が明確 |
| 複数技術の厳密な比較評価 | **MADR** | トレードオフの構造化に最適 |
| エグゼクティブ向け要約 | **Y-Statement** | 一文で核心を伝達 |
| AI エージェントの判断記録 | **AgDR** | モデル・プロンプトのメタデータ保持 |
| 大規模 OSS への提案 | **KEP / RFC 形式** | Goals/Non-Goals で境界を明示 |

詳細は `references/format-selection-guide.md` を参照。

---

## 随時参照できるリファレンス

作業中に必要になったら読む。最初から全部読む必要はない。

| ファイル | 内容 | 読むタイミング |
|---|---|---|
| `references/templates.md` | 4つの ADR テンプレート（Nygard, MADR, Y-Statement, AgDR） | ADR を執筆するとき |
| `references/format-selection-guide.md` | フォーマット選択の詳細ガイドと比較表 | どのテンプレートを使うか迷ったとき |
| `references/bigtech-practices.md` | AWS, Microsoft, Salesforce, Google のプラクティス | ガバナンスや評価手法を参考にしたいとき |
| `references/oss-examples.md` | Kubernetes KEP, Rust RFC, Backstage の実例 | 実際の ADR の書き方を参考にしたいとき |
| `references/review-checklist.md` | ADR レビュー用チェックシート（ATAM-Lite 含む） | ADR をレビュー・評価するとき |

---

## ADR の配置規約

```
docs/adr/                    # または docs/architecture-decisions/
├── 0001-use-markdown-adr.md
├── 0002-adopt-postgresql.md
├── 0003-api-versioning-strategy.md
└── ...
```

- ファイル名: `NNNN-kebab-case-title.md`（4桁の連番）
- 配置先: プロジェクトルートの `docs/adr/` を推奨（コードと共にバージョン管理）
- 既存プロジェクトに ADR ディレクトリがある場合はその慣習に従う

---

## 品質基準

高品質な ADR は以下の条件を満たす:

1. **文脈が具体的**: 「パフォーマンスが悪い」ではなく「P95 レイテンシが 500ms を超える」
2. **代替案が複数**: 最低2つの代替案を検討し、却下理由を明記
3. **トレードオフが明示的**: 選択の正の影響と負の影響の両方を記述
4. **根拠がコードに紐づく**: 抽象論ではなく具体的なコード・制約に言及
5. **「しなかった場合」のリスク**: この決定をしなかった場合に何が起こるかを記述
6. **ハルシネーションの排除**: 架空の製品・機能を捏造しない
