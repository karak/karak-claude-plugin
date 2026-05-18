# 業界シグナル & 重みづけ評価

`architecture-principles` スキルが扱う概念群について、**業界での実証された存在感** を基準にフラットに重みづけする。
特定文献を構造的に上位扱いせず、現在のシグナルで序列を判断する。

調査日: **2026-05-16** （調査時点。指標は半年で陳腐化しうるので適宜更新する）。

---

## 0. 重み定義

| 重み | 記号 | 意味 | 判定基準 |
|---|---|---|---|
| Critical | ★★★★★ | 業界の共通語彙。知らないと議論が成立しない | Gartner / CNCF / DORA に確固たる地位 + 50%超の採用率 + 過去1年で重要なアップデート |
| Strong | ★★★★☆ | 強く成長中 or 標準化済み。実務に直接効く | ThoughtWorks Radar の Adopt/Trial、複数の Big-Tech 採用、過去2年で活発な書籍・カンファレンス活動 |
| Established | ★★★☆☆ | 安定的に普及。新規性はないが廃れていない | 業界に定着、教科書化されている、依然として実装される |
| Specialized | ★★☆☆☆ | 特定コミュニティで強い。汎用ではない | DDD / Sociotechnical 系のニッチで深い、一般エンジニアには浸透していない |
| Background | ★☆☆☆☆ | 思想的源流。直接適用は稀だが理解は重要 | 起源・理論的基盤として参照される、現代の実装は別概念で行われる |

---

## 1. 主要な業界シグナル（一次データ）

### 1.1 Gartner / 業界調査

