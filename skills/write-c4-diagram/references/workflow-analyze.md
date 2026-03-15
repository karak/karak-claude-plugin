# 既存コードベース分析ワークフロー

既存の実装からアーキテクチャ図を起こす手順（リバースエンジニアリング）。
コードが存在する状態で C4 ダイアグラムを作成する場合に使う。

---

## Step 0: コードベース調査（必須、省略不可）

> **なぜ必須か**: コードを読まずに推測で図を書くと、実際の構成と乖離する。
> 特に Component/Code レベルでは、クラス名・関数名・FK 関係をソースから正確に抽出する必要がある。

### 調査対象

| 対象 | 確認するもの |
|---|---|
| バックエンド構造 | ルーティング、Blueprint/Controller、Service 層、Repository 層、ORM モデル |
| フロントエンド構造 | SPA/SSR の種類、主要フレームワーク、API クライアント、認証フロー |
| IaC (Terraform/CDK 等) | デプロイ先、ネットワーク構成、DB、ロードバランサー、シークレット管理 |
| 外部システム連携 | API 呼び出し先、OAuth プロバイダ、メッセージキュー |
| 既存ドキュメント | 設計ドキュメント、既存ダイアグラム |

**調査の進め方:**
- バックエンド・フロントエンド・IaC は**並列で調査**して効率化する（Agent ツールを活用）
- 調査結果を元にレベル間の要素マッピングを計画してから図を書き始める

---

## 4レベルの作成手順（既存コードから）

**必ず上位レベルから順に作成する。** 上位レベルの要素名が下位レベルの参照元になるため、順序を逆転させると名前の不一致が発生する。

### Level 1: System Context

```plantuml
@startuml
!include https://raw.githubusercontent.com/plantuml-stdlib/C4-PlantUML/master/C4_Context.puml

LAYOUT_WITH_LEGEND()

title システム名 - C4 Level 1: System Context

Person(user, "ユーザー名", "説明")
System(system, "システム名", "システムの概要説明")
System_Ext(ext1, "外部システム名", "説明")

Rel(user, system, "動詞", "プロトコル\n補足")
Rel(system, ext1, "動詞", "プロトコル\n補足")

@enduml
```

**L1 チェック:**
- [ ] システムは **1つの `System()`** で表現されている
- [ ] Person が全利用者ロールを網羅している
- [ ] 外部システムは `System_Ext()` で表現されている
- [ ] `Rel()` に動詞とプロトコルが記載されている

### Level 2: Container

```plantuml
@startuml
!include https://raw.githubusercontent.com/plantuml-stdlib/C4-PlantUML/master/C4_Container.puml

LAYOUT_WITH_LEGEND()

title システム名 - C4 Level 2: Container

Person(user, "ユーザー名", "説明")
System_Ext(ext1, "外部システム名", "説明")

System_Boundary(system, "システム名") {
    Container(app, "アプリ名", "技術スタック", "責務の説明")
    ContainerDb(db, "DB名", "技術", "格納データの概要")
}

Rel(user, app, "動詞", "プロトコル")
Rel(app, db, "SQL", "技術詳細")
Rel(app, ext1, "HTTPS", "API呼び出し内容")

@enduml
```

**L2 チェック:**
- [ ] Person と System_Ext が **L1 と同じ名前・説明** で定義されている
- [ ] `System_Boundary` の名前が L1 の `System()` と一致している
- [ ] DB は `ContainerDb()` を使用している
- [ ] 各 Container に技術スタック（第3引数）と責務（第4引数）が記載されている
- [ ] 関係線にプロトコルを明記している

### Level 3: Component

```plantuml
@startuml
!include https://raw.githubusercontent.com/plantuml-stdlib/C4-PlantUML/master/C4_Component.puml

LAYOUT_WITH_LEGEND()

title システム名 - C4 Level 3: Component (対象コンテナ名)

' L2 の他コンテナを外部参照
Container(spa, "SPA名", "技術", "")
ContainerDb(db, "DB名", "技術", "")
System_Ext(ext1, "外部システム名", "")

' 対象コンテナを展開
Container_Boundary(target, "対象コンテナ名") {
    Component(comp1, "コンポーネント名", "技術\nパス", "責務")
    Component(comp2, "コンポーネント名", "技術", "責務")
}

Rel(spa, comp1, "HTTP動詞", "パスパターン")
Rel(comp1, comp2, "呼び出し", "メソッド名()")
Rel(comp2, db, "SQL", "技術詳細")

@enduml
```

