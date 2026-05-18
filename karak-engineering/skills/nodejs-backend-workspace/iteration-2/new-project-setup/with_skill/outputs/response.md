# Node.js 24 + Express 5 + Drizzle ORM + better-sqlite3 + Vitest 新規プロジェクトセットアップ

## クイックスタート（テンプレートから始める場合）

```bash
cp -r <skill-path>/references/todo-app/ ./my-api
cd my-api
npm install
npm run generate   # drizzle-kit generate（テスト前に必須）
npm test           # 全テスト通過を確認
npm run dev        # 開発サーバー起動
```

---

## ディレクトリ構成

```
my-api/
├── src/
│   ├── __tests__/
│   │   ├── setup.ts        # Vitest セットアップ（migrate）
│   │   └── todos.test.ts   # HTTP テスト (supertest)
│   ├── db/
│   │   ├── client.ts       # Drizzle インスタンス
│   │   └── schema.ts       # テーブル定義
│   ├── routes/
│   │   └── todos.ts        # Express Router
│   ├── app.ts              # Express app（listen なし）
│   └── server.ts           # エントリーポイント（listen のみ）
├── drizzle/                # drizzle-kit generate で自動生成
├── drizzle.config.ts
├── package.json
├── tsconfig.json
├── tsup.config.ts
└── vitest.config.ts
```

---

## 1. package.json

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

- **`"type": "module"`** — ESM プロジェクトとして宣言。これがないと `.ts` ファイルで ESM 構文が使えない
- **`"engines": { "node": ">=24.0.0" }`** — Node.js 24 のネイティブ type-stripping を前提とした宣言
- **開発は `tsx watch`** — `tsc --watch` は不要。tsx が TypeScript をそのまま実行する
- **ビルドは `tsup`** — ESM 出力、tree-shaking、`better-sqlite3` / `drizzle-orm` は外部化

---

## 2. tsconfig.json

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

### 重要ポイント

| オプション | 理由 |
|---|---|
| `target: "ES2022"` | `ES2024` にすると drizzle-kit（内部 esbuild v0.19）がコンパイルエラーを出す |
| `module: "NodeNext"` + `moduleResolution: "NodeNext"` | Node.js ランタイムの解決ロジックと一致。`bundler` は拡張子なし import を許可するが Node.js ランタイムで失敗する |
| `verbatimModuleSyntax: true` | 型のみのシンボルに `import type` / `export type` を強制。type-stripping 時の不正動作を防ぐ |
| `erasableSyntaxOnly: true` | Node.js 24 のネイティブ type-stripping に合わせ、`enum` / `namespace` / parameter decorators をコンパイル時に禁止 |
| `noUncheckedIndexedAccess: true` | 配列・オブジェクトの添字アクセスに `undefined` を含める（安全なコード） |

### 必須: import パスに `.ts` 拡張子を明記

```ts
// NG — Node.js が解決できない（RuntimeError）
import { db } from './db/client'

// OK
import { db } from './db/client.ts'
```

### 必須: `__dirname` は ESM で未定義

```ts
// NG — ReferenceError: __dirname is not defined
const dir = path.join(__dirname, 'drizzle')

// OK — Node.js 21.2+ で利用可能
const dir = path.join(import.meta.dirname, 'drizzle')
```

### `erasableSyntaxOnly` で禁止される構文

```ts
// NG — enum は禁止
enum Status { Active, Inactive }

// OK — as const で代替
const Status = { Active: 'active', Inactive: 'inactive' } as const
type Status = typeof Status[keyof typeof Status]
```

---

## 3. drizzle.config.ts

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

- **`import.meta` は使用不可** — drizzle-kit は設定ファイルを esbuild の CJS モードでコンパイルするため `import.meta.dirname` が使えない。プロジェクトルートからの相対パスを使う
- **`drizzle-kit migrate` はインメモリ DB 非対応** — `:memory:` は CLI の別プロセスから接続できない。テスト用インメモリ DB には後述の `setup.ts` でプログラム内 migrate を使う

### マイグレーションワークフロー

```bash
# 1. src/db/schema.ts を編集
# 2. SQL マイグレーションファイルを生成（drizzle/ に保存）
npm run generate

# 3. ファイル DB に適用
npm run migrate

# 4. Drizzle Studio（GUI）
npm run studio
```

---

## 4. Drizzle スキーマとクライアント

### src/db/schema.ts

```ts
import { int, sqliteTable, text } from 'drizzle-orm/sqlite-core'

export const todos = sqliteTable('todos', {
  id: int('id').primaryKey({ autoIncrement: true }),
  title: text('title').notNull(),
  done: int('done', { mode: 'boolean' }).notNull().default(false),
  createdAt: text('created_at').notNull().$defaultFn(() => new Date().toISOString()),
})

// TypeScript 型を自動推論
export type Todo = typeof todos.$inferSelect
export type NewTodo = typeof todos.$inferInsert
```

**`.notNull()` は必須:** 省略するとカラムが DB で NOT NULL でも TypeScript 型が `T | null` になる。

### src/db/client.ts

