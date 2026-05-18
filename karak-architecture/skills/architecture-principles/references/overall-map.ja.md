# アーキテクチャ原則 全体マップ（業界シグナル重みづけ版）

特定の書籍を構造的に上位扱いせず、**2026-05-16 時点の業界シグナル** で重みづけしたフラットな全体マップ。
重みづけ根拠は [industry-weights.ja.md](./industry-weights.ja.md) 参照。

旧 [concept-map.ja.md](./concept-map.ja.md) を更新するのではなく、**観点を変えた別アングルのマップ** として併存させる。
旧マップは「4文献の役割分担」起点、本マップは「問題層 × 業界シグナル」起点。

---

## 0. 読み方

- 重み記号は industry-weights.ja.md と同じ ★1〜★5
- **★★★★★** = 議論の前提語彙、知らないと話が進まない
- **★★★★☆** = 提示すべき第一候補
- **★★★☆☆** = 文脈マッチ時の選択肢
- **★★☆☆☆** = 専門領域・要解説
- **★☆☆☆☆** = 思想的源流、ユーザが深掘りした時のみ

---

## 1. 5層モデル — 文献中立の全体構造

「どの本に書いてあったか」を横に置き、**問題の階層** で並べ直す。

```
┌─────────────────────────────────────────────────────────────┐
│ Layer 5: MEASURE — うまく回っているのか                      │
│   Four Keys, DX Core 4, DevEx, Flow Framework,               │
│   Westrum, SPACE, Rework Rate                                │
├─────────────────────────────────────────────────────────────┤
│ Layer 4: PRACTICE — 日々どう作るのか                         │
│   Continuous Delivery, Trunk-based Dev, Fitness Function,    │
│   Strangler Fig, ADR, Postel's Law, LRM, Architecture Quantum│
├─────────────────────────────────────────────────────────────┤
│ Layer 3: ORGANIZE — 誰がどう組むのか                         │
│   Team Topologies (4型 + 3モード), AMET, Cognitive Load,     │
│   Platform Engineering / IDP, Federated Governance,          │
│   Conway's Law / Inverse Conway                              │
├─────────────────────────────────────────────────────────────┤
│ Layer 2: MAP — どこに何があるのか                            │
│   Wardley Mapping, Bounded Context, EventStorming,           │
│   Context Mapping, Subdomain Types (Core/Supp/Generic),      │
│   Architecture Modernization (Tune の統合フレーム),          │
│   Sociotechnical Architecture, Cynefin                       │
├─────────────────────────────────────────────────────────────┤
│ Layer 1: WHY — 何のために変えるのか                          │
│   Outcomes over Outputs, Product Operating Model,            │
│   BVSSH, Three Horizons, North Star, VOICE,                  │
│   Servant Leadership, Goodhart's Law (警句)                  │
└─────────────────────────────────────────────────────────────┘
```

**注意**: 旧マップが BVSSH / Team Topologies / Evolutionary / Four Keys を **4本柱** として並列化していたが、業界シグナルから見ると不正確だった:
- Four Keys は Layer 5 の中核だが **Layer 4 を強制しない**
- Team Topologies は Layer 3 の中核だが **Layer 2 の前提が必要**
- BVSSH は Layer 1 の処方だが、業界の **共通語彙** ではない（コミュニティ規模は限定）
- Evolutionary Architecture は Layer 4 の実装思想で、**書籍自体は後続書で superseded** との評価

**つまり**: 4文献が同レベルで並んでいるのではなく、**異なる層を扱っている**。本マップではそれを明示する。

---

## 2. 問題領域 × 推奨概念（重みづけ版）

旧 concept-map.ja.md の8領域を維持しつつ、各推奨に重みを付与する。
**重み高 = 議論の前提として持つべき、重み低 = 必要に応じ提示**。

### 2.1 組織とアーキテクチャの整合

| 重み | 概念 | 役割 |
|---|---|---|
| ★★★★★ | Conway's Law | 現象認識の語彙 |
| ★★★★★ | Stream-aligned Team | 中核構造 |
| ★★★★★ | Bounded Context | 境界の言語 |
| ★★★★☆ | Inverse Conway Maneuver | 戦略アプローチ |
| ★★★★☆ | Platform Engineering / IDP | 全社的な下支え |
| ★★★☆☆ | Architecture Quantum | 量子境界の判定 |
| ★★★☆☆ | Fracture Plane | 分割面候補のリスト |
| ★★★☆☆ | Sociotechnical Architecture | 思想的前提 |

