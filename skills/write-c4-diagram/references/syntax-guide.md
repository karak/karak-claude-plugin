# PlantUML C4 構文ガイド

## 必須ヘッダー

```plantuml
' include は GitHub raw URL を使用（ローカルパスは不可）
!include https://raw.githubusercontent.com/plantuml-stdlib/C4-PlantUML/master/C4_Context.puml
!include https://raw.githubusercontent.com/plantuml-stdlib/C4-PlantUML/master/C4_Container.puml
!include https://raw.githubusercontent.com/plantuml-stdlib/C4-PlantUML/master/C4_Component.puml

LAYOUT_WITH_LEGEND()          ' 凡例を表示（必須）
' LAYOUT_LEFT_RIGHT()         ' 左→右レイアウト（任意、要素が多い場合に有効）

title システム名 - C4 Level N: レベル名
```

## 要素の引数一覧

| 関数 | 引数数 | 例 |
|---|---|---|
| `Person(id, "名前", "説明")` | 3 | `Person(user, "学習者", "英語を学ぶ一般ユーザー")` |
| `System(id, "名前", "説明")` | 3 | `System(sys, "学習システム", "英語短文学習を提供")` |
| `System_Ext(id, "名前", "説明")` | 3 | `System_Ext(api, "Gemini API", "文章生成・評価を提供")` |
| `System_Boundary(id, "名前")` | 2 | `System_Boundary(sys, "学習システム")` |
| `Container(id, "名前", "技術", "説明")` | 4 | `Container(app, "Flask API", "Python/Flask", "REST API を提供")` |
| `ContainerDb(id, "名前", "技術", "説明")` | 4 | `ContainerDb(db, "メインDB", "PostgreSQL", "ユーザーと学習データを格納")` |
| `Container_Boundary(id, "名前")` | 2 | `Container_Boundary(api, "Flask API")` |
| `Component(id, "名前", "技術\nパス", "説明")` | 4 | `Component(bp, "Auth Blueprint", "Flask Blueprint\napi/auth.py", "認証・セッション管理")` |
| `Rel(from, to, "ラベル", "技術/補足")` | 4 | `Rel(app, db, "読み書き", "SQLAlchemy ORM")` |

## よくある構文エラー

| エラー | 原因 | 修正 |
|---|---|---|
| `!include C4_Container.puml` | パスが不完全 | GitHub raw URL を使用 |
| `System_Boundary(id)` | 第2引数（ラベル）が不足 | `System_Boundary(id, "名前")` を追加 |
| `Container(id, "名前")` | 第3・第4引数が不足 | 技術と説明を追加 |
| `Component(id, "名前")` | 第3・第4引数が不足 | 技術（パス含む）と説明を追加 |
| レンダリング時に要素が重なる | レイアウト未指定 | `LAYOUT_WITH_LEGEND()` を追加 |
| 関係線のラベルが空 | `Rel(a, b, "uses")` で済ませる | 動詞 + プロトコル/技術を明記 |

## Rel のプロトコル例

```plantuml
Rel(user, spa, "閲覧・操作", "HTTPS")
Rel(spa, api, "API呼び出し", "HTTPS / JSON REST")
Rel(api, db, "データ読み書き", "SQL (SQLAlchemy)")
Rel(api, gemini, "文章生成・評価", "HTTPS / REST")
Rel(api, spa, "SSE ストリーミング", "Server-Sent Events")
Rel(worker, queue, "ジョブ取得", "AMQP")
```

## グルーピング構文（L3 Component で有用）

```plantuml
' パッケージ境界を示す（C4 公式構文ではないが視認性が上がる）
together {
    Component(service1, ...)
    Component(service2, ...)
}
```
