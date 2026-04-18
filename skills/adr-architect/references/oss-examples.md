# OSS プロジェクトにおける ADR の実例集

大規模 OSS プロジェクトがどのように設計判断を記録・管理しているかの実例。
ADR のベストプラクティスを学ぶための参照資料。

---

## 1. Kubernetes Enhancement Proposals (KEPs)

### 概要

Kubernetes における意思決定の中心は KEP (Kubernetes Enhancement Proposal) である。
KEP は提案のライフサイクルを厳密に管理し、Goals/Non-Goals でスコープ境界を明示する。

### KEP のライフサイクル

```
Provisional → Implementable → Implemented
     ↓              ↓
  Deferred      Withdrawn
```

| ステータス | 意味 |
|-----------|------|
| **Provisional** | アイデアが受け入れられ、SIG がスポンサーとなった |
| **Implementable** | 設計が承認され、実装可能な状態 |
| **Implemented** | 実装が完了し、リリースに含まれた |
| **Deferred** | 保留中。将来再検討される可能性がある |
| **Withdrawn** | 提案者が取り下げた |

### KEP テンプレートの構造

```markdown
# KEP-NNNN: タイトル

## Summary
[1段落の要約]

## Motivation
### Goals
- [達成したいこと 1]
- [達成したいこと 2]

### Non-Goals
- [意図的に対象外とすること 1]
- [意図的に対象外とすること 2]

## Proposal
### User Stories
#### Story 1
[ユーザーストーリー]

### Risks and Mitigations
[リスクとその軽減策]

## Design Details
### Test Plan
[テスト計画]

### Graduation Criteria
#### Alpha
- [Alpha 段階の基準]
#### Beta
- [Beta 段階の基準]
#### GA (General Availability)
- [GA 段階の基準]

## Alternatives
[検討した代替案とその却下理由]
```

### ADR への応用ポイント

1. **Goals / Non-Goals パターン**: ADR に「この決定が解決しないこと」を明示することで、スコープクリープを防止
2. **Graduation Criteria**: 段階的なロールアウト計画を ADR に含めることで、リスクを管理
3. **User Stories**: 抽象的な要件を具体的なシナリオに落とし込む

### 実例: KEP-4639 (OCI Volume Source)

```markdown
## Goals
- Allow Pod authors to reference OCI artifacts as volume sources directly
- Support read-only mounting of OCI images as volumes

## Non-Goals
- Providing write access to OCI volumes
- Supporting non-OCI image formats
- Providing a generic plugin interface for volume sources
```

**学べること**: Non-Goals を明記することで、レビュアーと提案者の期待値を一致させている。

### 参考リンク
- KEP Process: https://github.com/kubernetes/enhancements/blob/master/keps/sig-architecture/0000-kep-process/README.md
- KEP Template: https://github.com/kubernetes/enhancements/tree/master/keps/NNNN-kep-template

---

## 2. Rust RFC (Request for Comments) プロセス

### 概要

Rust コミュニティは言語設計のあらゆる重要な変更を RFC として管理する。
RFC は「Drawbacks（欠点）」と「Prior Art（先行事例）」を必須セクションとして要求し、
議論の透明性を極限まで高めている。

### RFC テンプレートの構造

```markdown
# Feature Name

- Feature Name: (RFC のファイル名, e.g. my_awesome_feature)
- Start Date: (YYYY-MM-DD)
- RFC PR: [rust-lang/rfcs#0000](https://github.com/rust-lang/rfcs/pull/0000)
- Tracking Issue: [rust-lang/rust#0000](https://github.com/rust-lang/rust/issues/0000)

## Summary
[1段落の説明]

## Motivation
[なぜこれを行うべきか？どのユースケースをサポートするか？
期待される成果は何か？]

## Guide-level explanation
[この提案を初めて知る Rust プログラマーに説明するかのように。
概念の導入とその使い方を具体例で説明する。]

## Reference-level explanation
[技術的な詳細。言語との相互作用、エッジケース、
実装の詳細を記述する。]

## Drawbacks
[なぜこれを行うべきでないか？]

## Rationale and alternatives
- なぜこの設計が可能な設計空間の中で最良なのか？
- どのような代替設計が検討されたか、なぜ選ばなかったのか？
- この提案を採用しないことの影響は何か？

## Prior art
[他の言語やフレームワークでの類似実装を議論する。
成功例と失敗例の両方を含める。]

## Unresolved questions
[RFC プロセス中に解決すべき未解決の設計問題。
実装中に解決される予定の問題。
将来の拡張として扱われる関連問題。]

## Future possibilities
[将来のこの RFC の拡張について。]
```