### 2.2 変化への耐性

| 重み | 概念 | 役割 |
|---|---|---|
| ★★★★★ | Continuous Delivery | 規範 |
| ★★★★☆ | Fitness Function | 自動検証 |
| ★★★★☆ | Architectural Decision Record | 決定の進化追跡 |
| ★★★★☆ | Trunk-based Development | 小バッチ前提 |
| ★★★☆☆ | Architectural Characteristic | 設計対象 |
| ★★☆☆☆ | Postel's Law | 契約進化 |
| ★★☆☆☆ | Last Responsible Moment | 意思決定遅延 |

### 2.3 価値とリスクの優先順位

| 重み | 概念 | 役割 |
|---|---|---|
| ★★★★☆ | Outcomes over Outputs | 議論の出発点 |
| ★★★★☆ | Product Operating Model | 経営層への語彙 |
| ★★★★☆ | Wardley Mapping | 投資位置の診断 |
| ★★★☆☆ | Three Horizons | 配分比率 |
| ★★★☆☆ | BVSSH | 抽象的指針セット |
| ★★☆☆☆ | VOICE | コミュニケーション形式 |
| ★★☆☆☆ | Pioneers/Settlers/Town Planners | 人材アサイン |

### 2.4 改善の計測

| 重み | 概念 | 役割 |
|---|---|---|
| ★★★★★ | Four Keys (+ Rework Rate) | 共通計測語彙 |
| ★★★★☆ | DX Core 4 | 経営層統合 |
| ★★★★☆ | DevEx Framework | 開発者主観計測 |
| ★★★★☆ | Value Stream Management | 価値の流れ |
| ★★★☆☆ | Flow Framework (Kersten) | 4種 Flow Item |
| ★★★☆☆ | Westrum Culture | 文化計測 |
| ★★★☆☆ | SPACE Framework | 学習リソースとして |
| ★★☆☆☆ | Goodhart's Law | 警句 |

### 2.5 段階的モダナイゼーション

| 重み | 概念 | 役割 |
|---|---|---|
| ★★★★☆ | Architecture Modernization (Tune) | 統合実装書 |
| ★★★★☆ | Strangler Fig Pattern | 移行戦略 |
| ★★★☆☆ | AMET | 推進体制 |
| ★★★☆☆ | Three Horizons | 投資配分 |
| ★★★☆☆ | Federated Governance | 統制設計 |
| ★★★☆☆ | Minimum Viable Compliance | 規制の軽量化 |

### 2.6 認知負荷の管理

| 重み | 概念 | 役割 |
|---|---|---|
| ★★★★★ | Platform Engineering / IDP | 外在負荷を削る |
| ★★★★☆ | Cognitive Load (3種) | 分解の言語 |
| ★★★★☆ | DevEx (Cognitive Load 軸) | 計測手段 |
| ★★★☆☆ | Thinnest Viable Platform | 過剰回避 |
| ★★★☆☆ | Team API | 境界明示 |
| ★★★☆☆ | X-as-a-Service | 相互作用モード |

### 2.7 境界の引き方

| 重み | 概念 | 役割 |
|---|---|---|
| ★★★★★ | Bounded Context | 言語境界 |
| ★★★★☆ | EventStorming | 発見手段 |
| ★★★☆☆ | Context Mapping (9パターン) | 関係性パターン |
| ★★★☆☆ | Subdomain Types (Core/Supp/Generic) | 投資判断 |
| ★★★☆☆ | Architecture Quantum | 同期境界 |
| ★★★☆☆ | Fracture Plane | 候補リスト |

### 2.8 文化と意思決定

| 重み | 概念 | 役割 |
|---|---|---|
| ★★★☆☆ | Westrum Culture | 計測モデル |
| ★★★☆☆ | Servant / Host Leadership | リーダーシップ言語 |
| ★★★☆☆ | Cynefin Framework | 状況分類 |
| ★★★☆☆ | Three Ways (DevOps) | 哲学的基盤 |
| ★★★☆☆ | Architectural Decision Record | 意思決定の記録 |
| ★★☆☆☆ | Theory of Constraints | 制約の理論 |

---

## 3. 2024-2025 業界シフトの読みかた

過去1年で **業界シグナルが大きく動いた** 6つのテーマ。スキル設計上、これらを優先的に反映する。

