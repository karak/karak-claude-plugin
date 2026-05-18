# Node.js 24 + Express 5 + Drizzle ORM + better-sqlite3 + Vitest 新規プロジェクトセットアップ手順

スキルファイル `nodejs-backend/SKILL.md` に基づき、`references/todo-app/` を雛形として利用した手順です。

---

## 1. クイックスタート（雛形コピー）

```bash
cp -r <skill-path>/references/todo-app/ ./my-api
cd my-api
npm install
npm run generate      # drizzle-kit generate（SQL マイグレーションファイル生成）
npm test              # 全テスト通過を確認
npm run dev           # 開発サーバー起動（tsx watch）
```

---

## 2. ディレクトリ構成

```
my-api/
├── src/
│   ├── server.ts          # listen() エントリーポイント
│   ├── app.ts             # Express app（listen なし。テストがここをインポート）
│   ├── db/
│   │   ├── schema.ts      # Drizzle スキーマ定義
│   │   └── client.ts      # DB 接続
│   ├── routes/
│   │   └── todos.ts       # Router
│   └── __tests__/
│       ├── setup.ts       # マイグレーション適用（beforeAll）
│       └── todos.test.ts  # supertest テスト
├── drizzle/               # drizzle-kit generate の出力先（SQL ファイル）
├── package.json
├── tsconfig.json
├── drizzle.config.ts
├── vitest.config.ts
└── tsup.config.ts
```

---

## 3. package.json

```json
{
  "name": "my-api",
  "version": "1.0.0",
  "type": "module",
  "engines": {
    "node": ">=24.0.0"
  },
  "scripts": {
    "dev": "tsx watch src/server.ts",
    "build": "tsup",
    "test": "vitest run",
    "test:watch": "vitest",
    "generate": "drizzle-kit generate",
    "migrate": "drizzle-kit migrate",
    "studio": "drizzle-kit studio"
  },
  "dependencies": {
    "better-sqlite3": "^12.0.0",
    "drizzle-orm": "^0.36.0",
    "express": "^5.0.0"
  },
  "devDependencies": {
    "@types/better-sqlite3": "^7.6.0",
    "@types/express": "^5.0.0",
    "@types/node": "^24.0.0",
    "@types/supertest": "^6.0.0",
    "drizzle-kit": "^0.28.0",
    "supertest": "^7.0.0",
    "tsup": "^8.0.0",
    "tsx": "^4.0.0",
    "typescript": "^5.8.0",
    "vitest": "^3.0.0"
  }
}
```

### 重要ポイント

- **`"type": "module"` は必須。** これがないと `.ts` ファイルが CommonJS として扱われ、ESM import が動かない。
- **`"engines": { "node": ">=24.0.0" }` を明記。** Node.js 24 のネイティブ type-stripping を前提とするため。
- `tsx` は開発時の `tsx watch` に使用。本番ビルドは `tsup`（`erasableSyntaxOnly` 準拠）。

---

## 4. tsconfig.json

```json
{
  "compilerOptions": {
    "target": "ES2022",
    "module": "NodeNext",
    "moduleResolution": "NodeNext",
    "verbatimModuleSyntax": true,
    "erasableSyntaxOnly": true,
    "strict": true,
    "noUncheckedIndexedAccess": true,
    "outDir": "./dist",
    "rootDir": "./src"
  }
}
```

### 各オプションの理由

| オプション | 理由 |
|---|---|
| `target: ES2022` | `ES2024` を指定すると drizzle-kit（esbuild v0.19）が設定ファイルのコンパイル時にエラーを出す。Node.js 24 は ES2024 構文をネイティブサポートするため実害はない |
| `module: NodeNext` + `moduleResolution: NodeNext` | Node.js ランタイムのモジュール解決と一致。`bundler` は extension-less import を許可するが Node.js ランタイムで失敗する |
| `erasableSyntaxOnly: true` | Node.js 24 のネイティブ type-stripping に合わせ、ランタイム変換が必要な構文（enum, namespace with values, parameter decorators）をコンパイル時に禁止 |
| `verbatimModuleSyntax: true` | 型のみのシンボルに `import type`/`export type` を強制。strip-types 時の不正動作を防ぐ |
| `noUncheckedIndexedAccess: true` | 配列・オブジェクトの添字アクセスに `undefined` を含める |

### 落とし穴: tsconfig の `paths` はランタイムで無視される

Node.js 24 は `tsconfig.json` を一切読まない。`paths: { "@/*": ["./src/*"] }` 等のエイリアスはコンパイルは通るが、ランタイムで `Cannot find module '@/...'` になる。

**解決策:** `package.json` の `imports` フィールドを使う:

