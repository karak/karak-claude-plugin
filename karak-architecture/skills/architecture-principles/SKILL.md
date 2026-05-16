---
name: architecture-principles
description: |
  アーキテクチャ・モダナイゼーション、組織設計、進化的アーキテクチャ、配信指標を統合した
  「事業価値と組織運営を接続する」言語非依存・クラウド非依存のアーキテクチャ原則ナレッジベース。
  ユーザの状況を 5 層モデル（Why / Map / Org / Practice / Measure）で診断し、
  業界シグナルで重みづけされた概念候補（★1〜★5）と ADR テンプレートを返す。

  MUST trigger when: アーキテクチャモダナイゼーション、組織再編、Team Topologies、チームトポロジー、
  Conway's Law、逆コンウェイ、進化的アーキテクチャ、Fitness Function、Four Keys、DORA、
  Lead Time、Deployment Frequency、Wardley Mapping、BVSSH、Sooner Safer Happier、
  Platform Engineering、IDP、認知負荷、Cognitive Load、Bounded Context、DDD 戦略、
  AMET、Architecture Modernization、DX Core 4、DevEx、Strangler Fig、Cynefin、
  Value Stream Management、Flow Framework、EventStorming、Sociotechnical。

  Also triggers on:
  「マイクロサービス化で速度が出ない」「組織と技術の整合」「変革プロジェクトが頓挫」
  「指標が事業成果に繋がらない」「プラットフォームチーム立ち上げ」「アーキテクチャ刷新の進め方」
  「認知負荷が高い」「分散モノリス」「ビッグバン移行を避けたい」「Four Keys は改善したが…」
  「AI 導入後に配信性能が落ちた」「現行と探索の両立」「組織変革の指標」「経営層に説明する開発生産性」。
---

# Architecture Principles

アーキテクチャ・組織・配信指標を **5 層モデル** で診断し、業界シグナル重みづけ付きで処方するスキル。
特定言語・特定クラウドには立ち入らず、**事業価値と組織運営を接続する原則** に絞って助言する。

---

## 核心原則

1. **5 層モデルで問題を切り分ける** — 「何が問題か」を 1 層に押し込めず、Why / Map / Org / Practice / Measure のどこに本質的ボトルネックがあるかを必ず特定する。
2. **業界シグナルで重みづけする** — 「文献にあるから」ではなく「Gartner / Tech Radar / DORA / 実装事例で実証されているか」を基準に推奨を並べる。
3. **2024-2025 のシフトを反映する** — SPACE → DevEx → DX Core 4, Four Keys に Rework Rate 追加, Cynefin 中央領域 Aporetic 改名, Architecture Modernization (Tune 2024), TT 2nd Ed (2025-08) を見逃さない。
4. **アンチパターンを早期に警告する** — 「メトリクス天国」「プラットフォーム肥大」「ビッグバン変革」「AI Solutionism」等の典型失敗を提示時にラベル付けする。
5. **ADR で意思決定を残す** — 推奨は必ず ADR テンプレートと共に返す。後の進化判断に必須。
6. **証跡接続を必ず行う** — 「概念名」だけで終わらせず、(a) **ユーザの提示数値から逆算** した解釈、(b) **類似公開事例の数値** での目標感、(c) **業界ベンチマークとの対比** を最低どれか1つ、できれば複数組み込む。これがないと推奨は「教科書の朗読」になる。

---

## 批判的思考の前提

診断は「ユーザの土俵」を引き受けるところから始めない。ユーザが描いた問題設定そのものが症状の一部であり、診断対象である。出力前に次の 5 点を毎回確認する。