**コンポーネントのグルーピング:**
コード構造上のコンポーネント数が多い場合（例: Blueprint が 11 個）、以下の基準で論理グループにまとめる:
- **機能ドメイン** で統合（例: questions + notes + progress → "Learning Blueprint"）
- **利用者ロール** で統合（例: upload + jobs + admin → "Admin Blueprint"）
- **技術レイヤー** で統合（例: health + spa → "Infrastructure Blueprint"）
- 統合した場合は説明文に元のコンポーネント一覧を含め注記を付ける

**L3 チェック:**
- [ ] L2 の他コンテナが **同じ名前** で外部参照として定義されている
- [ ] `Container_Boundary` の名前が L2 の `Container()` と一致している
- [ ] コンポーネントが実際のコードの構造を反映している（Blueprint, Service, Repository 等）
- [ ] レイヤー構造（API → Service → Repository → ORM → DB）が関係線から読み取れる
- [ ] 認証・認可のコンポーネント（JWT Manager, admin_required 等）が含まれている

### Level 4: Code

- C4-PlantUML には Code 用の専用 include がないため、`C4_Component.puml` を流用する
- **最も複雑または重要なコンポーネント** を選んで展開する（全コンポーネントを展開しない）
- ORM モデル、Repository 関数、パイプラインノード等が典型的な対象

**L4 チェック:**
- [ ] L3 のコンポーネントが外部参照として定義されている
- [ ] クラス属性・メソッド名がソースコードと一致している
- [ ] FK 関係の ondelete 挙動 (CASCADE, SET NULL) が正確に記載されている
- [ ] nullable カラムが明示されている

---

## コードベースからの要素抽出ガイド

### バックエンド (Python/Flask 例)

| 抽出対象 | ソース | C4 要素 |
|---|---|---|
| Blueprint 一覧 | `app.py` の `register_blueprint()` | L3 Component |
| Service クラス | `services/` ディレクトリ | L3 Component |
| Repository/DAO | `db/repository.py` | L3 Component |
| ORM モデル | `db/models.py` | L4 Component |
| 外部 API クライアント | import / 設定ファイル | L2 System_Ext |

### フロントエンド (React 例)

| 抽出対象 | ソース | C4 要素 |
|---|---|---|
| SPA 全体 | `package.json` + `vite.config.ts` | L2 Container |
| API クライアント | `api/` ディレクトリ | L3 Component（必要時） |
| SSR テンプレート | `templates/` ディレクトリ | L2 Container（別コンテナとして、注記付き） |

### IaC (Terraform 例)

| 抽出対象 | ソース | C4 要素 |
|---|---|---|
| Cloud Run / ECS | `main.tf` | L2 Container（実行環境） |
| RDS / Cloud SQL | `database.tf` | L2 ContainerDb |
| Load Balancer | `loadbalancer.tf` | L1 or L2（境界に配置） |
| Secret Manager | `secrets.tf` | L2 Container |
| VPC / Network | `networking.tf` | Rel のラベルに反映 |

---

## ファイル命名規約

```
docs/design/c4-context.puml          # Level 1
docs/design/c4-container.puml        # Level 2
docs/design/c4-component.puml        # Level 3
docs/design/c4-code.puml             # Level 4
```

複数の Component/Code 図がある場合:
```
docs/design/c4-component-flask-api.puml
docs/design/c4-component-pipeline.puml
docs/design/c4-code-orm-models.puml
```

---

## チェックリスト（既存コード分析）

### 着手前
- [ ] コードベース調査 (Step 0) を実施したか
- [ ] 作成するレベルを明確にしたか（全4レベル or 特定レベルのみ）
- [ ] 既存のアーキテクチャ文書やダイアグラムを確認したか

### 作業中
- [ ] 上位レベルから順に作成しているか (Context → Container → Component → Code)
- [ ] 各レベルで正しい `!include` を使用しているか
- [ ] `LAYOUT_WITH_LEGEND()` と `title` を全図に含めているか
- [ ] 要素の全引数 (id, 名前, 技術, 説明) を埋めているか
- [ ] `Rel()` にプロトコル/技術を明記しているか
- [ ] Person, System_Ext の名前がレベル間で一致しているか

### 完了時
- [ ] レベル間のズームイン整合性を検証したか（`references/consistency-rules.md` を参照）
- [ ] ソースコードと照合し、Blueprint/Model/FK 関係が正確か
- [ ] 外部参照の漏れがないか（L2 のコンテナが L3 に全て出現するか）
- [ ] PlantUML 構文が有効か（引数の数、include パス、Boundary のラベル）