### Shift A: Platform Engineering の主流化 ↑↑

- Gartner 採用予測 55%(2025) → 80%(2026)
- Backstage が IDP 市場の 89% / CNCF コミット数 4位
- Team Topologies の **Platform Team / TVP** が抽象論から実装規律に
- スキル上の含意: 「Platform Team は実在するか / TVP の境界は妥当か」を診断項目に入れる

### Shift B: 指標フレームワークの統合 ↑↑

- 2023: DevEx 発表 (SPACE 進化形)
- 2024-12: DX Core 4 発表 (DORA + SPACE + DevEx 統合)
- DORA 2024: Rework Rate 追加、Time to Restore を Throughput 側に再分類
- スキル上の含意: 「Four Keys だけ」を推奨しない。**DX Core 4** を経営層向け、**DevEx** を開発者向けに使い分け

### Shift C: 統合実装書の登場 ↑↑

- Nick Tune *Architecture Modernization* (2024) が Wardley + Team Topologies + DDD + EventStorming を統合
- **AMET (Architecture Modernization Enabling Team)** が新語彙として流通
- スキル上の含意: 「個別概念の紹介」ではなく「束ねかた」を示すフローを SKILL.md に組み込む

### Shift D: Sociotechnical Architecture の主流化 ↑

- DDD 系（Yao, Hjorteland, da Silva）が NDC London / OOP / Explore DDD で連続登壇
- InfoQ が「Sociotechnical Design が Architectural Decisions を改善する」と 2025-09 に報道
- スキル上の含意: 「組織と技術を **同時に** 設計する」をデフォルトのスタンスに

### Shift E: Cynefin の Aporetic 改名 (2024)

- Snowden 自身が「Chaotic という語の使用に過信があった」と公表
- 中央領域を **Aporetic / Confused** に改名
- スキル上の含意: 古い Cynefin 図を参照している資料は更新が必要

### Shift F: Team Topologies 2nd Edition (2025-08)

- 5年間の現場事例（Adidas, EBSCO, KFC, Creditas, Singapore GovTech 等）を反映
- Humane / Sociotechnical 観点の強化
- スキル上の含意: Team Topologies を引用する際は 2nd Edition を一次資料に

---

## 4. 概念の関係グラフ

「どの概念がどの概念を **補強・派生・対立** するか」のフラットな関係。

### 4.1 補強関係（A があると B が効く）

```
Bounded Context ←─→ Team Topologies (Stream-aligned)
       │                    │
       ▼                    ▼
EventStorming         Cognitive Load
       │                    │
       ▼                    ▼
Architecture       Platform Engineering
Modernization      / IDP / TVP
       │
       ├─→ Wardley Mapping
       │
       └─→ AMET

Continuous Delivery ←─→ Trunk-based Dev
       │
       ├─→ Fitness Function
       ├─→ Four Keys (測れる)
       └─→ DX Core 4

Outcomes over Outputs ←─→ Product Operating Model
       │                         │
       ▼                         ▼
North Star / OKR          Flow Framework / VSM
```

### 4.2 派生関係（後続が前を更新）

```
SPACE (2021) ──→ DevEx (2023) ──→ DX Core 4 (2024-12)

Tavistock 1951 ──→ Sociotechnical Architecture (2020s)

Conway 1968 ──→ Inverse Conway ──→ Team Topologies (2019/2025)

Lean / TPS ──→ DevOps Three Ways ──→ DORA Capabilities

Cynefin (旧 Disorder) ──→ Cynefin (新 Aporetic, 2024)

Four Keys (4指標) ──→ Four Keys + Rework Rate (5指標, 2024)
```

### 4.3 対立 / トレードオフ

| 対立軸 | 一方 | 他方 |
|---|---|---|
| 統制 vs 自律 | 中央集権ガバナンス | Federated Governance |
| 計測の意図 | DORA (プロセス計測) | DevEx (主観計測) |
| 移行戦略 | ビッグバン置換 | Strangler Fig |
| プラットフォーム | Thinnest Viable | "全部抱える" Platform |
| 相互作用 | 永続 Collaboration | X-as-a-Service |
| 指標数 | 単一指標 (Goodhart 化) | 多次元 (SPACE / DX Core 4) |
| 状況対応 | Best Practice 万能 | Cynefin 領域別 |

### 4.4 「使う層」と「源流」