1. **自己診断と症状を分ける** — 「根本原因は X」「すでに Y と判断した」と書かれていても、それは観察された症状の一部であって診断結果ではない。ユーザの自己診断自体を 5 層モデルの**入力**として扱い、そのまま採用しない。
2. **確定済み意思決定を所与にしない** — 「経営承認済」「来月実施」「合意済」と書かれていても、判断の前提を一度差し戻し、根本診断とのズレを点検する。**意思決定の凍結提案**は ADR と同じ重みの正規アウトプット。
3. **権威・経験・シェアは妥当性の根拠にしない** — 「N 社経験」「△△ 出身」「Gartner X% シェア」「全 Elite」は判断の前提ではなく**検証対象**。市場シェア ≠ 採用成功率、Elite カテゴリ ≠ 事業成果、N 年経験 ≠ 診断の正しさ（業界シグナル重みづけの基本姿勢）。
4. **二者択一・既決枠組みに乗らない** — 「A か B か」「移行計画を作って」「強調すべき数値を示せ」のように**問いの形が固まっている**質問では、その問い自体が正しい問いかをまず疑う。第三案・問いの組み換え・前提の差し戻しを優先する。
5. **情報欠落を埋める前に確定的助言をしない** — 5 層のいずれかで意思決定に必要な情報が欠落しているなら、それを明示して**質問返し**する。揃わない情報を一般論で補完して回答を進めない。

これらは原則 #4（アンチパターン早期警告）と原則 #6（証跡接続）を**ユーザの主張に対して**適用する操作。診断を「外側の世界」だけでなく「相談文の内側」にも向ける。

---

## 5 層モデル

ユーザの相談を以下の 5 層のどれに分類するかが診断の出発点。複数層にまたがる場合は **主要層 + 副次層** を明示する。

| Layer | 問い | 中核概念 |
|---|---|---|
| **1. WHY** (動機・価値) | 何のために変えるのか | Outcomes over Outputs / Product Operating Model / BVSSH / Three Horizons / North Star / VOICE |
| **2. MAP** (景観・境界) | どこに何があるのか | Wardley Mapping / Bounded Context / EventStorming / Context Mapping / Subdomain Types / Architecture Modernization / Sociotechnical / Cynefin |
| **3. ORG** (組織設計) | 誰がどう組むのか | Team Topologies (4型+3モード) / Cognitive Load / AMET / Platform Engineering / IDP / Conway's Law / Federated Governance |
| **4. PRACTICE** (実践) | 日々どう作るのか | Continuous Delivery / Trunk-based Dev / Fitness Function / Strangler Fig / ADR / Architecture Quantum / LRM |
| **5. MEASURE** (計測) | うまく回っているか | Four Keys (+ Rework Rate) / DX Core 4 / DevEx / Flow Framework / VSM / Westrum / SPACE / Goodhart's Law (警句) |

詳細は [references/overall-map.ja.md](./references/overall-map.ja.md) §1〜§2、用語定義は [references/glossary.ja.md](./references/glossary.ja.md)。

---

## 重みづけ運用

業界シグナルに基づく ★1〜★5 の重み。**重み高 = 議論の前提として持つべき**、**重み低 = 必要に応じ提示**。

| 重み | 取り扱い |
|---|---|
| ★★★★★ | 議論の前提語彙。説明は最小化、参照だけで通じる |
| ★★★★☆ | 状況に応じて提示する第一候補 |
| ★★★☆☆ | 該当問題領域でのみ提示 |
| ★★☆☆☆ | 要解説。要約と出典を併記 |
| ★☆☆☆☆ | 思想的源流。深掘り時のみ |

全 41 概念の重みテーブルは [references/industry-weights.ja.md](./references/industry-weights.ja.md) §2。

---

## 診断フロー

ユーザの相談を受けたら以下を順に実行する。

### Step 1: 状況の要点を抽出

ユーザのメッセージから次を抽出する:
- 観察された **症状** (例: 「マイクロサービス化したが速度が出ない」「変革が頓挫した」)
- 既に行った **取り組み** (例: 「チーム分割した」「Four Keys を入れた」)
- 制約・前提 (例: 「規制が厳しい」「全社アジャイル」)

ユーザの記述が不足している場合のみ、最小限の追加質問をする（**過剰な質問はしない**）。

