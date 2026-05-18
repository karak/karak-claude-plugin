# アーキテクチャ原則 概念マップ

「どの概念が、どの組織課題に効くか」を 8つの問題領域 × 主要概念のマトリクスで示す。
glossary.ja.md と対になる **使い分けのための地図**。

## 全体像 — 4文献の役割分担

```
                       BVSSH ──────────────┐
                  (なぜ変えるか・成果)        │
                                            │
                                            ▼
  Wardley Mapping ─→  問題領域の地図化 ─→ 進化的アーキテクチャ
   (どこを変えるか)         │              (どう変え続けるか)
                            │                    │
                            ▼                    ▼
                   Team Topologies          Four Keys
                  (誰が・どう組むか)         (うまくいっているか)
```

| 文献 | 主な問い | 主な処方 |
|---|---|---|
| BVSSH | なぜ・何を変えるのか | アウトカム志向、Federated Governance、Pull System |
| Team Topologies | 誰がどう組むのか | 4チーム型 + 3相互作用モード + 認知負荷 |
| Evolutionary Architecture | 変化にどう備えるのか | フィットネス関数、Architecture Quantum、LRM |
| Four Keys / Accelerate | うまく回っているのか | 4指標、24 Capabilities、Westrum 文化 |

---

## 問題領域 × 概念マトリクス

| # | 問題領域 | 主にここで使う | 補強として使う |
|---|---|---|---|
| 1 | 組織とアーキテクチャの整合 | Conway's Law / Inverse Conway / Stream-aligned Team / Bounded Context | Fracture Plane / Architecture Quantum / Sociotechnical |
| 2 | 変化への耐性 | Evolutionary Architecture / Fitness Function / Architectural Characteristic | Postel's Law / LRM / Strangler Fig |
| 3 | 価値とリスクの優先順位 | BVSSH / Outcomes over Outputs / Wardley Mapping | Three Horizons / North Star / VOICE |
| 4 | 改善の計測 | Four Keys / DORA Performance Categories | SPACE / Flow Framework / Goodhart's Law (警告) |
| 5 | 段階的モダナイゼーション | Three Horizons / Strangler Fig / Pioneers-Settlers-Town Planners | Federated Governance / MVC / Last Responsible Moment |
| 6 | 認知負荷の管理 | Cognitive Load (3種) / Thinnest Viable Platform / Team API | Platform as Product / X-as-a-Service |
| 7 | 境界の引き方 | Bounded Context / Context Mapping / Subdomain Types | Fracture Plane / Architecture Quantum |
| 8 | 文化と意思決定 | Westrum Culture / Servant Leadership / Cynefin | Three Ways / Theory of Constraints / ADR |

---

## 1. 組織とアーキテクチャの整合 (Org/Architecture Alignment)

**症状**: 「マイクロサービスにしたのに開発速度が上がらない」「分散モノリス化した」「ある変更に5チームが関わる」。

**診断の問い**:
- 変更1件あたり何チームが関わるか？
- チーム間ハンドオフは何回発生するか？
- ある Bounded Context が複数チームに分散していないか？

**処方の系統樹**:

```
Conway's Law (現象認識)
    │
    ├─→ Inverse Conway Maneuver (戦略: 組織を先に変える)
    │       │
    │       ├─→ Stream-aligned Team を中核に再編
    │       │       └─→ Long-lived Value Streams
    │       │
    │       └─→ Fracture Plane で分割境界を選定
    │              ├─→ Bounded Context (DDD)
    │              ├─→ Architecture Quantum (Evolutionary)
    │              └─→ 規制境界 / 変更速度境界
    │
    └─→ Sociotechnical Architecture (前提)
            「社会系と技術系は同時最適化する」
```

**主要トレードオフ**:

| やりたいこと | 取るべき相互作用モード | 注意点 |
|---|---|---|
| 未知領域の探索 | Collaboration | 長期化すると境界が曖昧になる |
| 安定境界での共存 | X-as-a-Service | Team API が未定義だと崩壊 |
| 能力移転 | Facilitating (Enabling Team) | 常駐化させない（時限的） |

---

## 2. 変化への耐性 (Enabling Continuous Change)

**症状**: 「リリースが怖い」「テスト不在で変更が手詰まり」「セキュリティ要件で全体再設計が必要に」。

