# アーキテクチャ原則 用語集

事業価値・組織運営とソフトウェアアーキテクチャを接続する「言語非依存・クラウド非依存」の原則と用語集。
言語は日本語、用語は **原語併記**（一次文献に当たれる形を維持）。

## 凡例

各エントリは下記の形式で記述する。

```
### 用語 (Original Term)

**一行定義** — 30〜60字で要点を一文に。

**詳細** — 文脈、構成要素、ニュアンス。

**関連** — [[同ファイル内の他用語]] / 他文献。

**出典** — 書名・著者・章節。
```

---

## 1. アーキテクチャ・モダナイゼーション / BVSSH

> **Better Value Sooner Safer Happier** — Jonathan Smart, Zsolt Berend, Myles Ogilvie, Simon Rohrer (IT Revolution, 2020).
> 大組織のアジャイル変革で得た「アンチパターンとパターン」のカタログ。

### BVSSH (Better Value Sooner Safer Happier)

**一行定義** — 組織変革の成果を測る4つの北極星。「より良いもの (Better Value) を、より早く (Sooner)、より安全に (Safer)、より幸せに (Happier)」。

**詳細** — アウトプット（出荷数・ベロシティ）ではなく **アウトカム** に焦点を当てるためのフレーズ。Better/Value/Sooner/Safer/Happier は順序に意味があり、Safer を犠牲にした Sooner や Happier を犠牲にした Value は持続しない。

**関連** — [[Outcomes over Outputs]], [[Minimum Viable Compliance]], [[VOICE]]。

**出典** — Smart et al., *Sooner Safer Happier*, Preface & Ch.1。

### Outcomes over Outputs

**一行定義** — 「何を出したか」ではなく「何が変わったか」で進捗を測る原則。

**詳細** — アウトプット（機能リリース数、ストーリーポイント）は容易に測れるがビジネス効果と弱く相関する。アウトカム（NPS、顧客解約率、サイクルタイム）は測りにくいが事業価値と直結する。BVSSH は OKR の Key Result をアウトカムで書くことを推奨する。

**関連** — [[BVSSH]], [[North Star Metric]], [[Flow Framework]]。

**出典** — Smart et al., Ch.3 *Outcomes over Outputs*。

### Minimum Viable Compliance (MVC)

**一行定義** — 規制・統制を「最小限で十分な形」に再設計し、デリバリ速度を阻害しないようにする実践。

**詳細** — 大企業の変革を阻む典型は「全社統一・全プロセス重武装」のコンプライアンス。MVC は法令・規制の **本質要件** だけを残し、残りを Federated Governance（連邦型ガバナンス）でチームに委ねる。Three Lines of Defense の運用設計とセット。

**関連** — [[Federated Governance]], [[Long-lived Value Streams]]。

**出典** — Smart et al., Ch.13。

### Federated Governance

**一行定義** — 中央が「方針」を、各チームが「実装」を持つ連邦型の意思決定モデル。

**詳細** — 中央集権型は遅く、完全分散型は不整合を生む。Federated は「**何を**守るか（policy）」を中央が、「**どう**守るか（implementation）」を現場が決める。Platform Engineering の Paved Road（敷石）と相性がよい。

**関連** — [[Minimum Viable Compliance]], [[Paved Road]], [[Thinnest Viable Platform]]。

**出典** — Smart et al., Ch.13。

### Long-lived Value Streams

**一行定義** — プロジェクト単位ではなく、顧客価値の流れに沿った **長寿命** の組織単位。

**詳細** — プロジェクト型は「立ち上げ→解散」を繰り返し、暗黙知の蒸発・引き継ぎコスト・学習の断絶を招く。Long-lived Value Stream は同じ顧客セグメントに対し継続して責任を持つ「事業単位」として組織を編成する。Team Topologies の Stream-aligned Team と一致する概念。

**関連** — [[Stream-aligned Team]], [[Project to Product]]。

**出典** — Smart et al., Ch.7。

### VOICE (Vision, Outcomes, Intent, Context, Experiments)

**一行定義** — 変革のリーダーシップが繰り返し伝えるべき5要素のフレームワーク。

**詳細** — Vision（あるべき姿）→ Outcomes（測定可能な成果）→ Intent（指揮官の意図）→ Context（背景・制約）→ Experiments（仮説検証）。Mission Command（任務指揮）型のリーダーシップ言語。

**関連** — [[Outcomes over Outputs]], [[Servant Leadership]], [[Mission Command]]。

**出典** — Smart et al., Ch.4。

### Three Horizons (BVSSH文脈)

**一行定義** — 現行事業 (H1)・拡張事業 (H2)・未来事業 (H3) を同時に経営する考え方を、組織変革の段階モデルに転用したもの。

**詳細** — McKinsey の Three Horizons of Growth を組織進化に適用。H1 = 既存価値ストリームの最適化、H2 = 隣接領域の拡張、H3 = 破壊的探索。各 Horizon に **異なるリスク受容度・成功指標・組織構造** を割り当てる。

**関連** — [[Pioneers, Settlers, Town Planners]], [[Wardley Mapping]]。

**出典** — Smart et al., Ch.6。McKinsey *The Alchemy of Growth*。

### Pull System / WIP Limits

**一行定義** — 仕掛り (Work In Progress) の上限を設定し、後工程からの「引き」で仕事を始める運用。

**詳細** — Push 型（誰かが投入する）は仕掛りが増え、サイクルタイムが伸び、品質が落ちる。Pull 型は WIP 上限を超えると新規着手を止め、ボトルネック解消を優先する。Lean / TPS / Kanban の中核原則。

**関連** — [[Theory of Constraints]], [[Flow Framework]], [[Cycle Time]]。