### ADR への応用ポイント

1. **Drawbacks（欠点）セクション**: ADR に「この決定の弱点」を正直に記述する文化を促進
2. **Prior Art（先行事例）**: 他のプロジェクトや業界での類似判断を調査・参照する習慣
3. **Guide-level vs Reference-level**: 読者のレベルに応じた説明の階層化
4. **Unresolved Questions**: 今回は解決しないが将来取り組むべき課題の明示

### 実例: RFC 2532 (Associated Type Defaults)

```markdown
## Drawbacks

This introduces another way for trait defaults to cause surprising behavior
when changed. If a trait author adds or changes an associated type default,
it could silently change behavior for implementors who rely on the default.

## Prior art

- Haskell: Type families with defaults
- C#: Default interface methods (partial overlap)
- Scala: Abstract type members with defaults
```

**学べること**: 「なぜやるべきでないか」を最初に考えることで、判断の堅牢性が高まる。

### 参考リンク
- Rust RFC Repository: https://github.com/rust-lang/rfcs
- RFC Template: https://github.com/rust-lang/rfcs/blob/master/0000-template.md

---

## 3. Spotify Backstage — プラットフォーム ADR

### 概要

Spotify が主導する Backstage プロジェクトでは、ADR を `/docs/architecture-decisions/` に集約し、
プラットフォームの核心的な設計判断を記録している。ドメインモデル（Entity Model）の定義などが含まれる。

### Backstage ADR テンプレート

```markdown
---
id: adrNNN
title: [short title]
status: [proposed | accepted | deprecated | superseded]
date: [YYYY-MM-DD]
---

# ADR-NNN: [short title]

## Context

[description of the problem and context]

## Decision

[description of the decision]

## Consequences

[description of the consequences, both positive and negative]
```

### 実例: ADR-005 Catalog Core Entity Types

Backstage の最も重要な ADR の一つで、カタログのコアエンティティモデルを定義している。

```markdown
# ADR005: Catalog Core Entity Types

## Context

The catalog needs to model the software ecosystem in a way that is both
general enough to cover many organizations' needs, and specific enough
to be useful out of the box.

## Decision

We define the following core entity types:

- **Component**: A piece of software (service, website, library, etc.)
- **API**: A boundary between components, exposing functionality
- **Resource**: Physical or virtual infrastructure (database, S3 bucket, etc.)
- **System**: A collection of components and resources that form a product
- **Domain**: A grouping of systems that share business purpose
- **Group**: A team or organizational unit
- **User**: A person
- **Location**: A reference to external data sources
- **Template**: A scaffolding template
- **Type**: Entity categorization within each kind

## Consequences

- All entities share a common metadata structure (apiVersion, kind, metadata, spec)
- Organizations can extend with custom entity types
- The type system is deliberately loose to accommodate diverse organizational structures
- Tools and plugins can rely on these core types for interoperability
```

### ADR への応用ポイント

1. **ドメインモデルの ADR**: 組織の共通語彙（Ubiquitous Language）を ADR で定義する
2. **拡張性の設計**: 「コアは固定、拡張は自由」という設計哲学を ADR で明示
3. **簡潔さ**: Backstage の ADR は非常に簡潔で、必要最小限の情報に集中している

### 参考リンク
- Backstage ADRs: https://github.com/backstage/backstage/tree/master/docs/architecture-decisions
- ADR Template: https://github.com/backstage/backstage/blob/master/docs/architecture-decisions/adr000-template.md