**診断の問い**:
- 想定していなかった要件変化に何日で対応できるか？
- アーキテクチャ特性のうち、自動検証されているのは何個か？
- 「重要だが計測していない」特性はどれか？

**処方の系統樹**:

```
Evolutionary Architecture (目的)
    │
    ├─→ Architectural Characteristic を3つに絞る
    │       (例: スケーラビリティ / 監査可能性 / 保守性)
    │
    ├─→ 各特性に Fitness Function を定義
    │       │
    │       ├─→ Atomic / Holistic 軸で粒度設計
    │       ├─→ Triggered / Continual 軸で計測タイミング設計
    │       └─→ Automated 優先 (Manual は最小化)
    │
    ├─→ Architecture Quantum を意識した変更単位
    │
    ├─→ Postel's Law で契約を進化可能に
    │       └─→ Consumer-Driven Contract Testing
    │
    ├─→ Last Responsible Moment で意思決定を遅延
    │
    └─→ ADR で「なぜそう決めたか」を記録
            (将来の進化判断の参照点)
```

**「変化耐性」を測る代替指標**:
- 新規 Architectural Characteristic を追加したときの影響範囲
- 既存 Fitness Function を新規サービスに適用するコスト
- Strangler Fig 適用時のロールバック容易さ

---

## 3. 価値とリスクの優先順位 (Value & Risk Prioritization)

**症状**: 「すべてが最優先」「ロードマップが機能リストになっている」「投資判断がエンジニアの声の大きさで決まる」。

**診断の問い**:
- ロードマップは Outcome で書かれているか？ Output で書かれているか？
- 各取り組みは Wardley Map のどこに位置するか？
- Three Horizons の配分はどうなっているか？

**処方の系統樹**:

```
BVSSH の Better-Value-Sooner-Safer-Happier
    │
    ├─→ Outcomes over Outputs (ロードマップ書き換え)
    │       └─→ OKR の Key Result をアウトカムで書く
    │
    ├─→ VOICE (Vision-Outcome-Intent-Context-Experiments)
    │       └─→ Mission Command 型の伝達言語
    │
    └─→ Wardley Mapping (どこに投資するか)
            │
            ├─→ Genesis / Custom: Pioneers の探索 (高失敗率前提)
            ├─→ Product: Settlers の製品化
            └─→ Commodity: Town Planners の運用最適化
                   └─→ ここを内製するのは無駄
```

**Three Horizons × Wardley の対応**:

| Horizon | Wardley段階 | 主役 | 成功指標 | リスク許容 |
|---|---|---|---|---|
| H3 (未来) | Genesis | Pioneers | 学習量 | 失敗常態 |
| H2 (拡張) | Custom / Product | Settlers | 採用率 | 中程度 |
| H1 (現行) | Product / Commodity | Town Planners | SLA達成 | 低 |

**警告**: H1 の指標で H3 を評価すると、すべての探索が「失敗」に見える。

---

## 4. 改善の計測 (Measurement)

**症状**: 「指標が増えたが改善が見えない」「ダッシュボードが意思決定に使われない」「ベロシティが上がっても顧客満足は下がる」。

**診断の問い**:
- 指標は「変更プロセス」「価値創出」「人の状態」のどこを測っているか？
- 1つの指標で評価していないか？（Goodhart's Law）
- 指標を改善することと、ビジネス成果を改善することは一致しているか？

**処方の系統樹**:

```
Four Keys (デリバリ性能の基礎)
    │
    ├─→ Throughput 軸
    │     ├─ Deployment Frequency
    │     └─ Lead Time for Changes
    │
    ├─→ Stability 軸
    │     ├─ Change Failure Rate
    │     └─ Time to Restore Service
    │
    └─→ + Reliability (2021 追加: SLO達成率)

  ↑ ここまでは「変更プロセス」のみ計測

SPACE Framework (補完: 開発者の状態)
    ├─ Satisfaction & Well-being
    ├─ Performance
    ├─ Activity
    ├─ Communication & Collaboration
    └─ Efficiency & Flow

Flow Framework (補完: ビジネス価値の流れ)
    ├─ Flow Velocity
    ├─ Flow Time
    ├─ Flow Efficiency
    ├─ Flow Load
    └─ Flow Distribution (Feature/Defect/Risk/Debt)
```

