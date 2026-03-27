# ビッグテックにおける ADR のプラクティスとガバナンスモデル

世界の主要テクノロジー企業がどのように ADR を組織的に活用しているかを整理する。
AI による ADR 生成の際に「教師データ」として参照すべき基準と手法。

---

## 1. Amazon Web Services (AWS) — Prescriptive Guidance

### 核心思想: 不変性とチーム所有権

AWS は ADR を「技術的な意思決定を合理化し、チーム全員がその所有権を持つ」ためのツールとして位置づけている。

### ベストプラクティス

| プラクティス | 内容 |
|-------------|------|
| **不変の履歴** | ADR は削除しない。新しい決定が古いものを置き換える場合、古い記録を「Superseded」に変更し、新しい ADR へリンクする |
| **チーム全員の所有権** | ADR は特定のアーキテクトだけでなく、チーム全員が作成・レビューする |
| **リ・リティゲーションの防止** | 過去の「Superseded」な決定を参照可能にすることで、同じ議論の繰り返しを防ぐ |
| **ステータス管理** | Proposed → Accepted → Deprecated / Superseded のライフサイクルを厳密に管理 |
| **コードとの共存** | ADR はソースコードリポジトリに格納し、コードと同じバージョン管理を行う |

### AI 適用のポイント

- AI に ADR を生成させる前に、既存の「Superseded」な ADR をコンテキストとして読み込ませ、過去の失敗から学習させる
- ステータス遷移の自動提案: 新しい ADR が既存の ADR と矛盾する場合、AI が自動的に「Supersedes ADR-XXX」を提案する

### 参考リンク
- AWS Prescriptive Guidance: Best practices for ADR
  https://docs.aws.amazon.com/prescriptive-guidance/latest/architectural-decision-records/best-practices.html

---

## 2. Microsoft Azure — ATAM-Lite と Well-Architected Framework

### 核心思想: 量的スコアリングとリスク評価

Microsoft は Azure Well-Architected Framework において、意思決定のライフサイクルをフレームワーク化し、
ATAM（Architecture Tradeoff Analysis Method）の軽量版を日常の設計判断に適用している。

### 意思決定フロー

```
1. 問題のフレーミング
   └→ 何を解決しようとしているか？影響範囲は？

2. 選択肢の列挙
   └→ 最低3つの選択肢（現状維持を含む）

3. トレードオフのスコアリング（意思決定マトリクス）
   └→ Azure の5つの柱で各案を 1-5 で評価
      - 信頼性 (Reliability)
      - セキュリティ (Security)
      - コスト最適化 (Cost Optimization)
      - オペレーショナルエクセレンス (Operational Excellence)
      - パフォーマンス効率 (Performance Efficiency)

4. ATAM-Lite レビュー
   └→ 「敏感点（Sensitivity Points）」と「トレードオフポイント」の特定
   └→ リスクテーマの抽出

5. 意思決定と記録
   └→ ADR として記録、スコアの根拠を明記
```

### ATAM-Lite チェックポイント

| チェック項目 | 質問 |
|-------------|------|
| **敏感点** | この決定の小さな変化が、システムの品質属性に大きな影響を与えるか？ |
| **トレードオフ** | ある品質属性の改善が、別の品質属性を犠牲にしていないか？ |
| **リスク** | この決定が失敗した場合のビジネスインパクトは？ |
| **非リスク** | 明示的に「これは問題ない」と判断した点は？ |

### AI 適用のポイント

- AI に意思決定マトリクスを生成させ、各セルのスコアの根拠を自動記述させる
- ATAM-Lite の4つのチェックポイントをレビュープロンプトに組み込む

### 参考リンク
- Microsoft Tech Community: How Great Engineers Make Architectural Decisions
  https://techcommunity.microsoft.com/blog/azurearchitectureblog/how-great-engineers-make-architectural-decisions

---

## 3. Salesforce — プロンプトチェーンと Human-Led AI

### 核心思想: 人間主導、AI 支援の段階的アプローチ

Salesforce は ADR 作成を「人間が主導し、AI が支援する（Human-led, AI-powered）」アプローチで進め、
単一のプロンプトではなく、プロンプトをチェーン化（連鎖）させる手法を推奨している。

### プロンプトチェーン

```
Step 1: ビジネス課題の定義
  → AI に「評価基準」を抽出させる
  → Salesforce の3つの柱で評価:
     - Trusted（信頼: セキュリティ、データ保護）
     - Easy（容易: 開発者体験、運用負荷）
     - Adaptable（適応性: 拡張性、変更容易性）

Step 2: リサーチと要約
  → AI に各選択肢の技術調査を実行させる
  → 公式ドキュメント、ベンチマーク、コミュニティの評価を収集

Step 3: ADR ドラフト作成
  → Step 1-2 の結果を入力として ADR を生成
  → 必ず人間がレビューし、ドメイン知識を補完

Step 4: 人間によるレビューと承認
  → AI のドラフトはあくまで「叩き台」
  → 最終的な判断と責任は人間のアーキテクトにある
```

### AI 適用のポイント

- Step 1-3 を自動化し、Step 4 で人間のレビューを必須化するワークフローを構築する
- 各 Step の出力を次の Step の入力として渡す「チェーン」構造がポイント
- 一度に完璧な ADR を書こうとせず、段階的に品質を高める