```ts
import Database from 'better-sqlite3'
import { drizzle } from 'drizzle-orm/better-sqlite3'
import * as schema from './schema.ts'

// DB_FILE=':memory:' のときはインメモリ DB（テスト用）
const sqlite = new Database(process.env.DB_FILE ?? ':memory:')
export const db = drizzle(sqlite, { schema })
```

### 最重要: better-sqlite3 クエリは同期 API

```ts
// NG — 不要な await（動くが誤解を招く）
const todos = await db.select().from(todos).all()

// OK — 同期で直接返る
const todos = db.select().from(todos).all()
const todo = db.insert(todos).values({ title: 'test' }).returning().get()
```

---

## 5. vitest.config.ts

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

### 重要ポイント

| 設定 | 理由 |
|---|---|
| `pool: 'forks'` | **必須・非交渉。** `better-sqlite3` はネイティブ addon（`.node` バイナリ）。デフォルトの `pool: 'threads'`（worker_threads）は V8 ヒープ共有によりセグメンテーションフォルトを引き起こす。`forks` は child_process を使うため安全 |
| `env: { DB_FILE: ':memory:' }` | テスト実行中のみインメモリ DB を使用。`forks` の各 fork プロセスに環境変数が注入される |
| `setupFiles` | テスト前に `migrate()` でスキーマを適用するセットアップファイルを指定 |

### src/__tests__/setup.ts

```ts
import { existsSync } from 'node:fs'
import { join } from 'node:path'
import { beforeAll } from 'vitest'
import { migrate } from 'drizzle-orm/better-sqlite3/migrator'
import { db } from '../db/client.ts'

// __dirname は ESM 未定義 → import.meta.dirname を使う
const migrationsFolder = join(import.meta.dirname, '../../drizzle')

beforeAll(() => {
  if (!existsSync(migrationsFolder)) {
    throw new Error('Run `npm run generate` before `npm test`.')
  }
  migrate(db, { migrationsFolder })
})
```

- `pool: forks` では各テストファイルが独立プロセスで実行されるため、`beforeAll` は worker（= テストファイル）ごとに 1 回だけ実行される → `:memory:` DB の分離が自動で保たれる

---

## 6. Express アプリ構成

### src/app.ts（listen なし）

```ts
import express from 'express'
import { todosRouter } from './routes/todos.ts'

export const app = express()
app.use(express.json())
app.use('/todos', todosRouter)
```

### src/server.ts（エントリーポイント）

```ts
import { app } from './app.ts'

const PORT = process.env.PORT ?? 3000
app.listen(PORT, () => console.log(`listening on ${PORT}`))
```

**`app.ts` と `server.ts` を分離する理由:**
- テストでは `app` だけをインポートし、`listen()` を呼ばない
- supertest は `app` を直接受け取り in-process でリクエストを処理するため、ポート競合やプロセス終了処理が不要

---

## 7. テスト (supertest + Vitest)

### src/__tests__/todos.test.ts

```ts
import { describe, it, expect, beforeEach } from 'vitest'
import request from 'supertest'
import { db } from '../db/client.ts'
import { todos } from '../db/schema.ts'
import { app } from '../app.ts'

// 各テスト前にテーブルを空にする（同期）
beforeEach(() => {
  db.delete(todos).run()
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

## 8. tsup.config.ts（プロダクションビルド）

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

- **`external: ['better-sqlite3', 'drizzle-orm']`** — ネイティブ addon はバンドルできないため外部化が必須

---

## セットアップチェックリスト

- [ ] `package.json` に `"type": "module"` と `"engines": { "node": ">=24.0.0" }`
- [ ] `tsconfig.json` に `module: NodeNext`, `moduleResolution: NodeNext`, `erasableSyntaxOnly: true`, `verbatimModuleSyntax: true`
- [ ] import パスに `.ts` 拡張子を明記（`'./file'` ではなく `'./file.ts'`）
- [ ] `__dirname` を `import.meta.dirname` に置換
- [ ] `drizzle.config.ts` を作成（`import.meta` は使用不可、相対パスで記述）
- [ ] `vitest.config.ts` に `pool: 'forks'` を設定（better-sqlite3 ネイティブ addon 必須）
- [ ] `npm run generate` を `npm test` より前に実行（`drizzle/` ディレクトリ生成）
- [ ] `app.ts`（listen なし）と `server.ts`（listen のみ）を分離

---

## よくある落とし穴

| 症状 | 原因 | 解決策 |
|---|---|---|
| `Cannot find module './db/client'` | import パスに拡張子がない | `'./db/client.ts'` と明記 |
| `ReferenceError: __dirname is not defined` | ESM で `__dirname` は未定義 | `import.meta.dirname` に置換 |
| テストでセグメンテーションフォルト | `pool: 'threads'` で better-sqlite3 を使用 | `pool: 'forks'` に変更 |
| `Error: Run npm run generate before npm test` | `drizzle/` ディレクトリが存在しない | `npm run generate` を先に実行 |
| `import.meta is not defined` in drizzle.config.ts | drizzle-kit が CJS モードでコンパイル | 相対パスを直接使用 |
| `await db.select()...` で型エラー | better-sqlite3 は同期 API | `await` を削除 |
| `enum` で TypeScript エラー | `erasableSyntaxOnly: true` で禁止 | `as const` オブジェクトに変換 |