**指標の組み合わせ指針**:

| 視点 | 採用指標 | 警告 |
|---|---|---|
| デリバリ性能 | Four Keys | Goodhart's Law: デプロイ頻度だけ追うと "no-op deploy" が増える |
| 開発者体験 | SPACE 3〜5次元 | Activity だけ追うと作業量主義に陥る |
| 事業接続 | Flow Distribution | Feature 100% にすると技術的負債爆発 |

**重要原則**:
- **絶対値より変化率** を見る（業界・組織で閾値の意味は変わる）
- **指標は仮説**。次の四半期に何を学んだら指標を入れ替えるか、決めておく
- **Westrum 文化スコア** が低い組織では、Four Keys 改善は持続しない

---

## 5. 段階的モダナイゼーション (Phased Modernization)

**症状**: 「全社アジャイル変革プロジェクト」が頓挫した。「ビッグバン移行」で半年遅延。「PoC は成功したが本格展開で破綻」。

**診断の問い**:
- 「現行 / 拡張 / 探索」の3層を、別々のリーダーシップ・別々の指標で運用しているか？
- 移行は Strangler Fig 型か、Replace All 型か？
- 「敷石 (Paved Road)」が用意されているか？

**処方の系統樹**:

```
Three Horizons で投資配分
    │
    ├─→ H1 (現行): Long-lived Value Streams で持続改善
    │       └─→ Four Keys で計測
    │
    ├─→ H2 (拡張): Strangler Fig で漸進移行
    │       │
    │       └─→ Federated Governance + Minimum Viable Compliance
    │              （統制は必要、過剰統制は避ける）
    │
    └─→ H3 (探索): Pioneers が安全に失敗できる場
            └─→ Last Responsible Moment で標準化を遅延

各層に共通: Platform Team が Thinnest Viable Platform を提供
                └─→ 移行の摩擦を下げる「敷石 Paved Road」
```

**Strangler Fig の運用パターン**:

```
[Legacy System] ←─ 全トラフィック
        ↓
[Legacy] + [Façade (Routing)] ─→ [New: 1機能]
        ↓                          ↓
[Legacy: 残機能] + [Façade] ─→ [New: 増えていく機能]
        ↓                          ↓
                  [New: 全機能]   ←─ Façade 撤去
```

**失敗パターン**:
- Façade を作らず、両系統を並走させた → データ不整合
- 旧系のフラグだけで切り替えた → ロールバック不能
- New 側の Bounded Context を旧系に合わせた → 同じ問題を再生産

---

## 6. 認知負荷の管理 (Cognitive Load Management)

**症状**: 「新メンバーが半年経っても自走できない」「1チームが扱うサービスが20を超えた」「ドキュメントを書く時間がない」。

**診断の問い**:
- Stream-aligned Team が抱えるサービス数・ツール数は妥当か？
- Intrinsic / Extraneous / Germane のどの負荷が高いか？
- Platform Team は「内部顧客がいる Product」として運用されているか？

**処方の系統樹**:

```
Cognitive Load の分解
    │
    ├─→ Intrinsic (ドメイン本来の複雑さ)
    │     └─→ 削れない。Subdomain を Core に絞る
    │
    ├─→ Extraneous (偶発的負荷)
    │     │
    │     ├─→ Platform Team が Thinnest Viable Platform で削る
    │     │     ├─ CI/CD パイプライン
    │     │     ├─ 観測基盤
    │     │     ├─ サービステンプレート
    │     │     └─ 「Paved Road」整備
    │     │
    │     └─→ Team API の明示で「他チームに聞かないと進まない」を減らす
    │
    └─→ Germane (学習負荷)
          └─→ Enabling Team が時限的に並走
                  (常駐は Extraneous に逆戻り)
```

**Platform as Product チェックリスト**:
- [ ] 内部顧客（Stream-aligned Team）を特定している
- [ ] ロードマップを公開している
- [ ] SLO / SLA を持っている
- [ ] ドキュメントが Onboarding Path として機能している
- [ ] 利用統計を計測し、改善に反映している
- [ ] 「使われていない機能」を削除する勇気を持っている

---

## 7. 境界の引き方 (Boundary Design)

**症状**: 「サービスAを変更するたびにサービスB,C,Dも変更が必要」「同じ概念が違う意味で使われている」「DBスキーマが複数チームの結合点になっている」。