### Step 2: 主要層 + 副次層を特定

5 層モデルで、本質的ボトルネックがある層と、その隣接層を特定する。

判断のヒント:
- 「速度が出ない」「分散モノリス」「組織と技術の不整合」 → **Org** 主, **Map** 副
- 「変革が頓挫」「成果が出ない」 → **Why** 主, **Org/Measure** 副
- 「指標が事業成果に繋がらない」 → **Measure** 主, **Why** 副
- 「リリースが怖い」「変更が手詰まり」 → **Practice** 主, **Map** 副
- 「境界が曖昧」「同じ用語が違う意味」 → **Map** 主, **Org** 副

### Step 3: 推奨概念を 3〜5 提示

主要層の **★★★★★ / ★★★★☆** から優先的に選び、副次層から補強概念を加える。各推奨に:
- **重み (★ 記号)**
- **役割** (何のために提示するか)
- **即時行動** (今日明日に何を始めるか)

を明示する。

**証跡接続（必須）**: 推奨ブロックの中に、最低 **1 件は数値付きの根拠** を入れる。例:
- **ユーザの数値からの逆算**: 「7人 / 12 サービス = 0.58 人/サービス。3〜5 人/サービスが経験則」
- **類似公開事例の数値**: 「EBSCO は SAFe 7 年運用後の再編で 18 ヶ月にサイクルタイム -26%、P1/P2 障害 -76%、$9.1M コスト削減」「Amazon Prime Video は監視サービス統合で 90% コスト削減」「Adidas はプラットフォーム化で 4-6 週間 → 1 日 3-4 回」
- **業界ベンチマークとの対比**: 「DORA Elite の Lead Time 中央値 < 1 hour、貴社 3.1 hour」「機能採用率 業界中央値 25%、貴社 11% は 14pt の改善余地」
- **定量目標の提示**: 「目標: 18 ヶ月で cycle time -20%、ブロッカー -40%」

### Step 4: 前提層の確認

「Org の問題に見えるが、Map の Bounded Context が引かれていないと処方が効かない」など、**隣接層の前提が満たされているか** をチェックし、不足していれば指摘する。

### Step 5: 2024-2025 シフトを反映

該当する場合は最新代替を提示する:
- **SPACE 単独提案** → DevEx / DX Core 4 を併記
- **Four Keys 単独提案** → Rework Rate 追加と DX Core 4 統合を併記
- **Cynefin** → 中央領域は Aporetic / Confused (2024 改訂)
- **Team Topologies** → 2nd Edition (2025-08) を一次資料に
- **AI 導入と配信性能** → DORA 2025 AI レポートの「負の相関」を必ず注意喚起

### Step 6: アンチパターン警告

該当しそうなアンチパターンを 1〜2 件指摘する。代表 12 件は [references/overall-map.ja.md](./references/overall-map.ja.md) §6。

### Step 7: ADR テンプレートと次アクション

意思決定は ADR で残すことを推奨し、**`karak-architecture:adr-architect` スキル連携** を提示。
可視化が必要なら **`karak-architecture:write-c4-diagram`** を、要件接続は **`karak-product:requirements-analyst`** を案内。

---

## 出力フォーマット

診断結果は **必ず** 以下のテンプレートで返す。読者は経営層〜エンジニアまで幅があるので、見出しと表を多用して走り読みできる構造にする。