**出典** — Smart et al., Ch.10。Anderson, *Kanban*。

### Servant Leadership / Host Leadership

**一行定義** — 「指示する」のではなく「障害を取り除き、文脈を提供する」型のリーダーシップ。

**詳細** — Robert Greenleaf (1970) が起源。BVSSH では Host Leadership（McKergow）を併用し、「ステージに上がる時」と「裏方に回る時」を意識的に切り替える。Westrum の Generative 文化を強化する手段。

**関連** — [[Westrum Culture]], [[Mission Command]]。

**出典** — Smart et al., Ch.5。Greenleaf, *The Servant as Leader*。

---

## 2. チームトポロジー / Team Topologies

> **Team Topologies** — Matthew Skelton, Manuel Pais (IT Revolution, 2019).
> 「組織と認知負荷をアーキテクチャの第一級制約として扱う」ための4つのチーム型と3つの相互作用モード。

### Conway's Law (コンウェイの法則)

**一行定義** — システムの構造は、それを設計する組織のコミュニケーション構造を写し取る。

**詳細** — Melvin Conway (1968) の論文 *How do committees invent?*。元来は記述的観察（「こうなる」）であって規範的主張ではない。組織が3つの部門で分かれていれば、システムは3層に分かれる、という現象。

**関連** — [[Inverse Conway Maneuver]], [[Sociotechnical Architecture]]。

**出典** — Conway, *Datamation* 1968。

### Inverse Conway Maneuver (逆コンウェイ戦略)

**一行定義** — 望ましいアーキテクチャを得るために、先に組織を再設計する戦略。

**詳細** — Conway's Law を **規範的** に逆用する。「マイクロサービス化したいから、まずチームをマイクロサービス境界に合わせて分割する」。組織変更なしでアーキテクチャだけ変えると、Conway's Law がそれを巻き戻す。

