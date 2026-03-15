---
name: write-c4-diagram
description: "C4モデルに基づくシステムアーキテクチャ図を PlantUML (C4-PlantUML) で作成する。4つの抽象レベル (Context, Container, Component, Code) を正しい依存順序で生成し、レベル間の整合性を保証する。MUST trigger when: C4 ダイアグラム作成、アーキテクチャ図作成、システム構成図作成、PlantUML C4 図の作成・レビュー。Also triggers on keywords like 'C4', 'C4 diagram', 'container diagram', 'component diagram', 'system context', 'architecture diagram', 'アーキテクチャ図', 'システム構成図'."
---

# Write C4 Diagram

C4モデル (Context / Container / Component / Code) に基づくアーキテクチャ図を PlantUML で作成するスキル。

---

## 核心原則: 抽象レベルを守る

| Level | 名称 | 聴衆 | 粒度 | include |
|---|---|---|---|---|
| 1 | System Context | 全員 | システム全体が1箱 | `C4_Context.puml` |
| 2 | Container | 開発チーム | アプリ・DB・キュー等 | `C4_Container.puml` |
| 3 | Component | 開発者 | Blueprint/Service/Repository 等 | `C4_Component.puml` |
| 4 | Code | 開発者 | クラス・モジュール・関数 | `C4_Component.puml`（Code 用はない） |

**抽象レベルの混在を即座に検知する:**
「Context 図に PostgreSQL を入れたい」という要求が来たら→ L2 の話であることを説明し、L1 を正しく作った上で L2 も提供する。要求を拒絶して終わるのは最悪のパターン。

---

## タスク判定 → 参照ファイルのロード

まず以下の問いに答えてから参照ファイルを読む。

### これは「新規システム設計」か「既存コードベース分析」か？

**新規システム設計** — ゼロベースで設計するシステム、まだコードが存在しない、または要件定義フェーズ
→ **`references/workflow-create.md` を読む**（初期思考フェーズ → 4レベル作成テンプレート）

**既存コードベース分析** — 既存の実装からアーキテクチャ図を起こす、リバースエンジニアリング
→ **`references/workflow-analyze.md` を読む**（コードベース調査 Step 0 → 要素抽出ガイド）

---

## 随時参照できるリファレンス

作業中に必要になったら読む。最初から全部読む必要はない。

| ファイル | 内容 | 読むタイミング |
|---|---|---|
| `references/syntax-guide.md` | PlantUML 構文・要素の引数・よくあるエラー | 構文に迷ったとき |
| `references/consistency-rules.md` | レベル間命名一致マトリクス・ズームイン検証手順 | 複数レベル作成後のレビュー時 |
| `references/pitfalls.md` | 繰り返し発生する7つの失敗パターンと対処 | 問題が発生したとき・完成レビュー時 |