---

## 4. Apache プロジェクト — メーリングリストからの知識抽出

### 概要

Apache プロジェクト（Cassandra, Hadoop 等）では、意思決定の **89%** がメーリングリスト上で行われている（Freiburg大学の研究より）。メーリングリストは ADR の「源泉データ」として最も豊富だが、抽出難易度が高い。

### メーリングリストからの ADR 抽出パイプライン

```
1. テーマ分析（Thematic Analysis）
   └→ どのメールがアーキテクチャに関連しているかを分類

2. 引用関係の追跡
   └→ メール間の引用関係から論理的な合意形成のタイムラインを再構成

3. 合意ポイントの特定
   └→ 「+1」「LGTM」「I agree」等のシグナルから合意に達した箇所を特定

4. ADR への変換
   └→ 合意された設計判断を Nygard or MADR 形式に変換
```

### AI による抽出のプロンプト例

```
以下のメーリングリストのスレッドを解析してください。
このスレッドでは [トピック] が議論されています。

1. アーキテクチャに関連する意思決定ポイントを特定してください
2. 最終的な合意事項を特定してください
3. 却下された代替案とその理由を特定してください
4. 以上を Nygard 形式の ADR ドラフトに変換してください
```

### 参考リンク
- Freiburg 大学研究論文: "Exploring the Rationale of Design Decisions in Open-Source Software Mailing Lists"
  https://fse.studenttheses.ub.rug.nl/28569/

---

## 5. GitHub Discussions からの ADR 生成

### 概要

GitHub Discussions は Issue よりも自由な形式で設計アイディアが交わされる場。
AI を用いて、合意形成の推移を ADR に変換する手法。

### 抽出のシグナル

| シグナル | 強度 | 活用方法 |
|---------|------|---------|
| **Answer としてマークされた投稿** | 高 | 意思決定の結論として採用 |
| **多くの Upvote を集めた投稿** | 中〜高 | コミュニティの合意を示す |
| **メンテナーによるコメント** | 高 | 最終的な判断として重視 |
| **反対意見とその反論** | 中 | 代替案と却下理由として活用 |
| **コードスニペットの共有** | 中 | 実装の具体例として ADR に含める |

### AI によるプロンプト例

```
以下の GitHub Discussion スレッドを解析してください:

1. 最終的な合意事項（特に Answer マークされた投稿）を特定
2. 検討された代替案とその却下理由を抽出
3. 技術的なトレードオフの議論を整理
4. MADR 形式の ADR ドラフトを生成
```

---

## データソース別の特性比較

| ソース | 含まれる知識 | 抽出シグナル強度 | AI 抽出の課題 |
|--------|------------|----------------|--------------|
| **GitHub Discussions** | 比較、合意、代替案 | 中〜高 | 議論の散漫さ、ノイズ |
| **メーリングリスト** | 歴史的背景、深い洞察 | 低（抽出難易度高） | スレッド追跡、古い文脈 |
| **GitHub Issues** | バグ、制約、修正履歴 | 中 | AD との判別が困難 |
| **Stack Overflow** | 特定課題の解決策 | 高 | 文脈の欠如 |
| **Research Papers** | 抽象化された理論 | 高 | 実装への橋渡し |
| **Design Docs** | 設計意図、代替案 | 非常に高 | 社内文書のためアクセス困難 |

---

## ツールエコシステム

ADR 管理を支援するツール群:

| ツール | 言語 | 機能 | リンク |
|--------|------|------|--------|
| **adr-tools** | Bash | ADR の作成・一覧・ステータス変更 | https://github.com/npryce/adr-tools |
| **adrust** | Rust | ADR 管理のCLI | https://github.com/omallassi/adrust |
| **log4brains** | JS | ADR → 静的 Web サイト変換 | https://github.com/thomvaill/log4brains |
| **git-adr** | Shell | Git notes ベースの ADR 管理 | https://github.com/zircote/git-adr |
| **Decision Guardian** | YAML | PR と ADR の自動紐付け | https://github.com/DecispherHQ/decision-guardian |