**関連** — [[Conway's Law]], [[Fracture Plane]], [[Bounded Context]]。

**出典** — Skelton & Pais, *Team Topologies*, Ch.2。

### Stream-aligned Team

**一行定義** — 単一の価値ストリーム（顧客セグメント・製品ライン）に **end-to-end** で責任を持つチーム。

**詳細** — Team Topologies の4つのチーム型の中核。他3型はすべて Stream-aligned Team を支えるために存在する。理想は「自チーム内で本番リリースまで完結できる」自律性を持つこと。

**関連** — [[Long-lived Value Streams]], [[Enabling Team]], [[Platform Team]], [[Complicated Subsystem Team]]。

**出典** — Skelton & Pais, Ch.5。

### Enabling Team (実現支援チーム)

**一行定義** — 専門領域（テスト自動化・セキュリティ・SRE等）の知識を Stream-aligned Team に **時限的に** 移植する横断チーム。

**詳細** — 常駐サポートではなく、「数週間〜数カ月で能力を移転して撤収する」のが原則。Communities of Practice の制度版と捉えるとよい。

**関連** — [[Facilitating]], [[Communities of Practice]]。

**出典** — Skelton & Pais, Ch.5。

### Complicated Subsystem Team (複雑サブシステムチーム)

**一行定義** — 数学的・科学的・法的専門性が必要で、Stream-aligned Team の認知負荷を超える領域を切り出して担うチーム。

**詳細** — 例: 動画コーデック、価格最適化アルゴリズム、決済精算、税法計算。Stream-aligned Team との関係は通常 **X-as-a-Service**。

**関連** — [[Cognitive Load]], [[X-as-a-Service]]。

**出典** — Skelton & Pais, Ch.5。

### Platform Team (プラットフォームチーム)

**一行定義** — Stream-aligned Team が「自分たちで本番運用できる」状態を、内部プラットフォーム（PaaS的なもの）として提供するチーム。

**詳細** — 顧客は **社内の他チーム**。プロダクトとして運用し、SLA / ロードマップ / ドキュメントを持つ。Thinnest Viable Platform（必要最小限）から始めるのが鉄則。

**関連** — [[Thinnest Viable Platform]], [[Platform as Product]], [[X-as-a-Service]]。

**出典** — Skelton & Pais, Ch.5。

### Thinnest Viable Platform (TVP)

**一行定義** — 「これ以上薄くしたら価値がなくなる」最小のプラットフォーム。

**詳細** — Platform Team の罠は「全部抱える」こと。TVP は「Stream-aligned Team の認知負荷を下げる **ちょうどそのライン** で止める」設計指針。CI/CD パイプライン・観測基盤・標準サービステンプレートくらいから始める例が多い。

**関連** — [[Platform Team]], [[Cognitive Load]]。

**出典** — Skelton & Pais, Ch.5。

### Interaction Modes (3つの相互作用モード)

**一行定義** — チーム間の関わり方を Collaboration / X-as-a-Service / Facilitating の3種に限定する制約。

**詳細** —
- **Collaboration**: 高帯域・短期。境界未確定の新領域を一緒に開拓する。コスト高だが学習速度高。
- **X-as-a-Service**: API/契約越し。境界が安定した領域。低コスト・低結合。
- **Facilitating**: Enabling Team が他チームの学習を加速する短期支援。

「すべてのチームがすべての他チームと話す」状態（混沌）を防ぐための **意図的な制限**。

**関連** — [[Stream-aligned Team]], [[Team API]]。

**出典** — Skelton & Pais, Ch.7。

### Team API

**一行定義** — チームが外部に公開する「コード・ドキュメント・コミュニケーション窓口・SLA」の総体。

**詳細** — ソフトウェアモジュールに API があるように、チームにも API がある。これを明示することで X-as-a-Service モードが成立する。曖昧な Team API は不必要な Collaboration を引き起こす。

**関連** — [[X-as-a-Service]], [[Platform as Product]]。

**出典** — Skelton & Pais, Ch.6。

### Cognitive Load (認知負荷)

**一行定義** — チームが扱える「考えること」の総量。Intrinsic / Extraneous / Germane の3種に分かれる。

**詳細** —
- **Intrinsic（内在的）**: 問題そのものの難しさ。例: ドメインの複雑さ。
- **Extraneous（外在的）**: 偶発的に増える負荷。例: 古いツール、複雑な手順。
- **Germane（学習的）**: スキル獲得のための負荷。例: 新パターンの学習。

Platform Team / TVP は Extraneous を削り、Stream-aligned Team が Intrinsic と Germane に集中できるようにする。Sweller の認知負荷理論をソフトウェアチーム設計に応用。

**関連** — [[Thinnest Viable Platform]], [[Team API]]。

**出典** — Skelton & Pais, Ch.3。Sweller, *Cognitive Load Theory*。

### Fracture Plane (分割面)

**一行定義** — モノリスやチームを分割する際に、最も自然な「割れ目」となる境界。

**詳細** — ビジネスドメイン境界、規制境界、変更速度境界、リスクプロファイル境界、ユーザペルソナ境界、地理・コンプラ境界、技術境界などが候補。DDD の Bounded Context と整合性が高い。誤った Fracture Plane は分散モノリスを生む。

**関連** — [[Bounded Context]], [[Architecture Quantum]], [[Inverse Conway Maneuver]]。

**出典** — Skelton & Pais, Ch.6。

---

## 3. 進化的アーキテクチャ / Evolutionary Architecture

> **Building Evolutionary Architectures** — Neal Ford, Rebecca Parsons, Patrick Kua (O'Reilly, 1st 2017 / 2nd 2023).
> 「未来は予測できない。だから **変化に耐える** ことを設計の目的に据える」。

### Evolutionary Architecture (進化的アーキテクチャ)

**一行定義** — 複数の次元にわたる「導かれた漸進的変化」を支えるアーキテクチャ。

**詳細** — 定義の構成要素:
- **Guided（導かれた）**: ランダムでなくフィットネス関数で方向付けされた変化。
- **Incremental（漸進的）**: ビッグバンでなく小刻みな変更。
- **Multiple dimensions（多次元）**: 技術 / データ / セキュリティ / 運用 / ドメインなど。

「変更可能性そのもの」を architectural characteristic（建築特性）として位置づける。

**関連** — [[Fitness Function]], [[Architectural Characteristic]], [[Architecture Quantum]]。

**出典** — Ford, Parsons, Kua, *Building Evolutionary Architectures* (1st/2nd ed)。

### Fitness Function (フィットネス関数)

**一行定義** — アーキテクチャ特性が「望ましい範囲内」にあるかを **自動的・継続的に** 評価する仕組み。

**詳細** — 遺伝的アルゴリズムの fitness function からの借用。例:
- 「全 API の p95 レイテンシが 200ms 未満」（性能）
- 「サービス間で循環依存ゼロ」（モジュラリティ）
- 「PII を含むテーブルは暗号化されている」（セキュリティ）

CI で実行する **automated fitness function** が中核。

**関連** — [[Architectural Characteristic]], [[Continuous Delivery]]。

**出典** — Ford et al., Ch.2。

### Fitness Function の分類軸

**一行定義** — Atomic / Holistic, Triggered / Continual, Static / Dynamic, Automated / Manual, Temporal, Intentional / Emergent, Domain-specific の7軸。

**詳細** —
- **Atomic vs Holistic**: 単一特性 vs 特性間の相互作用（例: 性能 ↔ セキュリティ）。
- **Triggered vs Continual**: イベント駆動 vs 常時計測。
- **Static vs Dynamic**: 閾値固定 vs スケールに応じ変化。
- **Automated vs Manual**: 自動 vs 人的レビュー（後者は最小化する）。
- **Temporal**: 時限性（例: TLS バージョン期限）。
- **Intentional vs Emergent**: 設計時定義 vs 運用中発見。
- **Domain-specific**: 業界規制由来（金融の取引監査など）。

**関連** — [[Fitness Function]]。

**出典** — Ford et al., 2nd ed Ch.2。

### Architectural Characteristic (アーキテクチャ特性)

**一行定義** — システムが満たすべき「-ility」(可用性・性能・セキュリティ・保守性等)を、トレードオフ可能な設計対象として扱った概念。

**詳細** — 旧称 Non-Functional Requirements（NFR）。Mark Richards & Neal Ford は「特性」と呼び直し、**3つまでに絞る** ことを推奨。すべて満たそうとすると何も満たせなくなる（unknown unknowns を考慮した上で）。

**関連** — [[Fitness Function]], [[Trade-off Analysis]]。

**出典** — Richards & Ford, *Fundamentals of Software Architecture*, Ch.4。

### Architecture Quantum (アーキテクチャ量子)

**一行定義** — 独立してデプロイ可能で、機能的凝集が高く、同期的に通信する **最小の単位**。

**詳細** — 単一のサービス = 1 quantum とは限らない。共有 DB を持つ2つのサービスは「1 quantum」。同期呼び出しでチェーン化された複数サービスも「1 quantum」。Quantum 境界 = Fracture Plane の有力候補。

**関連** — [[Fracture Plane]], [[Bounded Context]]。

**出典** — Ford, Richards, Sadalage, Dehghani, *Software Architecture: The Hard Parts*。

### Last Responsible Moment (LRM)

**一行定義** — 「決定を遅らせるコスト < 早く決めるリスク」となる最後の瞬間まで意思決定を保留する。

**詳細** — Lean ソフトウェア開発から。早すぎる決定は「逆転コスト」を生む。LRM までに学習を最大化し、選択肢を温存する。Evolutionary Architecture は LRM を運用上のデフォルトに置く。

**関連** — [[Set-based Concurrent Engineering]]。

**出典** — Poppendieck, *Lean Software Development*。Ford et al., Ch.7。

### Postel's Law (ロバストネス原則)

**一行定義** — 「送るものには厳格に、受け取るものには寛容に」。

**詳細** — Jon Postel (RFC 793, TCP)。進化的アーキテクチャでは契約進化の原則に転用される。Producer は最小限の保証だけ約束し、Consumer は未知フィールドを許容する。Consumer-Driven Contract Testing と組み合わせる。

**関連** — [[Consumer-Driven Contract]], [[Evolutionary Architecture]]。

**出典** — RFC 793。Ford et al., Ch.5。

### Architectural Decision Record (ADR)

**一行定義** — アーキテクチャ上の意思決定を「文脈・選択肢・決定・帰結」の構造で記録する文書。

**詳細** — Michael Nygard 起源 (2011)。進化的アーキテクチャでは「決定の進化」を追跡する不可欠なツール。Nygard / MADR / Y-Statement の3形式が普及。

**関連** — [[karak-architecture:adr-architect]] スキル。

**出典** — Nygard, *Documenting Architecture Decisions* (2011)。

---

## 4. 古典的指標 / Four Keys & Accelerate

> **Accelerate: The Science of Lean Software and DevOps** — Nicole Forsgren, Jez Humble, Gene Kim (IT Revolution, 2018).
> 4年間の DORA 調査をもとに「高パフォーマンス組織は何が違うか」を定量化。

### Four Keys (DORA Four Key Metrics)

**一行定義** — ソフトウェアデリバリ性能を測る4指標: Deployment Frequency / Lead Time for Changes / Change Failure Rate / Time to Restore Service。

**詳細** —
- **Deployment Frequency**: 本番デプロイ頻度（スループット系）。
- **Lead Time for Changes**: コミットから本番反映までの時間（スループット系）。
- **Change Failure Rate**: 本番障害につながった変更の割合（安定性系）。
- **Time to Restore Service (MTTR)**: 障害復旧までの時間（安定性系）。

スループット2軸 × 安定性2軸の組み合わせで「速さ vs 安定性のトレードオフは幻想」を実証した。

**2024 アップデート** — DORA *State of DevOps Report 2024* で **Rework Rate** が第5指標として追加され、Time to Restore はスループット側に再分類された。AI 採用が必ずしも配信性能を改善しないことが定量的に示された。

**関連** — [[DORA Performance Categories]], [[Reliability (5th key)]], [[Rework Rate]]。

**出典** — Forsgren et al., *Accelerate*, Ch.2。DORA *State of DevOps Report 2024*。

### Rework Rate (2024 追加指標)

**一行定義** — ユーザ向けバグへの対応で計画外に行われたデプロイの割合。Stability 側の新指標。

**詳細** — *State of DevOps Report 2024* で導入。「速くデプロイしているが、実は手戻りが多い」状態を Four Keys だけでは捉えきれなかった反省から。Change Failure Rate と組み合わせて Stability の解像度を上げる。

**関連** — [[Four Keys]], [[Change Failure Rate]]。

**出典** — DORA *State of DevOps Report 2024*。

### DORA Performance Categories (Elite / High / Medium / Low)

**一行定義** — Four Keys の閾値で組織を Elite / High / Medium / Low の4段階に分類するベンチマーク。

**詳細** — 例（2023 State of DevOps Report）:

| カテゴリ | Deploy Frequency | Lead Time | Change Failure Rate | MTTR |
|---|---|---|---|---|
| Elite | On-demand (複数回/日) | < 1 hour | 5% | < 1 hour |
| High | 1/週〜1/月 | 1日〜1週間 | 10% | < 1日 |
| Medium | 1/月〜1/6ヶ月 | 1週間〜1ヶ月 | 15% | < 1週間 |
| Low | < 1/6ヶ月 | 1ヶ月〜6ヶ月 | 64% | > 1週間 |

閾値は毎年の State of DevOps Report で更新される。**自社の絶対値より、改善トレンド** を見ること。

**関連** — [[Four Keys]]。

**出典** — DORA *State of DevOps Report*（年次）。

### Reliability (5th Key)

**一行定義** — 2021年に追加された「信頼性」指標。SLO達成率や運用性能を含む。

**詳細** — Four Keys は「変更プロセス」しか測らないという批判への応答。Reliability は SLO / SLA / SLI、可用性、レイテンシなどを統合した指標。実務では SRE の Error Budget と連動させる。

**関連** — [[Four Keys]], [[SLO/SLI/SLA]]。

**出典** — DORA *2021 State of DevOps Report*。

### 24 Capabilities (DORA Capability Model)

**一行定義** — Four Keys を改善する「24のケイパビリティ」を技術・プロセス・測定・文化の4領域で整理したモデル。

**詳細** — 例:
- **技術**: Version Control / Continuous Integration / Trunk-based Development / Test Automation / Deployment Automation / Shift Left on Security / ...
- **プロセス**: Customer Feedback / Working in Small Batches / Visual Management / ...
- **測定**: Monitoring / Proactive Notification / WIP Limits / ...
- **文化**: Westrum Culture / Learning Culture / Transformational Leadership / ...

「銀の弾丸」ではなく、24の地道なケイパビリティの組み合わせ。

**関連** — [[Westrum Culture]], [[Trunk-based Development]]。

**出典** — Forsgren et al., *Accelerate*, Appendix A。DORA *DevOps Capabilities*。

### Westrum Culture (組織文化の3類型)

**一行定義** — 組織を Pathological / Bureaucratic / Generative の3類型に分け、Generative がパフォーマンスを最大化するというモデル。

**詳細** — Ron Westrum (2004) の組織研究から。Generative 文化の特徴は:
- 高い協働
- 失敗の責任追及より学習
- 新規性の歓迎
- 情報の積極共有
- 部門間の橋渡し
- 共有された目標

DORA の調査で「Westrum スコア」が Four Keys と強く相関することが示された。

**関連** — [[Servant Leadership]], [[Generative Culture]]。

**出典** — Westrum, *A typology of organisational cultures* (2004)。Forsgren et al., Ch.3。

### SPACE Framework

**一行定義** — Four Keys の「過度な単純化」を補うため、開発者生産性を5次元で測るフレームワーク。

**詳細** — Microsoft Research, GitHub, University of Victoria 共同 (2021):
- **Satisfaction & Well-being**（満足度・健康）
- **Performance**（パフォーマンス）
- **Activity**（活動量）
- **Communication & Collaboration**（コミュニケーション）
- **Efficiency & Flow**（効率・フロー）

「単一指標で生産性を測ろうとすると Goodhart's Law（指標が目的化）で歪む」という洞察。**3次元以上を組み合わせて使う** のが推奨。

**関連** — [[Four Keys]], [[Goodhart's Law]], [[Developer Experience]]。

**出典** — Forsgren, Storey, Maddila, Zimmermann, Houck, Butler, *The SPACE of Developer Productivity* (Queue 2021)。

**後続フレームワーク** — SPACE は 2023年に [[DevEx Framework]] に進化し、さらに 2024-12 に [[DX Core 4]] が経営層向け統合フレームワークとして発表された。SPACE 原型は学習リソースとして残存するが、実務適用は DevEx / DX Core 4 に移行中。

### DevEx Framework

**一行定義** — 開発者体験を Feedback Loops / Cognitive Load / Flow State の3軸で計測する SPACE の進化形フレームワーク。

**詳細** — Abi Noda (DX 社 CEO), Margaret-Anne Storey, Nicole Forsgren, Michaela Greiler (2023)。SPACE の5次元が「測れるが、改善行動に繋がりにくい」という反省から、**開発者の主観体験** を中核に据え直した。

- **Feedback Loops（フィードバックループ）**: コード反映・テスト結果・本番監視までの応答速度。
- **Cognitive Load（認知負荷）**: Team Topologies と同じ概念。タスクに必要な思考量。
- **Flow State（フロー状態）**: 中断・コンテキストスイッチ・割り込みの最小化。

**関連** — [[SPACE Framework]], [[DX Core 4]], [[Cognitive Load]]。

**出典** — Noda, Storey, Forsgren, Greiler, *DevEx: What Actually Drives Productivity* (Queue 2023)。

### DX Core 4

**一行定義** — DORA + SPACE + DevEx を統合した経営層向け開発者生産性フレームワーク（2024-12 発表）。

**詳細** — Abi Noda & Laura Tacho (DX 社) が発表。CTO/CEO/CFO レベルで意思決定に使える 4つのコア指標群:

- **Speed**: Diffs per Engineer など、変更スループットの代理変数。
- **Effectiveness**: 開発者の主観効率（DevEx の Flow State / Cognitive Load 寄り）。
- **Quality**: Change Failure Rate / Rework など（DORA Stability 寄り）。
- **Business Impact**: 機能採用率 / Revenue per Engineer など、事業成果。

DORA・SPACE・DevEx の「測ったあとに何をするか」が曖昧という批判への応答。各 Big-Tech が KPI に取り込み始めている。

**関連** — [[Four Keys]], [[SPACE Framework]], [[DevEx Framework]]。

**出典** — Noda & Tacho, *Introducing the DX Core 4* (2024-12)。

### Flow Framework (Mik Kersten)

**一行定義** — 価値ストリームを Feature / Defect / Risk / Debt の4種の「Flow Item」で計測する経営層向けフレームワーク。

**詳細** — *Project to Product* (Mik Kersten, 2018)。指標:
- **Flow Velocity**: 完了 Flow Item 数 / 期間
- **Flow Time**: 着手から完了までの時間
- **Flow Efficiency**: 待ち時間を除いた実作業時間比率
- **Flow Load**: 仕掛り Flow Item 数
- **Flow Distribution**: 4種の比率（健全な比率は文脈依存）

Four Keys が「デリバリ工程」を測るのに対し、Flow Framework は「ビジネス成果との接続」を測る。

**関連** — [[Project to Product]], [[Four Keys]]。

**出典** — Kersten, *Project to Product*。

---

## 5. 周辺・必須関連 / Adjacent Essentials

### Wardley Mapping

**一行定義** — 「ユーザニーズ → 価値連鎖」を縦軸、「進化段階 (Genesis → Custom → Product → Commodity)」を横軸に置く戦略マップ。

**詳細** — Simon Wardley が Canonical 在籍時に開発。コンポーネントの **進化段階** に応じて適切な手法・組織構造・契約形態を変えるべき、という主張。Strategy Cycle（Purpose → Landscape → Climate → Doctrine → Leadership）で運用する。

**進化段階の含意**:
- Genesis / Custom-built: Pioneers が探索（高失敗率前提）
- Product: Settlers が安定化
- Commodity / Utility: Town Planners が運用最適化

**関連** — [[Pioneers, Settlers, Town Planners]], [[Three Horizons]]。

**出典** — Wardley, *Wardley Maps*（Medium / CC-BY-SA）。

### Pioneers, Settlers, Town Planners (PST)

**一行定義** — 進化段階に応じた3つのチームスタイル: 探索者・定着者・都市計画者。

**詳細** —
- **Pioneers**: 不確実領域で「動くもの」を作る。失敗を学習資源とする。
- **Settlers**: Pioneers の発見を製品化・スケール化する。
- **Town Planners**: 製品をコモディティ化・工業化する。SLA・運用最適化に強い。

同じ人が3役を兼ねるのは難しく、Promotion path も別に設計する必要がある。

**関連** — [[Wardley Mapping]], [[Three Horizons]]。

**出典** — Wardley, *Pioneers, Settlers and Town Planners* (blog post)。

### Bounded Context (境界づけられたコンテキスト)

**一行定義** — Ubiquitous Language（同じ用語が同じ意味を持つ）が成立する **言語境界**。

**詳細** — Eric Evans, *Domain-Driven Design* (2003) の戦略パターンの中核。同じ「顧客 (Customer)」という単語が、営業コンテキストでは「契約候補」、出荷コンテキストでは「配送先」を意味する。これを混ぜると Big Ball of Mud になる。Bounded Context は **Fracture Plane の第一候補**。

**関連** — [[Fracture Plane]], [[Context Mapping]], [[Architecture Quantum]]。

**出典** — Evans, *DDD*, Ch.14。

### Context Mapping パターン

**一行定義** — Bounded Context 間の関係を9つの関係性パターンで記述する技法。

**詳細** —
- **Partnership**: 相互依存。両者で同時にリリース。
- **Shared Kernel**: 共有モデル領域。変更には双方の合意。
- **Customer-Supplier**: 上下流。下流の声が上流に届く。
- **Conformist**: 上下流。下流は上流に従う（影響力なし）。
- **Anticorruption Layer (ACL)**: 上流モデルから自モデルを守る変換層。
- **Open Host Service**: 多数の下流向けに公開された安定API。
- **Published Language**: Open Host が使う標準化されたデータ語彙。
- **Separate Ways**: 統合しない選択。
- **Big Ball of Mud**: 統合不能な混沌（避けるべき状態の記述）。

**関連** — [[Bounded Context]], [[Team API]]。

**出典** — Evans, *DDD*, Ch.14。Vernon, *Implementing DDD*。

### Subdomain Types (Core / Supporting / Generic)

**一行定義** — ドメインを「コア（競争優位）/ サポート（自社固有・非競争）/ ジェネリック（汎用）」に分類する戦略的判断。

**詳細** —
- **Core**: 競争優位の源泉。最高の人材と内製を投じる。
- **Supporting**: 自社固有だが競争優位ではない。最低限の内製。
- **Generic**: 業界共通。SaaS / OSS / 外部委託が合理的。

「すべて Core」「すべて Generic」も誤り。**Core を見極めて投資集中する** のが戦略。

**関連** — [[Wardley Mapping]] の Product/Commodity と整合。

**出典** — Evans, *DDD*, Ch.15。

### Sociotechnical Architecture

**一行定義** — 社会システム（人・組織・文化）と技術システムを **同時最適化** すべき不可分のシステムとして扱う設計思想。

**詳細** — Tavistock Institute (1949) の Trist & Bamforth による炭鉱研究が起源。「技術だけ最適化しても人間系がボトルネックになる」という発見。現代では Trond Hjorteland, Eduardo da Silva らが Team Topologies + DDD + EventStorming + Wardley を統合する **Sociotechnical Architect** の概念を提唱。

**関連** — [[Conway's Law]], [[Joint Optimization]]。

**出典** — Trist & Bamforth (1951), *Some social and psychological consequences of the longwall method of coal-getting*。

### Cynefin Framework

**一行定義** — 状況を Clear / Complicated / Complex / Chaotic / Confusion の5領域に分け、領域ごとに適切な意思決定方式を選ぶ枠組み。

**詳細** — Dave Snowden 開発。
- **Clear (旧 Obvious / Simple)**: 因果が明確 → Sense-Categorize-Respond。ベストプラクティス適用。
- **Complicated**: 専門家が因果を分析できる → Sense-Analyze-Respond。Good Practice。
- **Complex**: 因果は後知恵でしか分からない → Probe-Sense-Respond。Emergent Practice。
- **Chaotic**: 因果関係なし → Act-Sense-Respond。Novel Practice。
- **Aporetic / Confused (旧 Disorder / Confusion)**: どの領域か判別不能。**2024年に Snowden は中央領域を "Aporetic"（哲学用語で「行き詰まり」「診断的不確実性」）に改名**。「Chaotic という語の使用に過信があった」と公に認めている。

ソフトウェア開発の多くは **Complex** にある（だから実験が必要）。BVSSH の VOICE も Cynefin Complex 領域への応答。

**関連** — [[VOICE]], [[Experiments]]。

**出典** — Snowden & Boone, *A Leader's Framework for Decision Making* (HBR 2007)。

### Theory of Constraints (制約理論)

**一行定義** — システムのスループットは「最も弱いリンク（制約）」で決まる、という Goldratt の主張。

**詳細** — 5 Focusing Steps: ① Identify the constraint, ② Exploit it, ③ Subordinate everything to it, ④ Elevate it, ⑤ Repeat。Goldratt の小説 *The Goal* (1984) で広く普及。DevOps の Three Ways（Flow / Feedback / Continual Learning）の理論的基盤。

**関連** — [[Three Ways]], [[Flow Framework]]。

**出典** — Goldratt, *The Goal*。

### The Three Ways (DevOps三本柱)

**一行定義** — DevOps の哲学的基盤を Flow（流れ）/ Feedback（フィードバック）/ Continual Learning（継続学習）の3原則で表したもの。

**詳細** — Gene Kim (*The Phoenix Project*, 2013):
- **First Way (Flow)**: 開発 → 運用 → 顧客への流れを最適化。
- **Second Way (Feedback)**: 下流から上流への高速フィードバック。
- **Third Way (Continual Learning)**: 実験・反復・学習文化。

Four Keys は Flow / Feedback の計測手段とみなせる。

**関連** — [[Four Keys]], [[Theory of Constraints]]。

**出典** — Kim et al., *The DevOps Handbook*。

### Strangler Fig Pattern

**一行定義** — 既存システムを一気に置き換えず、新システムが「絞め殺すように」徐々に機能を奪っていく漸進移行パターン。

**詳細** — Martin Fowler (2004) 命名。本来は熱帯雨林の植物（イチジク）の生態から。ビッグバン書き換えのリスクを避け、Evolutionary Architecture と整合的な移行戦略。

**関連** — [[Evolutionary Architecture]], [[Three Horizons]]。

**出典** — Fowler, *StranglerFigApplication* (martinfowler.com, 2004)。

### Goodhart's Law

**一行定義** — 「測定指標が目標になると、それは良い指標ではなくなる」。

**詳細** — Charles Goodhart (1975) の経済学的観察を Marilyn Strathern が一般化した。Four Keys や SPACE の運用上の最大の落とし穴。指標は **目的の代理変数** であり、目的そのものではない。

**関連** — [[SPACE Framework]], [[Outcomes over Outputs]]。

**出典** — Goodhart (1975)。Strathern (1997)。

---

## 6. 2024-2025 統合フレームワーク / Integrative Frameworks (Recent)

> 2024-2025 に登場した「複数概念を束ねた処方的フレームワーク」。
> 個別概念ではなく **組み合わせ方** に重みを置く点が特徴。

### Architecture Modernization (Nick Tune の統合実装書)

**一行定義** — Wardley Mapping / Team Topologies / DDD / EventStorming を **同時に運用** するための統合フレームワーク。

**詳細** — Nick Tune *Architecture Modernization* (Manning, 2024)。Eduardo da Silva との共同登壇・対談で発展。書籍が提供するのは以下のセットフロー:

1. **ビジネス景観の可視化**: Wardley Map で Genesis〜Commodity 軸の位置を診断。
2. **プロダクトタクソノミ構築**: アーキテクチャの枠組みとなるプロダクトの分類体系を作る。
3. **Big Picture EventStorming**: ドメインイベントから境界候補を発見。
4. **Team Topologies 適用**: 価値ストリームを特定し、4チーム型に再編。
5. **AMET で変革を駆動**: 短期的な実現支援チームが推進する。

「個別パターンを知っていても変革は進まない、束ねかたを知っているか」が中心メッセージ。

**関連** — [[Wardley Mapping]], [[Team Topologies]], [[Bounded Context]], [[EventStorming]], [[AMET]]。

**出典** — Tune, *Architecture Modernization: Socio-technical alignment of software, strategy, and structure* (Manning, 2024)。

### AMET (Architecture Modernization Enabling Team)

**一行定義** — アーキテクチャ・モダナイゼーションを **時限的に推進する** 実現支援チーム。

**詳細** — Nick Tune が *Architecture Modernization* で提唱。Team Topologies の Enabling Team を「アーキテクチャ変革」に特化させた役割。常駐型の変革チームではなく、Stream-aligned Team が自走できるようになるまで並走し、撤収する。「変革専門部署」が永続化する典型的失敗パターンへの応答。

**役割の典型**:
- 全社的なアーキテクチャ可視化（Wardley Map）の作成と更新
- EventStorming ワークショップのファシリテーション
- パターン適用のコーチング
- ADR レビューと標準化
- Federated Governance の「policy」側の整備

**関連** — [[Enabling Team]], [[Architecture Modernization]], [[Federated Governance]]。

**出典** — Tune, *Architecture Modernization* (2024)。

### EventStorming

**一行定義** — ドメイン専門家とエンジニアが付箋を使って、ドメインイベント中心に業務を可視化する協働ワークショップ。

**詳細** — Alberto Brandolini が考案 (2013-)。オレンジ付箋 = Domain Event、青 = Command、黄 = Aggregate、ピンク = Hot Spot（不明点）など色で分類し、時系列に並べる。

**3つのレベル**:
- **Big Picture**: 全社/全ドメインの俯瞰。Bounded Context 候補の発見。
- **Process Modeling**: 1つの業務プロセスを深掘り。コマンドとイベントの順序。
- **Software Design**: Aggregate と不変条件の特定。実装に直結。

DDD 採用の入り口として最も普及した手法。Tech Radar Trial 入り。

**関連** — [[Bounded Context]], [[Aggregate]], [[Architecture Modernization]]。

**出典** — Brandolini, *Introducing EventStorming* (Leanpub)。

### Product Operating Model

**一行定義** — プロジェクト型運営（期間限定・予算固定）から、プロダクト型運営（永続・成果駆動）に組織全体を移行する考え方。

**詳細** — Mik Kersten *Project to Product* (2018) と Marty Cagan *Empowered* (2020) の合流地点。

**プロジェクト型 → プロダクト型のシフト**:

| 軸 | プロジェクト型 | プロダクト型 |
|---|---|---|
| 寿命 | 期間限定 | 永続 |
| 成功基準 | スコープ・予算・期日 | アウトカム |
| 学習 | プロジェクト終了で蒸発 | チーム内で累積 |
| 改善 | 別プロジェクト化 | 継続 |
| 顧客接点 | プロジェクト末期 | 常時 |

Planview 2024 P2P State of the Industry によれば、回答者の過半数が「5年で 80% がプロダクト型」と予測。一方、97% が阻害要因に直面と回答。

**関連** — [[Long-lived Value Streams]], [[Flow Framework]], [[Outcomes over Outputs]]。

**出典** — Kersten, *Project to Product* (2018)。Planview 2024 P2P Report。

---

## 7. エンジニアリング実践 / Engineering Practices (DORA Capabilities)

> DORA *Accelerate* の Capability Model が「規範」として確立した実践群。
> 業界での前提的語彙となっており、★★★★★ 級の重み。

### Continuous Delivery (継続的デリバリ)

**一行定義** — 「いつでも本番にリリース可能な状態」をソフトウェアの常態として維持する規範。

**詳細** — Jez Humble & David Farley *Continuous Delivery* (2010)。Continuous Integration の上位概念。要件:

- すべてのコード変更が deployment pipeline を通る
- パイプラインが本番準拠の環境でテストを実行
- 「リリースは経営判断、技術判断ではない」を保証する状態

DORA Four Keys の **Deployment Frequency** と **Lead Time** はこれの結果指標。

**関連** — [[Trunk-based Development]], [[Four Keys]], [[Deployment Pipeline]]。

**出典** — Humble & Farley, *Continuous Delivery* (Addison-Wesley, 2010)。

### Trunk-based Development (トランクベース開発)

**一行定義** — 全開発者が小さなバッチを「最低1日1回」trunk にマージする開発手法。

**詳細** — 長寿命の feature branch を作らず、未完成機能は **Feature Flag** で隠す。Continuous Integration の前提条件。

**現状（2025）の課題**: DORA 報告によれば、依然として「重い code review プロセスがボトルネック」となり、完全採用は rare とされる。「数時間〜数日のレビュー待ちが small batches を阻害する」と DORA が公式に指摘。

**関連** — [[Continuous Delivery]], [[Feature Flag]], [[Continuous Integration]]。

**出典** — DORA Capabilities — Trunk-based Development。Paul Hammant *Trunk Based Development*。

### Internal Developer Platform (IDP) / Platform Engineering

**一行定義** — Stream-aligned Team が「自分たちで本番運用できる」状態を製品化した社内プラットフォーム、およびそれを運営する規律。

**詳細** — Team Topologies の Platform Team / Thinnest Viable Platform を実装レベルに具体化した分野。Gartner 予測:

- 2025 採用率 **55%** → 2026 予測 **80%**（2022年は 45%）
- 既存 IDP の **89%** が Backstage を採用
- Backstage は CNCF プロジェクトの中で end-user commit 数 4位（Kubernetes / OpenTelemetry / Argo に次ぐ）

「Backstage か、Port / Rely / Roadie などの ITY-Value 早期化 SaaS か、Mia-Platform / Compass などのエンタープライズ統合か」の3軸選択が業界の典型構図。

**関連** — [[Platform Team]], [[Thinnest Viable Platform]], [[Platform as Product]]。

**出典** — Gartner Hype Cycle for Platform Engineering 2024/2025。CNCF Annual Report。

---

## 8. 参照スキル / Related Skills in this Plugin

- [[karak-architecture:adr-architect]] — アーキテクチャ意思決定の記録
- [[karak-architecture:write-c4-diagram]] — C4 モデルによるアーキテクチャ可視化
- [[karak-product:requirements-analyst]] — 要件定義（Outcomes → Requirements）
- [[karak-product:agile-project-manager]] — クロスプラットフォーム開発のプロジェクト計画

---

## 9. 一次文献リスト

| 領域 | 書籍 | 著者 | 発行 |
|---|---|---|---|
| BVSSH | *Sooner Safer Happier* | Smart, Berend, Ogilvie, Rohrer | 2020 |
| Team Topologies | *Team Topologies* | Skelton, Pais | 2019 |
| Evolutionary | *Building Evolutionary Architectures* (2nd) | Ford, Parsons, Kua | 2023 |
| Evolutionary | *Software Architecture: The Hard Parts* | Ford, Richards, Sadalage, Dehghani | 2021 |
| Four Keys | *Accelerate* | Forsgren, Humble, Kim | 2018 |
| Four Keys | *State of DevOps Report* (年次) | DORA | 2014〜 |
| Wardley | *Wardley Maps* | Wardley | (CC-BY-SA, Medium) |
| DDD | *Domain-Driven Design* | Evans | 2003 |
| DDD | *Implementing Domain-Driven Design* | Vernon | 2013 |
| Project→Product | *Project to Product* | Kersten | 2018 |
| Lean | *Lean Software Development* | Poppendieck | 2003 |
| ToC | *The Goal* | Goldratt | 1984 |
| DevOps | *The DevOps Handbook* | Kim, Humble, Debois, Willis | 2016 |
| Cynefin | *A Leader's Framework for Decision Making* (HBR) | Snowden, Boone | 2007 |
| SPACE | *The SPACE of Developer Productivity* | Forsgren et al. | 2021 |
| Architecture | *Fundamentals of Software Architecture* | Richards, Ford | 2020 |
| Modernization | *Architecture Modernization* | Tune | 2024 |
| Continuous Delivery | *Continuous Delivery* | Humble, Farley | 2010 |
| Developer Productivity | *DevEx: What Actually Drives Productivity* (Queue) | Noda, Storey, Forsgren, Greiler | 2023 |
| Developer Productivity | *Introducing the DX Core 4* (newsletter) | Noda, Tacho | 2024-12 |
| EventStorming | *Introducing EventStorming* | Brandolini | 継続更新 |
| Product Operating | *Empowered* | Cagan | 2020 |
| Team Topologies | *Team Topologies* (2nd ed) | Skelton, Pais | 2025-08 |