### 参考リンク
- Salesforce Blog: Architectural Decisions — A Human-Led, AI-Powered Approach
  https://www.salesforce.com/blog/architectural-decisions-human-led-ai-powered-approach/

---

## 4. Google — Design Docs からの ADR 抽出

### 核心思想: 非公式な設計文書と正式な意思決定の橋渡し

Google では、正式な ADR よりも「Design Docs」と呼ばれる非公式な設計文書が広く使われている。
Design Docs はコーディング前に実装戦略と重要な設計判断を記録するもので、
ADR はその中の意思決定部分を抽出・構造化したものと位置づけられる。

### Design Docs と ADR の関係

```
Design Doc（設計文書）
  ├─ Context and Scope        → ADR の「コンテキスト」
  ├─ Goals and Non-Goals      → ADR の「制約事項」（KEP 形式に近い）
  ├─ The Actual Design        → 実装詳細（ADR の範囲外）
  ├─ Alternatives Considered  → ADR の「検討した代替案」
  └─ Cross-cutting Concerns   → ADR の「結果」に含める
```

### AI 適用のポイント

- 既存の Design Doc から ADR を自動抽出する「Design Doc → ADR 変換」パイプラインを構築可能
- Design Doc の「Alternatives Considered」セクションは、MADR の選択肢比較にそのまま変換できる
- Google の「Goals and Non-Goals」パターンは、スコープクリープを防ぐ強力な手法

### 参考リンク
- Google Design Docs (概念): https://www.industrialempathy.com/posts/design-docs-at-google/

---

## 5. Decision Guardian — CI/CD 連携によるガバナンス

### 核心思想: ADR を「生きたドキュメント」にする

Decision Guardian は GitHub Action として機能し、PR が「保護されたファイル」を変更した際に、
自動的に関連する ADR の文脈をコメントとして投稿する。

### 動作フロー

```
1. 開発者が PR を作成
2. Decision Guardian が変更されたファイルをスキャン
3. 関連する ADR を特定（ファイルパスと ADR の関連マッピング）
4. PR に ADR の文脈をコメントとして自動投稿
5. レビュアーが ADR を参照しながらコードレビュー
```

### 設定例

```yaml
# .github/decision-guardian.yml
decisions:
  - path: "src/database/**"
    adrs:
      - "docs/adr/0002-adopt-postgresql.md"
      - "docs/adr/0007-orm-usage-policy.md"
    message: "This PR modifies database-related code. Please review the above ADRs."

  - path: "src/auth/**"
    adrs:
      - "docs/adr/0003-jwt-authentication.md"
    message: "Authentication code changed. Ensure compliance with ADR-0003."
```

### AI 適用のポイント

- ADR とコードの対応マッピングを AI に自動生成させる
- PR レビュー時に AI が ADR 違反を検出する仕組みと組み合わせる

### 参考リンク
- Decision Guardian: https://github.com/DecispherHQ/decision-guardian

---

## 6. MCP Server 連携 — 組織知の AI アクセス

### 核心思想: ADR を AI アシスタントから検索可能にする

MCP（Model Context Protocol）サーバーを用いて、組織内の ADR、設計指針、コーディング規約を
AI アシスタントからクエリ可能にする最新のアプローチ。

### アーキテクチャ

```
[開発者] → [Claude Code / Copilot]
              ↓ MCP クエリ
          [MCP Server]
              ↓ RAG 検索
          [ADR リポジトリ]
              ↓
          [関連する ADR を返却]
```

### 効果

- 「なぜこの通信プロトコルを使っているのか？」→ AI が正確な ADR に基づいて回答
- 新規 ADR 作成時に、AI が既存 ADR との矛盾を自動検出
- オンボーディング時に、AI が ADR を根拠にシステムの「なぜ」を説明

### AI 適用のポイント

- RAG（検索拡張生成）を通じて、AI が最新の ADR を常に参照できる状態を維持する
- ADR の変更を検知し、AI の回答が古い ADR に基づかないようキャッシュを無効化する

### 参考リンク
- HexMaster Blog: MCP Server to Guide Copilot
  https://hexmaster.nl/posts/mcp-server-to-guide-copilot/

---

## ガバナンス比較サマリー

| 企業/ツール | フレームワーク | 意思決定の鍵 | AI 統合シナリオ |
|------------|---------------|-------------|----------------|
| **AWS** | Prescriptive Guidance | チーム全員の所有権、不変の履歴 | 過去の失敗からの学習、履歴管理 |
| **Microsoft** | Well-Architected (Azure) | 意思決定マトリクス、リスク評価 | 量的スコアリング、シナリオ分析 |
| **Salesforce** | Well-Architected (SF) | 3つの柱 (Trusted, Easy, Adaptable) | プロンプトチェーン、基準の自動生成 |
| **Google** | Design Docs (Internal) | 設計文書との統合 | Design Doc → ADR 自動変換 |
| **Decision Guardian** | GitHub Action | PR と ADR の自動紐付け | ADR 違反の自動検出 |
| **MCP Server** | Model Context Protocol | RAG による組織知アクセス | ADR ベースの AI 回答 |