業界で **直接適用** されるのは Layer 2〜5。Layer 1 の Why は通常、Layer 2〜5 を通して間接的に効く。

- **直接適用**: Team Topologies, Four Keys, Continuous Delivery, Bounded Context, Strangler Fig, Platform Engineering, DX Core 4, Architecture Modernization
- **間接適用 / 思想源流**: Conway's Law, Tavistock, Lean/TPS, Theory of Constraints, Westrum 原典, BVSSH (北米のコミュニティ外)

---

## 5. 統合シナリオ（更新版）

業界シグナルを反映した処方の流れ。

### シナリオA: 「マイクロサービス化が進んだが速度が出ない」

```
[診断]
  1. Four Keys 計測 (Lead Time / Deploy Freq の悪化)
  2. Rework Rate を追加計測 (2024 追加)
  3. DevEx の Cognitive Load 軸でアンケート
       → Stream-aligned Team が抱えるサービス数を確認

[処方]
  4. Platform Engineering / TVP の整備状況を確認
       → 不在なら Platform Team を立ち上げる (Backstage 採用を含む)
  5. Architecture Quantum 境界の検査
       → 同期チェーンが3段超なら境界が誤っている
  6. EventStorming で Bounded Context を再発見
  7. AMET を立ち上げて時限的に推進

[計測]
  8. DX Core 4 で経営層に説明
  9. 半年後に Four Keys + Rework Rate を再計測
```

### シナリオB: 「変革プロジェクトが頓挫した」

```
[診断]
  1. BVSSH の Outcomes over Outputs で「成果は何だった」を再確認
  2. Westrum 文化スコアを観察
       → Pathological 下では構造変更だけでは効かない
  3. Cynefin で課題領域を分類
       → Complex を Best Practice で扱おうとしていないか

[処方]
  4. Three Horizons で投資配分を再設計
       → H1 (現行) の指標で H3 (探索) を評価していないか
  5. Federated Governance + MVC で統制を軽量化
  6. Architecture Modernization (Tune) フローで再起動
       → Wardley → EventStorming → Team Topologies → AMET

[新しい問い]
  7. Sociotechnical Architecture の視点で
       「組織だけ・技術だけ」になっていないか確認
```

### シナリオC: 「Four Keys は良くなったが事業成果が上がらない」

```
[診断]
  1. Goodhart's Law を疑う
       → Deploy Frequency が「no-op deploy」で水増しされていないか
  2. Rework Rate (2024追加) を確認
       → 速いが手戻りが多い状態でないか
  3. Flow Framework の Flow Distribution を見る
       → Feature 100% で Tech Debt 0% でないか

[処方]
  4. DX Core 4 の Business Impact 軸を導入
       → 機能採用率・Revenue per Engineer を計測
  5. Outcomes over Outputs に立ち返り、North Star を再定義
  6. Product Operating Model への移行度合いを確認
       → プロジェクト型残存が事業接続を阻害
```

### シナリオD（新規）: 「AI コード生成導入後、配信性能が悪化した」

```
[診断]
  1. DORA 2025 AI-Assisted Software Development Report を参照
       → 「AI 採用と配信性能の負の相関」が複数組織で実証されている
  2. DevEx の Cognitive Load 軸を計測
       → AI 生成コードのレビュー負荷が増えていないか
  3. Fitness Function の検証で AI 生成コードの品質を検査
       → Tech Radar 2025 が「AI でフィットネス関数を生成する」を Trial 入り

[処方]
  4. Trunk-based Dev + 自動化 Fitness Function を強化
       → AI 生成コードを「素早く、自動で」検証する
  5. Platform Engineering の Paved Road で AI 生成テンプレートを標準化
  6. Code Review プロセスの軽量化（DORA 公式指摘）
```

---

## 6. アンチパターン早見表（業界シグナル根拠版）

旧マップの10件を、業界が実証しているもの中心に再整理。

