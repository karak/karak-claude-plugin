# Drizzle ORM + better-sqlite3: await の問題と Express 5 エラーハンドリング

## 結論

**`await` は不要であり、Express 5 のエラーハンドラにエラーが届かないケースの原因になり得る。**

---

## 1. better-sqlite3 は同期 API

`better-sqlite3` ドライバを使う Drizzle クエリはすべて **同期（Promise ではない）**。
`.all()` や `.get()` はそれぞれ即座に結果を返す同期メソッドであり、Promise を返さない。

```ts
// NG — 不要な await
const todos = await db.select().from(todos).all()
const inserted = await db.insert(todos).values({ title: 'test' }).returning().get()

// OK — 同期で直接返る
const todos = db.select().from(todos).all()
const inserted = db.insert(todos).values({ title: 'test' }).returning().get()
```

### `await` を付けても「動く」理由

JavaScript の `await` は非 Promise 値に対して即 resolve する。  
`await 42` が `42` を返すのと同じ原理で、同期値を `await` してもその値がそのまま返る。  
**つまり、`await` を付けても付けなくても結果は同じ**――ただし、エラーハンドリングの挙動が変わる。

---

## 2. Express 5 のエラーハンドラにエラーが届かないケース

### Express 5 の async error forwarding の仕組み

Express 5 では、async ルートハンドラ内で rejected になった Promise が **自動的に** `next(err)` に転送される。  
これにより、Express 4 で必要だった手動 try/catch が不要になった。

```ts
// Express 5 — rejected Promise は自動的に error handler に届く
app.get('/users', async (req, res) => {
  const users = await db.query('SELECT * FROM users')  // rejectされると自動転送
  res.json(users)
})
```

### 問題のシナリオ: 同期例外 × 非 async ハンドラ

**Express 5 の自動転送が効くのは「async 関数内の rejected Promise」のみ**。  
同期例外（`throw` / SQLite の constraint violation 等）は async 関数内で発生した場合のみ自動転送される。

```ts
// NG — 非 async ハンドラ内で同期例外がスローされた場合
app.get('/todos', (_req, res) => {
  // もし db 呼び出しが同期例外をスローしても、Express 5 は自動転送しない
  // → エラーがハンドラに届かず、サーバーがクラッシュするかレスポンスがハングする
  const todos = await db.select().from(todos).all()  // await は不要だが問題ではない
  res.json(todos)
})
```

### 正しい書き方

SQLite の同期例外が error middleware に届くようにするには、**ルートハンドラを `async` 関数にする**。

```ts
// OK — async 関数内の同期例外も Express 5 が自動転送する
app.get('/todos', async (_req, res) => {
  const todos = db.select().from(todos).all()   // await 不要、同期
  res.json(todos)
})

app.post('/todos', async (req, res) => {
  // SQLite constraint violation 等の同期例外が自動的に error handler に届く
  const inserted = db.insert(todos).values(req.body).returning().get()  // await 不要
  res.status(201).json(inserted)
})
```

`async` 関数内でスローされた同期例外は、JavaScript エンジンが自動的に rejected Promise に変換する。  
Express 5 はその rejected Promise を捕捉して `next(err)` に転送する、という流れになる。

---

## 3. PostgreSQL / pg ドライバとの違い

| 比較項目 | better-sqlite3 (SQLite) | pg / postgres.js (PostgreSQL) |
|---|---|---|
| API の性質 | **同期** | **非同期（Promise）** |
| `await` の要否 | 不要（付けても動く） | 必須（付けないと undefined になる） |
| Express 5 自動転送 | `async` ハンドラ内なら同期例外も転送される | rejected Promise が直接転送される |
| エラーの性質 | 同期 `throw`（constraint violation 等） | rejected Promise（接続エラー、クエリエラー等） |
| ハンドラの推奨形式 | `async` 関数（同期例外を Promise に変換させる） | `async` 関数（`await` で rejection を受け取る） |

```ts
// PostgreSQL (pg / drizzle-orm/node-postgres)
// await が必須。付けないと Promise がそのまま res.json() に渡り "{}}" になる
app.get('/todos', async (_req, res) => {
  const todos = await db.select().from(todos)  // PostgreSQL: await 必須
  res.json(todos)
})

// SQLite (better-sqlite3)
// await は不要。ただし async ハンドラにすることでエラー転送が保証される
app.get('/todos', async (_req, res) => {
  const todos = db.select().from(todos).all()  // SQLite: await 不要
  res.json(todos)
})
```

**PostgreSQL の Drizzle API (`drizzle-orm/node-postgres`) は Promise を返す**ため、`await` を外すとクエリ結果が `Promise` オブジェクトのままレスポンスに渡り、バグになる。  
better-sqlite3 と PostgreSQL でドライバを切り替えた場合に `await` の有無が問題になることがあるため、両者の違いを明確に理解しておく必要がある。

---

## 4. まとめ: 正しいコードパターン

```ts
import { Router } from 'express'
import { db } from '../db/client.ts'
import { todos } from '../db/schema.ts'
import { eq } from 'drizzle-orm'

export const todosRouter = Router()

// GET /todos — async ハンドラで同期エラーを自動転送
todosRouter.get('/', async (_req, res) => {
  const all = db.select().from(todos).all()  // await 不要
  res.json(all)
})

// POST /todos — constraint violation が error handler に届く
todosRouter.post('/', async (req, res) => {
  const inserted = db.insert(todos).values(req.body).returning().get()  // await 不要
  res.status(201).json(inserted)
})

// エラーハンドラ（引数は必ず4つ）
import type { ErrorRequestHandler } from 'express'
const errorHandler: ErrorRequestHandler = (err, _req, res, _next) => {
  console.error(err)
  const status = (err as { status?: number }).status ?? 500
  res.status(status).json({ error: err.message ?? 'Internal Server Error' })
}
app.use(errorHandler)
```

### チェックリスト

- [ ] better-sqlite3 クエリに `await` を付けない（`.all()` / `.get()` は同期）
- [ ] ルートハンドラは `async` にして SQLite 同期例外を Promise に変換させる
- [ ] エラーハンドラの引数は必ず `(err, req, res, next)` の 4 つ（3 つだと通常ミドルウェアとして扱われる）
- [ ] PostgreSQL に切り替える場合は `await` を追加する（API の性質が変わるため）
