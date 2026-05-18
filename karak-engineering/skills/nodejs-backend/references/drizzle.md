# Drizzle ORM — Patterns & Pitfalls

Drizzle ORM v0.36+ + drizzle-kit v0.28+

## ⚡ 最重要: better-sqlite3 は同期 API

**better-sqlite3 ドライバを使うすべての Drizzle クエリは同期（Promise ではない）。**
`await` は不要。誤って `await` しても動作するが（non-Promise を await すると即 resolve）、
エラーハンドリングの理解が歪む。

```ts
// NG — 不要な await（動くが誤解を招く）
const todos = await db.select().from(todos).all()

// OK — 同期で直接返る
const todos = db.select().from(todos).all()
const todo = db.insert(todos).values({ title: 'test' }).returning().get()
```

同期例外は Express 5 の async ハンドラ内でも正しく error middleware に届く:

```ts
app.post('/todos', async (req, res) => {
  // sqlite のエラー（constraint violation 等）は同期でスローされ、
  // Express 5 の async error forwarding で error handler に届く
  const todo = db.insert(todos).values(req.body).returning().get()
  res.status(201).json(todo)
})
```

---

## セットアップ

```bash
npm install drizzle-orm better-sqlite3
npm install -D drizzle-kit @types/better-sqlite3
```

### drizzle.config.ts（必須）

**この設定ファイルがないと `drizzle-kit generate` / `drizzle-kit migrate` が動かない。**

```ts
import { defineConfig } from 'drizzle-kit'

export default defineConfig({
  // drizzle-kit はこの設定ファイルを esbuild CJS モードでコンパイルするため、
  // import.meta は使用できない。プロジェクトルートからの相対パスを使う。
  schema: './src/db/schema.ts',
  out: './drizzle',
  dialect: 'sqlite',
  dbCredentials: {
    url: process.env.DB_FILE ?? './dev.db',
  },
})
```

---

## スキーマ定義

```ts
// src/db/schema.ts
import { int, sqliteTable, text } from 'drizzle-orm/sqlite-core'

export const todos = sqliteTable('todos', {
  id: int('id').primaryKey({ autoIncrement: true }),
  title: text('title').notNull(),        // .notNull() がないと T | null に推論される
  done: int('done', { mode: 'boolean' }).notNull().default(false),
  createdAt: text('created_at').notNull().$defaultFn(() => new Date().toISOString()),
})

// TypeScript 型を自動推論
export type Todo = typeof todos.$inferSelect
export type NewTodo = typeof todos.$inferInsert
```

**`.notNull()` の重要性:** 省略するとカラムが DB で NOT NULL でも TypeScript 型が `T | null` になる。

### PostgreSQL の場合

```ts
import { pgTable, serial, text, boolean, timestamp } from 'drizzle-orm/pg-core'

export const todos = pgTable('todos', {
  id: serial('id').primaryKey(),
  title: text('title').notNull(),
  done: boolean('done').notNull().default(false),
  createdAt: timestamp('created_at').notNull().defaultNow(),
})
```

---

## DB クライアント

```ts
// src/db/client.ts
import Database from 'better-sqlite3'
import { drizzle } from 'drizzle-orm/better-sqlite3'
import * as schema from './schema.ts'

// process.env.DB_FILE が ':memory:' の場合はインメモリ DB
// Vitest は test.env: { DB_FILE: ':memory:' } で自動設定
const sqlite = new Database(process.env.DB_FILE ?? ':memory:')
export const db = drizzle(sqlite, { schema })
```

---

## マイグレーションワークフロー

### 開発フロー

```bash
# 1. schema.ts を編集

# 2. SQL マイグレーションファイルを生成（drizzle/ ディレクトリに保存）
npx drizzle-kit generate

# 3. ファイル DB に適用
npx drizzle-kit migrate    # dev.db に適用

# 4. Prisma Studio 相当の GUI
npx drizzle-kit studio
```

### ⚠️ :memory: DB と drizzle-kit migrate は非互換

`drizzle-kit migrate` は別プロセスとして起動し、ファイル DB (`./dev.db`) に接続する。
**インメモリ DB (`':memory:'`) には接続できない。**

テスト用インメモリ DB のスキーマ適用には、プログラム内で `migrate()` を使う:

```ts
// src/__tests__/setup.ts
import { existsSync } from 'node:fs'
import { join } from 'node:path'
import { migrate } from 'drizzle-orm/better-sqlite3/migrator'
import { db } from '../db/client.ts'

const migrationsFolder = join(import.meta.dirname, '../../drizzle')

beforeAll(() => {
  if (!existsSync(migrationsFolder)) {
    throw new Error('Run `npm run generate` before `npm test`.')
  }
  migrate(db, { migrationsFolder })
})
```

---

## クエリ API

```ts
// SELECT
const all = db.select().from(todos).all()
const one = db.select().from(todos).where(eq(todos.id, 1)).get()

// SELECT with JOIN
const withUser = db
  .select({ todo: todos, user: users })
  .from(todos)
  .leftJoin(users, eq(todos.userId, users.id))
  .all()

// INSERT
const inserted = db.insert(todos).values({ title: 'Buy milk' }).returning().get()
// returning() は SQLite では全カラムを返す

// UPDATE
const updated = db
  .update(todos)
  .set({ done: true })
  .where(eq(todos.id, 1))
  .returning()
  .get()  // undefined if not found

// DELETE
const deleted = db.delete(todos).where(eq(todos.id, 1)).returning().get()

// Relational API (Prisma-like)
const todosWithTags = db.query.todos.findMany({
  with: { tags: true },
})
```

---

## 接続管理（explicit）

Drizzle は接続管理を自動で行わない。`better-sqlite3` の場合はプロセス終了時に自動クローズ。
長期間動く サーバーでは明示的にクローズ:

```ts
process.on('SIGTERM', () => {
  sqlite.close()
  process.exit(0)
})
```

---

## Drizzle vs Prisma 選択基準

→ `prisma.md` の比較表を参照

**Drizzle を選ぶ主な理由:**
- サーバーレス・エッジランタイム（バイナリなし）
- SQL を直接制御したい
- バンドルサイズを最小化したい

---

## 参考リンク

- [Drizzle ORM ドキュメント](https://orm.drizzle.team/)
- [Drizzle + SQLite Getting Started](https://orm.drizzle.team/docs/get-started-sqlite)
- [Drizzle Migrations](https://orm.drizzle.team/docs/migrations)
- [drizzle-kit CLI](https://orm.drizzle.team/kit-docs/overview)