```json
{
  "imports": {
    "#db/*": "./src/db/*.js",
    "#routes/*": "./src/routes/*.js"
  }
}
```

---

## 5. drizzle.config.ts

```ts
import { defineConfig } from 'drizzle-kit'

export default defineConfig({
  // drizzle-kit はこの設定ファイルを esbuild CJS モードでコンパイルするため、
  // import.meta は使用できない。プロジェクトルートからの相対パスを使う。
  schema: './src/db/schema.ts',
  out: './drizzle',
  dialect: 'sqlite',
  dbCredentials: { url: process.env.DB_FILE ?? './dev.db' },
})
```

### 重要ポイント

- **`import.meta.dirname` は drizzle.config.ts で使えない。** drizzle-kit は設定ファイルを esbuild の CJS モードでコンパイルするため。プロジェクトルートからの相対パスを使うこと。
- `dialect: 'sqlite'` を明示すること（PostgreSQL なら `'postgresql'`）。
- `DB_FILE` 環境変数でテスト時にインメモリ DB を使用できるようにしておく。

---

## 6. vitest.config.ts

```ts
import { defineConfig } from 'vitest/config'

export default defineConfig({
  test: {
    pool: 'forks',
    environment: 'node',
    env: { DB_FILE: ':memory:' },
    setupFiles: ['./src/__tests__/setup.ts'],
  },
})
```

### 重要ポイント: `pool: 'forks'` は必須・非交渉

`better-sqlite3` はネイティブ addon（`.node` バイナリ）。`pool: 'threads'`（worker_threads）は V8 ヒープを共有するためネイティブ addon のセグメンテーションフォルトを引き起こす。`pool: 'forks'`（child_process）では各テストファイルが独立した子プロセスで実行されるため安全。

- `env: { DB_FILE: ':memory:' }` — テスト時のみインメモリ DB を使用。各 fork プロセスに自動注入される。
- `setupFiles` — スキーマ適用用のセットアップファイルを指定。

---

## 7. tsup.config.ts（プロダクションビルド）

```ts
import { defineConfig } from 'tsup'

export default defineConfig({
  entry: ['src/server.ts'],
  format: ['esm'],
  target: 'node24',
  external: ['better-sqlite3', 'drizzle-orm'],
  clean: true,
})
```

### 重要ポイント

- `format: ['esm']` — ESM 出力（`package.json` の `"type": "module"` と整合）。
- `target: 'node24'` — Node.js 24 向け出力。
- `external: ['better-sqlite3', 'drizzle-orm']` — ネイティブアドオンや大きなパッケージはバンドルせず外部参照にする。

---

## 8. ソースコードの雛形

### src/server.ts（エントリーポイント）

```ts
import { app } from './app.ts'

const PORT = process.env.PORT ?? 3000
app.listen(PORT, () => console.log(`listening on ${PORT}`))
```

### src/app.ts（Express app — テスト用に listen なし）

```ts
import express from 'express'
import { todosRouter } from './routes/todos.ts'

export const app = express()
app.use(express.json())
app.use('/todos', todosRouter)
```

**なぜ `app.ts` と `server.ts` を分離するか:** テストでは `listen()` を呼ばないことでポート競合やプロセス終了処理が不要になる。supertest は `listen()` なしの app を in-process で直接テストできる。

### src/db/schema.ts

```ts
import { int, sqliteTable, text } from 'drizzle-orm/sqlite-core'

export const todos = sqliteTable('todos', {
  id: int('id').primaryKey({ autoIncrement: true }),
  title: text('title').notNull(),
  done: int('done', { mode: 'boolean' }).notNull().default(false),
  createdAt: text('created_at').notNull().$defaultFn(() => new Date().toISOString()),
})

export type Todo = typeof todos.$inferSelect
export type NewTodo = typeof todos.$inferInsert
```

**`.notNull()` の重要性:** 省略するとカラムが DB で NOT NULL でも TypeScript 型が `T | null` になる。

### src/db/client.ts

```ts
import Database from 'better-sqlite3'
import { drizzle } from 'drizzle-orm/better-sqlite3'
import * as schema from './schema.ts'

const sqlite = new Database(process.env.DB_FILE ?? ':memory:')
export const db = drizzle(sqlite, { schema })
```

### src/__tests__/setup.ts（テスト用マイグレーション適用）

```ts
import { existsSync } from 'node:fs'
import { join } from 'node:path'
import { beforeAll } from 'vitest'  // setupFiles では globals が自動注入されない
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

**重要:** `import.meta.dirname` を使うこと（`__dirname` は ESM では未定義）。`drizzle-kit migrate` CLI はインメモリ DB (`':memory:'`) に接続できないため、テスト用のスキーマ適用はプログラム内の `migrate()` 関数で行う。

### src/routes/todos.ts

```ts
import { Router } from 'express'
import { eq } from 'drizzle-orm'
import { db } from '../db/client.ts'
import { todos } from '../db/schema.ts'