| シグナル | 数値 | 出典 |
|---|---|---|
| Platform Engineering 採用率 (2025) | **55%**, 2026予測 **80%** | Gartner Hype Cycle for Platform Engineering 2025 |
| Backstage の IDP 市場シェア | **89%** | Roadie / Platform Engineering 2026 ([roadie.io](https://roadie.io/blog/platform-engineering-in-2026-why-diy-is-dead/)) |
| Backstage の CNCF コミット数ランク (2024) | 4位 (Kubernetes / OpenTelemetry / Argo 次) | CNCF / Platform Engineering blog |
| マイクロサービス採用率 (2024) | **85%** | Solo.io 2024 Survey |
| 価値ストリーム配信プラットフォーム移行 (2024) | 60% (2021: 20%) | Gartner VSM Market Guide |
| Product Operating Model 移行 | 過半が「5年で 80%」 | Planview 2024 P2P State of the Industry |
| Architecture Modernization 課題報告 | 97% が少なくとも1つの阻害要因 | Planview 2024 P2P |

### 1.2 ThoughtWorks Technology Radar (Vol.32 Apr 2025 / Vol.33 Nov 2025)

| 概念 | リング | 補足 |
|---|---|---|
| Team Topologies | Adopt | Accelerate のメトリクスとセットで参照 |
| Wardley Mapping | Trial | 価値連鎖と進化軸の可視化 |
| Fitness Functions | Trial (AIで補強テーマ) | AI でフィットネス関数を生成する技法が言及 |
| Architectural decision records | Adopt (継続) | — |
| Platform engineering teams | Adopt | — |
| EventStorming | Trial | — |

Vol.33 (Nov 2025) 主要テーマ: **AI が全テーマを統合**（AI 向けインフラ自動化、MCP、AI コーディングワークフロー、AI アンチパターン）。

### 1.3 DORA / Accelerate State of DevOps Report 2024

| 変更 | 内容 |
|---|---|
| 新指標 | **Rework Rate** 追加（ユーザ向けバグへの計画外デプロイの割合） |
| 再分類 | Time to Restore → Throughput 側に再考。Rework Rate は Stability 側 |
| 既存 | Deployment Frequency / Lead Time / Change Failure Rate / Reliability (2021〜) |
| 2025年テーマ | **AI-Assisted Software Development State** に独立レポートを発行。AI 採用が必ずしも配信性能を改善しないことを実証 |

### 1.4 新フレームワーク (2024-2025発表)

| フレームワーク | 著者 | 発表 | 位置づけ |
|---|---|---|---|
| **DevEx** | Noda, Storey, Forsgren, Greiler | 2023 | SPACE の進化形。Feedback Loops / Cognitive Load / Flow State の3軸 |
| **DX Core 4** | Noda, Tacho (DX社) | **2024-12** | DORA + SPACE + DevEx を統合した経営層向け処方フレームワーク |
| **Architecture Modernization (book)** | Nick Tune | 2024 | Wardley + Team Topologies + DDD + EventStorming の **統合実装書**。AMET を提唱 |
| **Team Topologies 2nd Edition** | Skelton, Pais | **2025-08** | 5年の現場事例を反映、Sociotechnical/Humane 強化 |

### 1.5 カンファレンス出現（2024-2025）

| 概念 | 主要登壇 |
|---|---|
| Sociotechnical Architecture | NDC London 2025 (Hjorteland), Explore DDD 2024 (Yao), OOP, GOTO |
| Architecture Modernization | GOTO Book Club 2024, GOTO Conferences 2024-2025 |
| Wardley Mapping | DevOps Enterprise Summit, GOTO Copenhagen, QCon |
| Team Topologies | Adidas, EBSCO, KFC UK&I, Creditas, Singapore GovTech 等の **公開事例** |
| Platform Engineering | PlatformCon (年次拡大) |

### 1.6 公開エンタープライズ採用事例

| 事例 | 効果 | 主要概念 |
|---|---|---|
| EBSCO Information Services (Conflux 支援) | **SAFe 7 年運用後の再編**。18 ヶ月で feature cycle time -26%、依存ブロッカー -45%、P1/P2 障害 -76%（2 年）、$9.1M 年間コスト削減、62% ROI。2 フェーズ: **Domain Definition → Flow Optimization**。"ownership → stewardship" マインドシフト | Team Topologies / Stream-aligned |
| KFC UK&I | チャネル別 (mobile/web/kiosk) → 価値ストリーム別 (Acquisition&Retention / Basket&Checkout / Payment&Fulfillment) 再編。アプリ売上 15 倍、サイクルタイム -33% | Team Topologies / 価値ストリーム再編 |
| Adidas | プラットフォーム内製化。デプロイ **4-6 週間 → 1 日 3-4 回**、4,000 pods / 200 nodes / 80,000 builds/月、クリティカル系の 40% を CloudNative プラットフォームへ | Team Topologies + Platform Engineering |
| **Amazon Prime Video Monitoring (反例)** | **マイクロサービス → モノリス回帰**。AWS Step Functions + S3 のオーケストレーション過剰がコストを押し上げ、ECS への統合と in-process aggregation で **インフラコスト -90%**。「将来スケールに備えた早期分散」の典型失敗 | Architecture Quantum / 分散モノリス回避 |
| Creditas | 認知負荷ベース再編 | Team Topologies / Cognitive Load |
| Singapore GovTech | 政府プラットフォーム | Platform as Government |
| Saven Tech (DDD) | 統合欠陥 -35%, 保守 -25% | DDD 戦略パターン |

---

## 2. 重みづけテーブル（フラット）

**4文献を特別扱いせず、業界シグナルの実数で重みづけ** する。

| Rank | 概念 | 重み | 出典系統 | 業界シグナル要約 | トレンド |
|---|---|---|---|---|---|
| 1 | **Platform Engineering / IDP** | ★★★★★ | Team Topologies / CNCF / Gartner | 採用 55%→80%予測、Backstage 89% シェア | ↑↑ 急騰 |
| 2 | **Four Keys (DORA Metrics)** | ★★★★★ | Accelerate | 業界の共通計測語彙、Rework Rate 追加 (2024) | → 安定・進化中 |
| 3 | **Team Topologies (4型 + 3モード)** | ★★★★★ | Team Topologies | Tech Radar Adopt、2nd Edition (2025)、複数 Big-Tech 事例 | ↑ 拡張中 |
| 4 | **Bounded Context (DDD 戦略)** | ★★★★★ | DDD | マイクロサービス 85% 採用の前提語彙 | → 普及済み |
| 5 | **Continuous Delivery / Trunk-based Dev** | ★★★★★ | Accelerate / Humble & Farley | DORA Capabilities 中核、依然「rare even in 2025」と報告 | → 規範として確立 |
| 6 | **Conway's Law / Inverse Conway** | ★★★★★ | Conway 1968 + Team Topologies | 組織設計議論の常識語彙 | → 安定 |
| 7 | **Strangler Fig Pattern** | ★★★★☆ | Fowler 2004 | AWS / Azure / GCP すべて公式ドキュメントで採用 | → 標準化済 |
| 8 | **Architecture Modernization (Tune)** | ★★★★☆ | Tune (2024) — 統合フレームワーク | 2024刊行直後で熱量高、GOTO で繰り返し登壇 | ↑↑ 急騰中 |
| 9 | **EventStorming** | ★★★★☆ | Brandolini | DDD と並走、Tech Radar Trial、実務ワークショップ標準 | ↑ 拡大中 |
| 10 | **Wardley Mapping** | ★★★★☆ | Wardley | Tech Radar Trial、Architecture Modernization の柱の1つ | ↑ 拡大中 |
| 11 | **Value Stream Management (VSM)** | ★★★★☆ | Flow Framework / Lean | 60% 採用予測、Gartner Market Guide あり | ↑ 拡大中 |
| 12 | **Fitness Functions** | ★★★★☆ | Ford / Parsons / Kua | Tech Radar Trial、AI 連携テーマで再注目 | ↑ AI で再加速 |
| 13 | **DX Core 4** | ★★★★☆ | Noda / Tacho 2024-12 | DORA+SPACE+DevEx の経営層統合、12月発表で2025展開中 | ↑↑ 急騰中 |
| 14 | **DevEx Framework** | ★★★★☆ | Noda / Storey / Forsgren / Greiler | SPACE 後継、3軸シンプル化 | ↑ 拡大中 |
| 15 | **Product Operating Model** | ★★★★☆ | Kersten / Planview | P2P 文脈で経営語彙化、Marty Cagan 系統と合流 | ↑ 拡大中 |
| 16 | **Architectural Decision Record (ADR)** | ★★★★☆ | Nygard 2011 | Tech Radar Adopt 継続、デファクト | → 確立 |
| 17 | **Architecture Quantum** | ★★★☆☆ | Ford / Richards | *Hard Parts* 経由で普及。マイクロサービス境界判定の道具 | → 安定 |
| 18 | **Cognitive Load (Sweller応用)** | ★★★☆☆ | Team Topologies | 公開事例で繰り返し言及（Creditas等） | → 安定 |
| 19 | **Outcomes over Outputs** | ★★★☆☆ | BVSSH / Marty Cagan | 経営語彙として広く流通 | → 普及済 |
| 20 | **Westrum Culture** | ★★★☆☆ | Westrum 2004 / Accelerate | 文化計測のデファクト | → 安定 |
| 21 | **SPACE Framework** | ★★★☆☆ | Forsgren et al. 2021 | DevEx / DX Core 4 に進化中、原型は学習リソースとして残る | ↓ DevEx に移行 |
| 22 | **Sociotechnical Architecture** | ★★★☆☆ | Trist & Bamforth 1951 / da Silva / Hjorteland / Yao | DDD 系コミュニティで熱量高、汎用浸透はこれから | ↑ 拡大中 |
| 23 | **Flow Framework (Kersten 5指標)** | ★★★☆☆ | Kersten 2018 | Planview の中核、VSM と合流 | → 安定 |
| 24 | **AMET (Architecture Modernization Enabling Team)** | ★★★☆☆ | Tune 2024 | 新概念、Enabling Team の特化版として2024-2025で流通開始 | ↑↑ 急騰中 |
| 25 | **Cynefin Framework** | ★★★☆☆ | Snowden | 中央領域を Aporetic に改名 (2024)、AI 文脈で再注目 | → 安定〜微増 |
| 26 | **Context Mapping (9パターン)** | ★★★☆☆ | Evans 2003 | DDD 普及層では基礎、汎用エンジニアには浸透薄 | → 安定 |
| 27 | **Three Ways (DevOps)** | ★★★☆☆ | Kim et al. | DevOps Handbook 経由で確立 | → 安定 |
| 28 | **Theory of Constraints** | ★★★☆☆ | Goldratt 1984 | DevOps 思想の理論的源流、直接適用は減少 | → 緩やかに古典化 |
| 29 | **BVSSH (Sooner Safer Happier)** | ★★★☆☆ | Smart et al. 2020 | 米州 Meetup・コミュニティあり、企業導入は限定的 | → ニッチで活発 |
| 30 | **Wardley Doctrine / Climate** | ★★☆☆☆ | Wardley | Wardley Mapping の上級プラクティス、適用組織は少数 | → 専門化 |
| 31 | **Pioneers, Settlers, Town Planners** | ★★☆☆☆ | Wardley | 概念は流通、組織制度化は稀 | → 緩やか |
| 32 | **Last Responsible Moment** | ★★☆☆☆ | Poppendieck | Lean 系で確立、直接話題に上る頻度は中 | → 安定 |
| 33 | **Subdomain Types (Core/Supporting/Generic)** | ★★☆☆☆ | Evans 2003 | DDD 戦略の定番だが、ビジネス側まで届いていない | → 専門化 |
| 34 | **Postel's Law (契約進化)** | ★★☆☆☆ | RFC 793 | API設計で時折、原則として参照 | → 安定 |
| 35 | **Goodhart's Law** | ★★☆☆☆ | Goodhart 1975 / Strathern 1997 | 指標導入時の警告として頻繁に引用 | → 警句として安定 |
| 36 | **Mission Command / VOICE** | ★★☆☆☆ | BVSSH / 軍事用語 | BVSSH 文脈での流通、外では稀 | → 専門化 |
| 37 | **Servant / Host Leadership** | ★★☆☆☆ | Greenleaf 1970 / McKergow | リーダーシップ語彙として一般化、直接の参照頻度は中 | → 安定 |
| 38 | **Three Horizons (McKinsey起源)** | ★★☆☆☆ | Baghai/Coley/White 1999 | BVSSH と Wardley で再活用、原型は経営戦略 | → 中庸 |
| 39 | **Lean / TPS / Pull System** | ★☆☆☆☆ | Ohno / Toyota | DevOps の理論的源流、直接適用は Lean Software 経由 | → 古典 |
| 40 | **Tavistock Sociotechnical (1951)** | ★☆☆☆☆ | Trist & Bamforth | Sociotechnical Architecture の起源、現代直接参照は稀 | → 思想的源流 |
| 41 | **Westrum 文化原典 (2004)** | ★☆☆☆☆ | Westrum | Accelerate 経由で流通、原典直読は稀 | → 思想的源流 |

---

## 3. トレンド・デルタ（過去1年で動いたもの）

### 3.1 急騰 ↑↑

- **Platform Engineering / IDP** — Gartner が「過熱期」と評価
- **Architecture Modernization (Tune の本)** — 2024刊行で AMET と統合パターンが急流通
- **DX Core 4** — 2024-12 発表、2025-2026 で経営層採用拡大予測
- **AI × Fitness Functions** — Tech Radar 2025 が AI 統合テーマで再強調

### 3.2 拡大 ↑

- **Team Topologies** — 2nd Edition (2025-08) でさらに浸透
- **Wardley Mapping** — Tune の本で他概念と統合され実務に届く
- **VSM** — Planview 等のツール市場拡大
- **DevEx** — SPACE から実用フレームワークへ進化
- **Sociotechnical Architecture** — DDD コミュニティでの熱量増

### 3.3 進化 / 再分類 →

- **DORA Four Keys** — 第5指標 Rework Rate 追加、AI 影響を独立レポート化
- **Cynefin** — 中央領域を Aporetic/Confused に改名 (2024)
- **SPACE** — DevEx / DX Core 4 に移行中（原型は学習用に残存）

### 3.4 古典化 ↓

- **Theory of Constraints** — 直接参照は減、思想的源流として残存
- **BVSSH** — コミュニティはアクティブだが、Team Topologies ほど一般化せず
- **Evolutionary Architecture 原著** — 「2025には後続書で superseded」とのレビュー。**概念自体は健在**、書籍は更新が必要なフェーズ

---

## 4. 重みづけの含意（スキル設計上のガイド）

このスキルが Stream-aligned Team / アーキテクト / 技術リードを支援するとき:

1. **★★★★★ は前提として扱う** — 議論のスタート地点。説明は最小化、参照だけで通じる前提。
2. **★★★★☆ は能動的に提示する** — ユーザの状況に応じて提示する第一候補。
3. **★★★☆☆ は文脈マッチで提示する** — 該当する問題領域でのみ提示。
4. **★★☆☆☆ は説明付きで提示する** — ユーザに既知でない可能性が高く、要約と出典を併記。
5. **★☆☆☆☆ は深掘り時のみ** — 思想的源流として、ユーザが「なぜそうなっているか」を問うた場合に限る。

---

## 5. 出典（主要なもの）

- [ThoughtWorks Technology Radar Vol.33 (Nov 2025)](https://www.thoughtworks.com/content/dam/thoughtworks/documents/radar/2025/11/tr_technology_radar_vol_33_en.pdf)
- [ThoughtWorks Technology Radar Vol.32 (Apr 2025)](https://www.thoughtworks.com/content/dam/thoughtworks/documents/radar/2025/04/tr_technology_radar_vol_32_en.pdf)
- [DORA Accelerate State of DevOps Report 2024](https://dora.dev/research/2024/dora-report/)
- [2025 DORA State of AI-Assisted Software Development](https://cloud.google.com/resources/content/2025-dora-ai-assisted-software-development-report)
- [Gartner Hype Cycle for Platform Engineering 2025](https://www.gartner.com/en/documents/6586902)
- [Team Topologies — 2nd Edition Announcement (Aug 2025)](https://teamtopologies.com/news-blogs-newsletters/2025/8/27/beyond-the-machine-team-topologies-second-edition-and-the-future-of-humane-high-performing-organizations)
- [Team Topologies — 5 Years of Transforming Organizations (IT Revolution)](https://itrevolution.com/articles/team-topologies-five-years-of-transforming-organizations/)
- [Architecture Modernization (Nick Tune) — Goodreads](https://www.goodreads.com/book/show/123260251-architecture-modernization---socio-technical-alignment-of-software-stra)
- [Introducing the DX Core 4 (Abi Noda, Dec 2024)](https://newsletter.getdx.com/p/introducing-the-dx-core-4)
- [DevEx Metrics Framework (InfoQ)](https://www.infoq.com/articles/devex-metrics-framework/)
- [How Sociotechnical Design Can Improve Architectural Decisions (InfoQ Sep 2025)](https://www.infoq.com/news/2025/09/sociotechnical-design/)
- [Platform Engineering in 2026 (Roadie)](https://roadie.io/blog/platform-engineering-in-2026-why-diy-is-dead/)
- [Planview 2024 P2P State of the Industry](https://newsroom.planview.com/new-planview-research-confirms-product-operating-model-drives-better-business-performance/)
- [DDD Systematic Literature Review (ScienceDirect 2025)](https://www.sciencedirect.com/science/article/pii/S0164121225002055)
- [DDD in 2025 (Saven Tech)](https://saventech.com/domain-driven-design-ddd-in-2025/)
- [BVSSH Principles (IT Revolution)](https://itrevolution.com/articles/bvssh-principles/)
- [Cynefin Framework (Wikipedia)](https://en.wikipedia.org/wiki/Cynefin_framework)
- [Strangler Fig Pattern — Azure Architecture Center](https://learn.microsoft.com/en-us/azure/architecture/patterns/strangler-fig)
- [Strangler Fig Pattern — AWS Prescriptive Guidance](https://docs.aws.amazon.com/prescriptive-guidance/latest/cloud-design-patterns/strangler-fig.html)
- [Octopus Deploy — DORA Metrics 2024/25](https://octopus.com/devops/metrics/dora-metrics/)
- [getDX — 2024 DORA Report Highlights](https://getdx.com/blog/2024-dora-report/)
- [Wardley Mapping — ThoughtWorks Tech Radar entry](https://www.thoughtworks.com/radar/techniques/wardley-mapping)
