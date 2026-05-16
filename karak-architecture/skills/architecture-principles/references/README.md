# architecture-principles / references

`architecture-principles` スキル（フェーズ2で SKILL.md 化予定）のための **ナレッジベース**。

このディレクトリの内容は、特定言語・特定クラウド・特定実装に依存しない
「組織運営と事業価値に接続する」アーキテクチャ原則の用語と概念マップを提供する。

## ファイル一覧

| ファイル | 内容 | 想定読者 |
|---|---|---|
| [glossary.ja.md](./glossary.ja.md) | 用語集（日本語、原語併記、出典付き）。2024-2025 追加概念（DX Core 4 / DevEx / Architecture Modernization / AMET / Rework Rate / Aporetic / Product Operating Model / Continuous Delivery / Trunk-based / IDP）含む | スキル本体・他スキルからの参照元 |
| [industry-weights.ja.md](./industry-weights.ja.md) | 業界シグナル収集と重みづけ評価（★1〜★5）。Gartner / Tech Radar / DORA / カンファレンス / 採用事例の一次データ | 重みづけの根拠資料 |
| [overall-map.ja.md](./overall-map.ja.md) | **業界シグナル重みづけ版 全体マップ**。5層モデル + 問題領域 × 重み + 2024-2025 シフト + 関係グラフ + 更新シナリオ + アンチパターン | **フェーズ2 SKILL.md の一次参照** |
| [concept-map.ja.md](./concept-map.ja.md) | 旧版マップ：4文献起点・8問題領域 × 概念の処方系統樹 | 詳細解説リファレンスとして併存 |

## カバーする文献

### コア4文献

- **BVSSH** — *Sooner Safer Happier* (Smart et al., 2020)
- **Team Topologies** — *Team Topologies* (Skelton & Pais, 2019)
- **Evolutionary Architecture** — *Building Evolutionary Architectures* (Ford, Parsons, Kua, 2017/2023)
- **Four Keys / DORA** — *Accelerate* (Forsgren, Humble, Kim, 2018) + *State of DevOps Report* (年次)

### 周辺必須文献

- **Wardley Mapping** (Simon Wardley)
- **DDD 戦略パターン** — *Domain-Driven Design* (Evans, 2003), *Implementing DDD* (Vernon, 2013)
- **Sociotechnical Architecture** — Trist & Bamforth (1951) を起源とする系譜
- **Project to Product** (Kersten, 2018) — Flow Framework
- **SPACE Framework** (Forsgren et al., 2021)
- **Cynefin** (Snowden & Boone, 2007)
- **Theory of Constraints** (Goldratt, 1984)
- **The DevOps Handbook** (Kim et al., 2016)
- **Lean Software Development** (Poppendieck, 2003)
- **Fundamentals of Software Architecture** (Richards & Ford, 2020)

## 設計方針

1. **言語・クラウド非依存** — Kubernetes / AWS / GCP / 特定言語などの実装層に踏み込まない。
2. **原語併記** — 日本語の解説と英語の原語を必ずセットにする（一次文献に当たれる形を保つ）。
3. **出典明示** — 各用語に書籍 / 章 / 著者を併記する。
4. **問題領域起点** — 「概念を覚える」より「症状から処方を引ける」構成を優先する（concept-map.ja.md）。
5. **アンチパターン併記** — 「使い方を誤った例」を明示し、銀の弾丸化を防ぐ。

## フェーズ進行

- **フェーズ1a（完了）**: 用語集 + 概念マップ（文献起点）の整理。
- **フェーズ1b（完了）**: 業界シグナル収集 + 重みづけ + フラット全体マップ（業界起点）の構築。
- **フェーズ2（次回）**: 本 references を参照する `SKILL.md` を `../SKILL.md` として作成。`overall-map.ja.md` の §7 に方針記載済。
- **フェーズ3（任意）**: 各問題領域の診断テンプレート / ADR テンプレートを `templates/` 配下に追加。

## 重みづけ方針（要約）

`industry-weights.ja.md` の重み定義に従い、特定文献を構造的に上位扱いしない:

- **★★★★★** 業界の前提語彙（Conway's Law, Four Keys, Team Topologies, Bounded Context, Continuous Delivery, Platform Engineering）
- **★★★★☆** 強く成長中 / 標準化済（Architecture Modernization, Wardley Mapping, EventStorming, Fitness Function, DX Core 4, DevEx, VSM, ADR, Strangler Fig, Product Operating Model）
- **★★★☆☆** 安定的に普及（Cynefin / Westrum / BVSSH / SPACE / Flow Framework / Sociotechnical 等）
- **★★☆☆☆** 専門領域（Wardley Doctrine, Context Mapping, Subdomain Types, Postel's Law, Goodhart's Law 等）
- **★☆☆☆☆** 思想的源流（Tavistock, Lean/TPS, Theory of Constraints 原典 等）

調査日: **2026-05-16**。半年で陳腐化しうるため適宜更新する。

## 関連スキル

- `karak-architecture:adr-architect` — アーキテクチャ意思決定の記録
- `karak-architecture:write-c4-diagram` — C4 モデルによるアーキテクチャ可視化
- `karak-product:requirements-analyst` — 要件定義（Outcomes → Requirements）
- `karak-product:agile-project-manager` — クロスプラットフォーム開発のプロジェクト計画