**診断の問い**:
- Ubiquitous Language は Bounded Context 内で一貫しているか？
- Architecture Quantum 境界と Team 境界は一致しているか？
- 共有 DB は意図したものか、惰性か？

**処方の系統樹**:

```
境界候補の発見
    │
    ├─→ EventStorming (ドメイン専門家との協働ワークショップ)
    │     ├─ Domain Event (起きたこと)
    │     ├─ Command (引き起こす操作)
    │     └─ Aggregate (一貫性境界)
    │
    └─→ Wardley Map での進化段階分析
          (Genesis と Commodity を同じチームに持たせない)

境界の確定
    │
    ├─→ Bounded Context (言語境界)
    │
    ├─→ Architecture Quantum (同期通信境界)
    │
    └─→ Fracture Plane (組織分割面)
        ├─ ビジネスドメイン
        ├─ 規制 / コンプラ
        ├─ 変更速度
        ├─ リスクプロファイル
        ├─ ユーザペルソナ
        ├─ 地理 / 言語
        └─ 技術 / 性能要件

境界間の関係を設計
    │
    └─→ Context Mapping (9パターンから選ぶ)
          ├─ Partnership: 双方向の協働が必要な領域
          ├─ Customer-Supplier: 上下流の声が届く関係
          ├─ Conformist: 力関係で従う（避けたいなら ACL）
          ├─ Anticorruption Layer: 上流の影響から自モデルを守る
          ├─ Open Host Service + Published Language: 多数の下流向け公開API
          ├─ Shared Kernel: 最小限の共有モデル
          └─ Separate Ways: 統合しない選択
```

**「分散モノリス」回避チェックリスト**:
- [ ] サービス間呼び出しチェーンが3段以下
- [ ] 1つのユースケースで複数 Bounded Context を更新するトランザクションがない
- [ ] サービス間の共有 DB / 共有テーブルがない
- [ ] サービス間の循環依存がない（Fitness Function で検査）
- [ ] サービスの独立デプロイが実証されている

---

## 8. 文化と意思決定 (Culture & Decision Making)

**症状**: 「インシデント後に犯人探しが起きる」「変更レビューが形式化している」「重要な決定の根拠が誰も思い出せない」。

**診断の問い**:
- 直近のインシデント Postmortem は Blameless だったか？
- ADR は書かれているか / 参照されているか？
- 状況に応じて Cynefin の異なる領域として扱えているか？

**処方の系統樹**:

```
Westrum Culture (3類型)
    │
    ├─→ Pathological (病的): 情報隠蔽・責任回避・橋渡し阻害
    │     → DORA調査で Four Keys 最低層と相関
    │
    ├─→ Bureaucratic (官僚的): 縄張り・規則第一
    │
    └─→ Generative (生成的): 協働・学習・橋渡し
          → Four Keys 最高層と相関
          │
          └─→ 育成手段
                ├─ Servant / Host Leadership
                ├─ Blameless Postmortem
                ├─ Psychological Safety
                └─ ADR で「なぜ」を残す

Cynefin (状況分類)
    │
    ├─→ Clear: ベストプラクティス適用
    │
    ├─→ Complicated: 専門家分析 → Good Practice
    │     (ADR 化に値する領域)
    │
    ├─→ Complex: 実験 → Emergent Practice
    │     (VOICE の Experiments 領域)
    │
    └─→ Chaotic: 即時行動 → 安定化後に再分類
          (インシデント対応の初期フェーズ)

Theory of Constraints / Three Ways
    │
    ├─→ Flow: 上流から下流への流れを最適化
    ├─→ Feedback: 下流から上流へ高速フィードバック
    └─→ Continual Learning: 実験・反復・学習の文化化
```

---

## 9. 概念の合流点 — 統合シナリオ

複数概念が **同じ判断に効く** 典型シナリオ。

### シナリオA: 「マイクロサービス化を始めたい」