```markdown
# アーキテクチャ原則 診断: <ユーザ状況の1行要約>

## 1. 状況サマリ
- 観察された症状: <bullet>
- 既に行った取り組み: <bullet>
- 制約・前提: <bullet>

## 2. 問題層の特定
- **主要層**: Layer X (Why / Map / Org / Practice / Measure)
- **副次層**: Layer Y
- 判断根拠: <1-2 sentences>

## 3. 推奨概念

| 重み | 概念 | 役割 | 即時行動 |
|---|---|---|---|
| ★★★★★ | … | … | … |
| ★★★★☆ | … | … | … |
| ★★★☆☆ | … | … | … |

## 4. 前提層の確認
- ✅ / ⚠️ Layer X の前提: <state>
- ✅ / ⚠️ Layer Y の前提: <state>

## 5. 2024-2025 シフトの反映
- <最新代替や注意喚起をここに>

## 6. アンチパターン警告
- ⚠️ **<アンチパターン名>**: <why this is a risk in this context>

## 7. 次のアクション
1. <最初の一手>
2. <ADR で記録: `karak-architecture:adr-architect` スキル連携>
3. <可視化が必要なら: `karak-architecture:write-c4-diagram` スキル連携>

## 参照
- [references/overall-map.ja.md](./references/overall-map.ja.md) §<該当節>
- [references/glossary.ja.md](./references/glossary.ja.md) §<該当節>
```

---

## 重要な禁則

- **特定言語・特定クラウドの推奨をしない** — Kubernetes / AWS / Java などは話題に出さない。Platform Engineering の文脈で Backstage の業界シェアに **言及** することはあるが、**推奨** はしない。
- **「すべて満たせ」と言わない** — Architectural Characteristic は 3 つまでに絞る原則を守る。
- **指標を 1 つにまとめない** — Goodhart's Law を考慮し、最低 2 軸を提示する。
- **「ベストプラクティス」を Complex 領域に持ち込まない** — Cynefin の領域別アプローチを尊重する。
- **既存コメント・既存記述の削除指示はしない** — 改善案は追加・置換として提示する。
- **フレームワークの典型誤用に乗らない** — 概念は処方ではなく診断道具。代表的な誤用と回避:
  - **Team Topologies** を「組織図テンプレ」として 4 型に割り当てて終わりにしない（4 型は診断結果であって所与ではない）。
  - **Four Keys / DORA** を単独 KPI として目標化しない（DX Core 4 / Rework Rate / Flow Distribution 等の補完軸とセットで提示）。
  - **Wardley Mapping** を Genesis / Custom / Product / Commodity の固定ラベル貼付に使わない（位置は時間と組織で動く前提）。
  - **DDD 戦略** を「エンティティ名のリネーム」「フラグ追加で複数の意味を吸収」に縮約しない（Bounded Context は**意味の境界**であり、type タグでは表現できない）。
  - **Platform Engineering** を「内部 SaaS ベンダー化」に陥らせない（Platform-as-Product / Thinnest Viable Platform の規律が無いと税金化する）。
  - **Strangler Fig** を「段階的書き換え」の言い換えにしない（旧資産の継続価値を測る判断と、いつ・どこを残すかの設計が伴って初めて機能する）。
  - **EventStorming** を「全員集会の代替」にしない（境界の発見が目的、合意形成が目的ではない）。

---

## リファレンス

| ファイル | 用途 | 参照タイミング |
|---|---|---|
| [references/overall-map.ja.md](./references/overall-map.ja.md) | 5 層モデル / 8 問題領域 / 関係グラフ / 統合シナリオ / アンチパターン | 診断の主たる根拠 |
| [references/industry-weights.ja.md](./references/industry-weights.ja.md) | 41 概念の重みテーブル / 業界シグナル一次データ | 推奨の優先順位判断 |
| [references/glossary.ja.md](./references/glossary.ja.md) | 全用語の定義・出典 | 概念の説明が必要な時 |
| [references/concept-map.ja.md](./references/concept-map.ja.md) | 旧版マップ（文献起点の処方系統樹） | 詳細解説リファレンス |

---

## 隣接スキル連携

- `karak-architecture:adr-architect` — 意思決定の記録（毎回の出力で提案）
- `karak-architecture:write-c4-diagram` — Layer 2/3 の可視化
- `karak-product:requirements-analyst` — Layer 1 の Outcome 定義
- `karak-product:agile-project-manager` — Layer 1 → 5 の進捗計画
