# Express 5 — Patterns & Migration Guide

Express 5 は 2024 年末〜2025 年初頭に npm `latest` タグになった。

## path-to-regexp v8 Breaking Changes (最重要)

Express 5 は path-to-regexp を 0.x → 8.x に更新。**既存のルートパターンが多数動かなくなる。**

### Wildcard パターン

```ts
// Express 4 (NG in Express 5)
app.get('/api/*', handler)
app.get('/files/*.*', handler)

// Express 5
app.get('/api/(.*)', handler)
app.get('/api/{*path}', handler)    // 推奨記法
```

### Optional パラメータ

```ts
// Express 4 (NG in Express 5)
app.get('/users/:id?', handler)

// Express 5
app.get('/users{/:id}', handler)
```

### 正規表現・特殊文字

```ts
// Express 4 (NG in Express 5) — 正規表現入りパターン
app.get('/[discussion|page]/:slug', handler)

// Express 5 — 正規表現はルート文字列に使えない
// Router.use() の第1引数として String のみ使用可
// 正規表現が必要な場合は app.use() で prefix 一致後に内部で処理
```

### ルートの検証

Express 5 は無効なパターンをサーバー起動時に**例外**としてスロー。
サードパーティミドルウェアが内部で `app.use(regex, ...)` をしている場合も注意。

---

## async エラーの自動 forwarding (DX 改善)

Express 5 では async ルートハンドラの rejected Promise が自動的に `next(err)` に転送される。

```ts
// Express 4 — 手動 try/catch が必要だった
app.get('/users', async (req, res, next) => {
  try {
    const users = await db.query('SELECT * FROM users')
    res.json(users)
  } catch (err) {
    next(err)
  }
})

// Express 5 — 自動転送
app.get('/users', async (req, res) => {
  const users = await db.query('SELECT * FROM users')
  res.json(users)
  // 例外は自動的に error handler に届く
})
```

**注意:** Drizzle + better-sqlite3 は同期 API なので `await` は不要。
同期例外は `async` 関数内であれば正しく error handler に届く:

```ts
// Drizzle (better-sqlite3) — 同期、await 不要
app.get('/todos', (_req, res) => {
  const all = db.select().from(todos).all()  // 同期
  res.json(all)
})

// async でもよいが await は不要
app.post('/todos', async (req, res) => {
  const inserted = db.insert(todos).values(req.body).returning().get()  // 同期
  res.status(201).json(inserted)
})
```

---

## 削除されたメソッド

| Express 4 | Express 5 代替 |
|---|---|
| `req.param(name)` | `req.params.name`, `req.query.name`, `req.body.name` を明示的に使用 |
| `res.json(obj, status)` | `res.status(status).json(obj)` |
| `res.send(body, status)` | `res.status(status).send(body)` |
| `app.del(path, handler)` | `app.delete(path, handler)` |

---

## TypeScript 型付きリクエスト/レスポンス

```ts
import type { Request, Response, NextFunction } from 'express'

// 型パラメータ: <Params, ResBody, ReqBody, Query>
app.post(
  '/todos',
  (req: Request<{}, Todo, { title: string }, {}>, res: Response<Todo>) => {
    const { title } = req.body   // string として推論
    const todo = createTodo(title)
    res.status(201).json(todo)
  }
)

// Params 付き
app.get(
  '/todos/:id',
  (req: Request<{ id: string }>, res: Response) => {
    const id = Number(req.params.id)
    // ...
  }
)
```

---

## Decorator ベースルーティングの禁止

`erasableSyntaxOnly: true` の環境（Node.js 24 推奨設定）では、以下は**使用不可**:

- `routing-controllers` (`@Get()`, `@Body()` 等)
- `tsyringe`, `inversify`（DI + decorator）
- `typeorm` の entity decorator

**代替:** plain function handlers + Router を使う。

```ts
// NG — erasableSyntaxOnly と非互換
@Controller('/todos')
class TodoController {
  @Get('/')
  list() { ... }
}

// OK — plain Router
import { Router } from 'express'
export const todosRouter = Router()

todosRouter.get('/', (_req, res) => { ... })
todosRouter.post('/', (req, res) => { ... })
```

---

## エラーハンドラーの定義

```ts
import type { ErrorRequestHandler } from 'express'

// 必ず引数を4つ記述すること（Express の判定条件）
const errorHandler: ErrorRequestHandler = (err, _req, res, _next) => {
  console.error(err)
  const status = (err as { status?: number }).status ?? 500
  res.status(status).json({ error: err.message ?? 'Internal Server Error' })
}

app.use(errorHandler)
```

---

## 404 ハンドラー

```ts
// すべてのルートの後に配置
app.use((_req, res) => {
  res.status(404).json({ error: 'Not Found' })
})
```

---

## 参考リンク

- [Express 5 公式ドキュメント](https://expressjs.com/en/5x/api.html)
- [Express 4→5 移行ガイド](https://expressjs.com/en/guide/migrating-5.html)
- [path-to-regexp 8.x 変更点](https://github.com/pillarjs/path-to-regexp/releases)