```
1. Wardley Map で対象領域の進化段階を診断
   → Genesis ならまだ Monolith でよい可能性
   → Commodity なら SaaS 移行のほうが合理的

2. Subdomain Types で Core / Supporting / Generic を分類
   → Core にだけ投資集中

3. EventStorming で Bounded Context 候補を発見

4. Inverse Conway Maneuver で組織再編を先行
   → Stream-aligned Team を Bounded Context 単位に編成

5. Thinnest Viable Platform を Platform Team が用意

6. Fitness Function で「分散モノリス化」を継続検査
   → 例: サービス間循環依存ゼロ
   → 例: サービス間同期呼び出しチェーン3段以下

7. Four Keys で改善トレンドを計測
   → Deployment Frequency が下がっていないか監視
```

### シナリオB: 「変革プロジェクトが頓挫した」

```
1. BVSSH の Outcomes over Outputs で「成果は何だったか」再確認
   → Output ベースだと「リリースしたが成果なし」が見える

2. Westrum 文化スコアを観察
   → Pathological 文化下では構造変更だけでは効かない

3. Three Horizons で投資配分を再点検
   → H1 (現行) の指標で H3 (探索) を評価していないか

4. Cynefin で課題領域を分類
   → Complex 領域に Best Practice を適用していないか

5. Federated Governance + MVC で統制を軽量化
   → 重武装の中央統制が阻害要因か検証

6. Pioneers-Settlers-Town Planners で人員配置を再設計
   → Pioneers に Town Planners の指標を課していないか
```

### シナリオC: 「Four Keys は良くなったが事業成果が上がらない」

```
1. Goodhart's Law を疑う
   → Deploy Frequency が「no-op deploy」で水増しされていないか

2. Flow Framework の Flow Distribution を見る
   → Feature 100% で Tech Debt 0% になっていないか
   → 逆に Defect が多すぎないか

3. SPACE Framework の Satisfaction を計測
   → エンジニア燃え尽きで「速いが続かない」状態か

4. Outcomes over Outputs に立ち返る
   → 計測している Output と、目指す Outcome の接続を見直す
   → North Star Metric を再定義

5. Architecture Characteristic を見直す
   → 顧客に効く特性を計測できていない可能性
```

---

## 10. アンチパターン早見表

| アンチパターン | 症状 | 立ち返るべき概念 |
|---|---|---|
| メトリクス天国 | ダッシュボードが増え意思決定に使われない | Goodhart's Law / Outcomes over Outputs |
| プラットフォーム肥大 | Platform Team が「全部抱え」内部顧客が逃げる | Thinnest Viable Platform / Platform as Product |
| 分散モノリス | サービス分割したのに独立デプロイ不能 | Architecture Quantum / Fracture Plane |
| 永続 Collaboration | すべてのチームが常時 Collab している | 3 Interaction Modes の意図的選択 |
| ビッグバン変革 | 全社一斉切り替えで頓挫 | Strangler Fig / Three Horizons |
| 中央集権統制 | 統制で速度が出ない | Federated Governance / Minimum Viable Compliance |
| Pioneer に SLA | 探索チームに運用指標を課す | Pioneers-Settlers-Town Planners 別指標 |
| Manual Fitness | 人手でのアーキレビューに依存 | Automated Fitness Function 化 |
| ADR 不在 | 過去の決定の根拠が失われ再議論 | Architectural Decision Record |
| Best Practice 万能視 | Complex 領域に Best Practice を持ち込む | Cynefin の領域別アプローチ |

---

## 11. フェーズ2 (SKILL.md 化) への引き継ぎ

この用語集と概念マップを SKILL 化する際の方針案:

1. **トリガー条件**: 「アーキテクチャ・モダナイゼーション」「組織設計」「Conway's Law」「進化的アーキテクチャ」「フィットネス関数」「Four Keys / DORA」「Team Topologies」「BVSSH」などのキーワード。
2. **基本フロー**: ユーザの状況を 8つの問題領域 (このマップの §1〜§8) のどれかに分類 → 該当系統樹から処方候補を提示 → ADR で記録。
3. **出力形式案**: 診断結果 (問題領域) + 処方候補 (3案) + アンチパターン警告 + ADR テンプレート提示。
4. **隣接スキル連携**: `karak-architecture:adr-architect` (記録), `karak-architecture:write-c4-diagram` (可視化), `karak-product:requirements-analyst` (要件接続)。
5. **言語非依存・クラウド非依存** を維持するため、具体的なツール・サービス名（Kubernetes / AWS / Datadog 等）は SKILL 本体には書かない。必要なら別途 references に切り出す。
