# Drizzle ORM + better-sqlite3: await の問題と Express 5 エラーハンドリング

## 結論

**問題あり。** `await` は不要なだけでなく、Express 5 のエラーハンドラにエラーが届かない原因になる。

---

## 1. better-sqlite3 は同期 API である

`better-sqlite3` は名前の通り、**すべての操作が同期（synchronous）**で完了する。  
Promise を返さず、`await` できるオブジェクトも返さない。

| ドライバ | 実行モデル | 戻り値 |
|---|---|---|
| `better-sqlite3` | 同期 | 生の値（配列・オブジェクト・undefined） |
| `node-postgres` (pg) | 非同期 | `Promise` |
| `mysql2` | 非同期 | `Promise` |

Drizzle ORM は接続しているドライバに合わせて動作を変える。  
`drizzle(betterSqlite3Database, ...)` で初期化した場合、クエリビルダメソッドは **Promise を返さない**。

### `.all()` と `.get()` の戻り値（better-sqlite3 使用時）

```ts
// better-sqlite3 バインド時の実際の型
db.select().from(todos).all()      // → Todo[]          (Promise ではない)
db.insert(todos).values(...).returning().get()  // → Todo | undefined (Promise ではない)
```

---

## 2. `await` を付けるとどうなるか

JavaScript では **`await` は非 Promise 値に適用しても即座にその値を返す**。  
`await 42` は `42` と同じであり、エラーにはならない。

```ts
const todos = await db.select().from(todos).all()
// await は同期値に対して no-op なので、todos には正しく Todo[] が入る
// → 通常ケースでは "動いているように見える"
```

**問題はエラー発生時**に現れる。

---

## 3. Express 5 のエラーハンドラに届かない理由

### Express 5 の非同期エラー処理の仕組み

Express 5 は `async` なルートハンドラが返す Promise の rejection を自動的に捕捉し、`next(err)` に転送する。これが Express 4 との最大の違いであり、Express 5 の主要な改善点の一つである。

```ts
// Express 5: async ルートで throw するとエラーハンドラに届く
app.get('/todos', async (req, res) => {
  throw new Error('DB error')  // → 自動的に next(err) される
})
```

### better-sqlite3 のエラーは同期例外として throw される

`better-sqlite3` はエラーを Promise rejection ではなく **同期 throw** で通知する。

```ts
// better-sqlite3 内部の動作イメージ
function all() {
  // ...
  throw new SqliteError('SQLITE_CONSTRAINT: ...')  // 同期 throw
}
```

### `await` を付けた場合の問題

```ts
app.get('/todos', async (req, res) => {
  const todos = await db.select().from(todos).all()
  //                    ^^^^^^^^^^^^^^^^^^^^^^^^
  // この行が同期 throw した場合、どうなるか？
})
```

`await expr` の評価順序：

1. `expr`（= `db.select().from(todos).all()`）を**同期的に評価・実行**する
2. もし `expr` の評価中に同期例外が throw された場合...
   - **`await` の前に例外が発生**するため、Promise rejection には変換されない
   - `async` 関数のなかでも、`await` 式の右辺を評価する前段階で throw が起きると、その例外は `async` 関数の返す Promise の rejection として包まれる

実際には、`async` 関数の本体内で発生した同期例外はすべて自動的に Promise rejection に変換される（JavaScript の仕様上）。

**ではなぜ届かないのか？**

問題は `await` の有無ではなく、**コードの書き方のパターン**による。

#### パターン A: try/catch で握りつぶしている場合

```ts
app.get('/todos', async (req, res) => {
  try {
    const todos = await db.select().from(todos).all()
    res.json(todos)
  } catch (e) {
    console.error(e)
    // next(e) を呼ばずに終わっている → エラーハンドラに届かない
  }
})
```

#### パターン B: コールバックスタイルと混在している場合

```ts
// Express 4 スタイルの名残
app.get('/todos', (req, res, next) => {
  // 通常の関数（非 async）の中で同期例外を throw しても next(err) には届かない
  // （Express 4 では手動で next(err) を呼ぶ必要がある）
  const todos = db.select().from(todos).all()  // ここで throw されても...
  // next が呼ばれない
})
```

#### パターン C: `await` が本質的問題を隠す