| アンチパターン | 症状 | 立ち返るべき概念 | 業界根拠 |
|---|---|---|---|
| メトリクス天国 | ダッシュボードが意思決定に使われない | Goodhart's Law / DX Core 4 | SPACE→DX Core 4 進化の動機 |
| プラットフォーム肥大 | Platform Team が「全部抱え」内部顧客が逃げる | TVP / Platform as Product | Gartner Hype Cycle 警告 |
| 分散モノリス | 独立デプロイ不能 | Architecture Quantum / Fracture Plane | *Software Architecture: The Hard Parts* 中心テーマ |
| ビッグバン変革 | 全社一斉切り替えで頓挫 | Strangler Fig / Three Horizons | Planview 2024: 97% が阻害要因 |
| 中央集権統制 | 統制で速度が出ない | Federated Governance / MVC | DORA "重い code review が TBD を阻害" |
| Pioneer に SLA | 探索チームに運用指標を課す | PST 別指標 / Three Horizons | Wardley 主張 |
| Manual Fitness | アーキレビューが人手依存 | Automated Fitness Function | Tech Radar 2025 Trial |
| ADR 不在 | 過去の決定の根拠が失われ再議論 | ADR | Tech Radar Adopt 継続 |
| Best Practice 万能視 | Complex 領域に Best Practice | Cynefin 領域別 | Snowden 2024 改訂 |
| **AI Solutionism**（新規） | AI 導入で配信性能・品質が改善するという期待 | DORA 2025 / Fitness Function | DORA 2025 AI レポート |
| **プロジェクト型残存**（新規） | プロダクト宣言だがプロジェクト管理が残る | Product Operating Model | Planview P2P: 残る課題 1位 |
| **Four Keys 単独運用**（新規） | プロセス計測のみで体験・事業を見ない | DX Core 4 (4軸統合) | DX Core 4 (2024-12) |

---

## 7. このマップから SKILL.md へ（フェーズ2方針）

### 7.1 SKILL.md のトリガー条件案

★★★★★ 概念のキーワードを最優先で trigger に含める:
- Conway's Law / Inverse Conway / 逆コンウェイ
- Team Topologies / チームトポロジー / Stream-aligned
- Four Keys / DORA / Lead Time
- Bounded Context / DDD 戦略
- Continuous Delivery / Trunk-based
- Platform Engineering / IDP

★★★★☆ も含める:
- Architecture Modernization
- Fitness Function
- Wardley Mapping
- DX Core 4 / DevEx
- VSM / Value Stream
- AMET
- EventStorming

### 7.2 診断フロー案（5層モデルベース）

```
ユーザの相談を受ける
    │
    ▼
1. どの Layer の問題か特定 (1=Why, 2=Map, 3=Org, 4=Practice, 5=Measure)
    │
    ▼
2. 該当 Layer の ★★★★★/★★★★☆ 概念から候補を3〜5提示
    │
    ▼
3. 隣接 Layer の前提が満たされているか確認
    (Layer 3 を扱う前に Layer 2 の Bounded Context が引かれているか等)
    │
    ▼
4. 2024-2025 シフトを反映した最新代替を提示
    (SPACE → DX Core 4, 旧 Cynefin → Aporetic 改訂版)
    │
    ▼
5. ADR テンプレートで意思決定を記録
    (karak-architecture:adr-architect スキル連携)
```

### 7.3 隣接スキル連携

- `karak-architecture:adr-architect` — 意思決定の記録 (Layer 4 で常時呼び出し)
- `karak-architecture:write-c4-diagram` — Layer 2/3 の可視化
- `karak-product:requirements-analyst` — Layer 1 の Outcome 定義
- `karak-product:agile-project-manager` — Layer 1 → 5 の進捗計画

### 7.4 言語・クラウド非依存の維持

具体的なツール名（Kubernetes / AWS / Datadog / Backstage 等）は SKILL.md 本体に書かない。
ただし、Platform Engineering の項目では「Backstage が IDP 市場 89%」など **業界シグナルの参照** として最小限言及してよい（特定推奨ではなく、現状把握として）。

---

## 8. 旧 concept-map.ja.md との関係

| 観点 | 旧 concept-map.ja.md | 本 overall-map.ja.md |
|---|---|---|
| 出発点 | 4文献の役割分担 | 業界シグナル重みづけ |
| 構造 | 8 問題領域 × 概念 | 5 層 + 8 問題領域 + 重み |
| 文献扱い | 4文献 + 周辺 | フラット |
| 推奨の根拠 | 文献内の主張 | 業界採用率 / Tech Radar / Gartner |
| 含む2024-2025更新 | なし | DX Core 4 / Rework Rate / Aporetic / Tune本 / TT 2nd Ed |

旧マップは「文献の地形図」として、本マップは「業界の現在地」として **併存** する。
フェーズ2の SKILL.md は本マップを一次参照にし、旧マップは詳細解説のリファレンスとして残す。