export const todosRouter = Router()

todosRouter.get('/', (_req, res) => {
  const all = db.select().from(todos).all()  // 同期 API
  res.json(all)
})

todosRouter.post('/', (req, res) => {
  const { title } = req.body as { title: string }
  const inserted = db.insert(todos).values({ title }).returning().get()
  res.status(201).json(inserted)
})

todosRouter.patch('/:id', (req, res) => {
  const id = Number(req.params['id'])
  const updated = db
    .update(todos)
    .set(req.body as Partial<typeof todos.$inferInsert>)
    .where(eq(todos.id, id))
    .returning()
    .get()
  if (!updated) return res.status(404).json({ error: 'not found' })
  res.json(updated)
})

todosRouter.delete('/:id', (req, res) => {
  const id = Number(req.params['id'])
  const deleted = db.delete(todos).where(eq(todos.id, id)).returning().get()
  if (!deleted) return res.status(404).json({ error: 'not found' })
  res.status(204).end()
})
```

### src/__tests__/todos.test.ts

```ts
import { describe, it, expect, beforeEach } from 'vitest'
import request from 'supertest'
import { db } from '../db/client.ts'
import { todos } from '../db/schema.ts'
import { app } from '../app.ts'

beforeEach(() => {
  db.delete(todos).run()  // 各テスト前にテーブルをクリア（同期）
})

describe('GET /todos', () => {
  it('returns empty array initially', async () => {
    const res = await request(app).get('/todos').expect(200)
    expect(res.body).toEqual([])
  })
})

describe('POST /todos', () => {
  it('creates a todo and returns 201', async () => {
    const res = await request(app).post('/todos').send({ title: 'buy milk' }).expect(201)
    expect(res.body.title).toBe('buy milk')
    expect(res.body.done).toBe(false)
    expect(res.body.id).toBeTypeOf('number')
  })
})
```

---

## 9. 初回セットアップ手順（ステップバイステップ）

```bash
# 1. プロジェクト初期化
mkdir my-api && cd my-api
npm init -y

# 2. package.json を上記の内容に更新

# 3. 依存パッケージインストール
npm install

# 4. 設定ファイルを作成（tsconfig.json, drizzle.config.ts, vitest.config.ts, tsup.config.ts）

# 5. ソースファイルを作成（src/以下の構成）

# 6. SQL マイグレーションファイルを生成（必須：npm test の前に実行）
npm run generate

# 7. 開発用 DB にマイグレーション適用
npm run migrate

# 8. テスト実行
npm test

# 9. 開発サーバー起動
npm run dev
```

---

## 10. 重大な落とし穴まとめ

| 落とし穴 | 正しい対応 |
|---|---|
| `pool: 'threads'` で better-sqlite3 がクラッシュ | `pool: 'forks'` を必ず設定する |
| `drizzle-kit migrate` をインメモリ DB に使う | `migrate()` 関数でプログラム内適用する |
| `drizzle.config.ts` で `import.meta` を使う | プロジェクトルートからの相対パスを使う |
| import パスに `.ts` 拡張子なし | `'./db/client.ts'` のように必ず `.ts` を付ける |
| `__dirname` を ESM で使う | `import.meta.dirname` に置換する |
| `enum` を使う（erasableSyntaxOnly エラー） | `as const` オブジェクトに置換する |
| Decorator ベースルーティング（routing-controllers 等） | plain Router + function handlers を使う |
| `tsconfig.json` の `paths` でエイリアス定義 | `package.json` の `imports` フィールドを使う |
| Express 5 で `app.get('/api/*', handler)` | `app.get('/api/{*path}', handler)` に変更 |
| better-sqlite3 クエリに `await` を付ける | 同期 API なので不要（付けても動くが誤解を招く） |
| `npm run generate` なしで `npm test` を実行 | 必ず generate を先に実行すること |

---

## 11. 開発コマンド早見表

```bash
# 開発サーバー
tsx watch src/server.ts

# テスト
vitest run
vitest --reporter=verbose

# Drizzle マイグレーション
drizzle-kit generate   # SQL マイグレーションファイル生成（schema.ts 変更後に実行）
drizzle-kit migrate    # ファイル DB に適用（:memory: 不可）
drizzle-kit studio     # GUI ブラウザで DB 閲覧

# プロダクションビルド
tsup src/server.ts --format esm --target node24 \
  --external better-sqlite3 --external drizzle-orm
```