```ts
app.get('/todos', async (req, res) => {
  // better-sqlite3 は同期なので、await は意味的に不要
  // しかし await があっても async 関数内なので例外は Promise rejection に包まれ、
  // Express 5 が自動的に next(err) する → エラーハンドラには届く
  const todos = await db.select().from(todos).all()
})
```

**本当の問題**は `await` の有無ではなく、以下のケースで起きる：

1. コールバック型ルートハンドラ（非 async）の中で例外が throw されても、Express 5 は捕捉できない
2. `async` ハンドラ内の **Promise でないコード**が try/catch で囲まれ、next(err) が呼ばれない
3. ハンドラ外（ミドルウェアチェーンの外側）での例外

---

## 4. 正しい書き方

### better-sqlite3 + Drizzle の場合（await 不要）

```ts
import { drizzle } from 'drizzle-orm/better-sqlite3'
import Database from 'better-sqlite3'
import { todos } from './schema'

const sqlite = new Database('app.db')
const db = drizzle(sqlite)

// ルートハンドラ: async にして Express 5 の自動 next(err) 伝搬を活かす
app.get('/todos', async (req, res) => {
  // await は不要（better-sqlite3 は同期）だが、async 関数内なので
  // 同期例外も自動的に Promise rejection → next(err) に変換される
  const result = db.select().from(todos).all()  // await なし
  res.json(result)
})

app.post('/todos', async (req, res) => {
  const inserted = db.insert(todos).values({ title: req.body.title }).returning().get()
  res.status(201).json(inserted)
})

// エラーハンドラ（4引数）
app.use((err: Error, req: Request, res: Response, next: NextFunction) => {
  console.error(err)
  res.status(500).json({ error: err.message })
})
```

### より明示的に: try/catch + next(err) を使う場合

```ts
app.get('/todos', (req, res, next) => {
  // 非 async ルートでも、try/catch + next(err) で確実にエラーを伝搬できる
  try {
    const result = db.select().from(todos).all()
    res.json(result)
  } catch (err) {
    next(err)  // ← これが必須
  }
})
```

---

## 5. PostgreSQL（pg ドライバ）との違い

| 観点 | better-sqlite3 | node-postgres (pg) |
|---|---|---|
| 実行モデル | 同期 | 非同期（Promise） |
| `await` の要否 | 不要（付けても no-op） | 必須 |
| エラーの種類 | 同期 throw | Promise rejection |
| Express 5 での自動伝搬 | async ハンドラ内なら自動（同期例外 → rejection に変換） | async ハンドラ内なら自動（rejection をそのまま捕捉） |

### pg の場合

```ts
// pg + Drizzle-ORM (drizzle-orm/node-postgres)
import { drizzle } from 'drizzle-orm/node-postgres'
import { Pool } from 'pg'

const pool = new Pool({ connectionString: process.env.DATABASE_URL })
const db = drizzle(pool)

app.get('/todos', async (req, res) => {
  // pg は非同期なので await は必須
  const result = await db.select().from(todos)  // .all() ではなく Promise を返す
  res.json(result)
  // Promise rejection は Express 5 が自動的に next(err) に変換
})
```

Drizzle ORM の API も微妙に異なる点に注意：

- `better-sqlite3` バインド: `.all()` / `.get()` / `.run()` (同期メソッド)
- `pg` / `mysql2` バインド: クエリビルダ自体が `Promise` を実装しており、`await db.select().from(todos)` で完結（`.all()` は不要）

---

## 6. まとめ

| 問題 | 原因 | 対処 |
|---|---|---|
| `await` が不要 | `better-sqlite3` は同期 API | `await` を外す（付けても動くが意味がない） |
| エラーハンドラに届かない | 非 async ルートで同期例外を `next(err)` しない | `async` ハンドラにするか、try/catch + `next(err)` を使う |
| pg との混同 | ドライバによって同期/非同期が異なる | `drizzle-orm/better-sqlite3` vs `drizzle-orm/node-postgres` の違いを意識する |

**最も安全なパターン：** `async` ルートハンドラを使い、better-sqlite3 のクエリは `await` なしで呼ぶ。  
Express 5 が async 関数内の同期例外を自動的に Promise rejection に変換し、エラーハンドラまで届ける。
