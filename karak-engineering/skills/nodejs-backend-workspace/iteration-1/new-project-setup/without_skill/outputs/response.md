# Node.js 24 + Express 5 + Drizzle ORM + better-sqlite3 + Vitest セットアップガイド

## 概要

このガイドでは、以下のスタックを使った新規バックエンドAPIプロジェクトのセットアップ手順を説明します。

- **Node.js 24** — 最新のLTSバージョン（2024年リリース）、`--experimental-strip-types` によるTypeScriptネイティブ実行に対応
- **Express 5** — 安定版リリース（2024年10月）、非同期エラーハンドリングが標準サポート
- **Drizzle ORM** — TypeScriptファーストの軽量ORM
- **better-sqlite3** — 同期APIを持つSQLiteバインディング
- **Vitest** — Viteベースの高速テストランナー

---

## 1. プロジェクト初期化

```bash
mkdir my-api && cd my-api
npm init -y
git init
```

---

## 2. 依存関係のインストール

```bash
# ランタイム依存
npm install express better-sqlite3 drizzle-orm

# 開発依存
npm install -D \
  typescript \
  tsx \
  @types/node \
  @types/express \
  @types/better-sqlite3 \
  drizzle-kit \
  vitest \
  @vitest/coverage-v8
```

**バージョンの目安（2024年末〜2025年時点）:**

| パッケージ | バージョン |
|---|---|
| express | ^5.0.0 |
| better-sqlite3 | ^11.x |
| drizzle-orm | ^0.38.x |
| drizzle-kit | ^0.29.x |
| vitest | ^2.x または ^3.x |
| typescript | ^5.x |

---

## 3. `package.json` の重要なポイント

```json
{
  "name": "my-api",
  "version": "1.0.0",
  "type": "module",
  "engines": {
    "node": ">=24.0.0"
  },
  "scripts": {
    "dev": "tsx watch src/index.ts",
    "build": "tsc",
    "start": "node dist/index.js",
    "db:generate": "drizzle-kit generate",
    "db:migrate": "drizzle-kit migrate",
    "db:studio": "drizzle-kit studio",
    "test": "vitest run",
    "test:watch": "vitest",
    "test:coverage": "vitest run --coverage"
  }
}
```

### 重要ポイント

1. **`"type": "module"`** — ESModule形式を使う。`import/export` 構文が使えるようになる。`require()` は使えなくなるため注意。
2. **`"engines"`** — Node.js 24以上を明示することで、CI/CD環境での意図せぬバージョン使用を防ぐ。
3. **`tsx`** — 開発時はtsxでTypeScriptを直接実行。本番は `tsc` でビルドしてから `node` で実行する2段構成。

### ESMとbetter-sqlite3の注意点

`better-sqlite3` はネイティブモジュール（`.node` バインディング）のため、Node.jsバージョンに合ったビルドが必要です。Node.jsのメジャーバージョンを上げた後は `npm rebuild better-sqlite3` を実行してください。

---

## 4. `tsconfig.json` の重要なポイント

```json
{
  "compilerOptions": {
    "target": "ES2022",
    "module": "NodeNext",
    "moduleResolution": "NodeNext",
    "lib": ["ES2022"],
    "outDir": "dist",
    "rootDir": "src",
    "strict": true,
    "esModuleInterop": true,
    "skipLibCheck": true,
    "declaration": true,
    "declarationMap": true,
    "sourceMap": true,
    "resolveJsonModule": true,
    "forceConsistentCasingInFileNames": true
  },
  "include": ["src/**/*"],
  "exclude": ["node_modules", "dist", "**/*.test.ts", "**/*.spec.ts"]
}
```

### 重要ポイント

1. **`"module": "NodeNext"` + `"moduleResolution": "NodeNext"`** — Node.js ESMに最も適した組み合わせ。`"module": "ESNext"` + `"moduleResolution": "Bundler"` はバンドラー向けなので注意。
2. **`"target": "ES2022"`** — Node.js 24はES2022以上をネイティブサポートするため、ダウンコンパイル不要。
3. **NodeNext モジュール解決の落とし穴** — `NodeNext` モードでは、TypeScriptファイルから他のtsファイルをimportするとき `.js` 拡張子で書く必要がある（コンパイル後のファイル名に合わせる）:

```typescript
// NG
import { db } from './db'
// OK
import { db } from './db.js'
```

4. **テストファイルを `exclude`** — テストファイルは本番ビルドに含めない。

---

## 5. ディレクトリ構成

```
my-api/
├── src/
│   ├── index.ts           # エントリーポイント
│   ├── app.ts             # Expressアプリ設定
│   ├── db/
│   │   ├── index.ts       # DB接続
│   │   └── schema.ts      # Drizzleスキーマ定義
│   ├── routes/
│   │   └── todos.ts       # ルートハンドラ
│   └── __tests__/
│       └── todos.test.ts
├── drizzle/               # drizzle-kitが生成するマイグレーションファイル
├── drizzle.config.ts
├── vitest.config.ts
├── tsconfig.json
└── package.json
```

---

## 6. Drizzle ORM 設定

### `drizzle.config.ts`

```typescript
import { defineConfig } from 'drizzle-kit'

export default defineConfig({
  schema: './src/db/schema.ts',
  out: './drizzle',
  dialect: 'sqlite',
  dbCredentials: {
    url: process.env.DATABASE_URL ?? './dev.db',
  },
  verbose: true,
  strict: true,
})
```

### 重要ポイント

1. **`dialect: 'sqlite'`** — drizzle-kit 0.21以降は `dialect` が必須フィールドになった（旧来の `driver` は非推奨）。
2. **`dbCredentials.url`** — SQLiteのファイルパスを指定。`file:./dev.db` のように `file:` プレフィックスをつける場合もある（drizzle-ormのバージョンによる）。
3. **`out`** — マイグレーションSQLファイルとスナップショットの出力先。

### `src/db/schema.ts`

```typescript
import { sqliteTable, text, integer } from 'drizzle-orm/sqlite-core'
import { sql } from 'drizzle-orm'

export const todos = sqliteTable('todos', {
  id: integer('id').primaryKey({ autoIncrement: true }),
  title: text('title').notNull(),
  completed: integer('completed', { mode: 'boolean' }).notNull().default(false),
  createdAt: text('created_at')
    .notNull()
    .default(sql`(datetime('now'))`),
})

export type Todo = typeof todos.$inferSelect
export type NewTodo = typeof todos.$inferInsert
```

### `src/db/index.ts`

```typescript
import Database from 'better-sqlite3'
import { drizzle } from 'drizzle-orm/better-sqlite3'
import * as schema from './schema.js'

const sqlite = new Database(process.env.DATABASE_URL ?? './dev.db')

// パフォーマンス最適化
sqlite.pragma('journal_mode = WAL')
sqlite.pragma('foreign_keys = ON')

export const db = drizzle(sqlite, { schema })
```

### 重要ポイント

1. **`pragma('journal_mode = WAL')`** — Write-Ahead Loggingを有効化。同時読み書きのパフォーマンスが大幅に向上する。
2. **`pragma('foreign_keys = ON')`** — SQLiteはデフォルトで外部キー制約が無効なので明示的に有効化する。
3. **`schema` をdrizzleに渡す** — クエリビルダで型安全なリレーション解決（`with`句）を使うために必要。

---

## 7. Express 5 アプリ設定

### `src/app.ts`

```typescript
import express from 'express'
import type { Request, Response, NextFunction } from 'express'
import { todosRouter } from './routes/todos.js'

export function createApp() {
  const app = express()

  app.use(express.json())
  app.use(express.urlencoded({ extended: true }))

  // ルート登録
  app.use('/api/todos', todosRouter)

  // ヘルスチェック
  app.get('/health', (_req: Request, res: Response) => {
    res.json({ status: 'ok' })
  })

  // 404ハンドラ
  app.use((_req: Request, res: Response) => {
    res.status(404).json({ error: 'Not Found' })
  })

  // Express 5のエラーハンドラ（4引数が必須）
  // eslint-disable-next-line @typescript-eslint/no-unused-vars
  app.use((err: Error, _req: Request, res: Response, _next: NextFunction) => {
    console.error(err.stack)
    res.status(500).json({ error: err.message })
  })

  return app
}
```

### Express 5 の重要な変更点

1. **非同期ルートハンドラのエラーが自動伝播** — Express 4では `try/catch` してから `next(err)` を手動で呼ぶ必要があったが、Express 5では `async` ルートハンドラでthrowされたエラーが自動的にエラーハンドラに伝わる。

```typescript
// Express 5: tryなしで書ける
router.get('/', async (req, res) => {
  const result = await db.select().from(todos) // エラーは自動でnext(err)に渡る
  res.json(result)
})
```

2. **`app.router` プロパティが廃止** — Express 4の `app.router` は削除された。
3. **`req.param()` メソッドが廃止** — `req.params.name` を使う。
4. **`res.json()` のボディ変換が改善** — `null` を渡すと空ボディではなく `null` というJSONを返す。

### `src/routes/todos.ts`

```typescript
import { Router } from 'express'
import { db } from '../db/index.js'
import { todos } from '../db/schema.js'
import { eq } from 'drizzle-orm'
import type { NewTodo } from '../db/schema.js'

export const todosRouter = Router()

// 一覧取得
todosRouter.get('/', async (_req, res) => {
  const result = await db.select().from(todos)
  res.json(result)
})

// 作成
todosRouter.post('/', async (req, res) => {
  const body = req.body as { title: string }
  if (!body.title?.trim()) {
    res.status(400).json({ error: 'title is required' })
    return
  }
  const newTodo: NewTodo = { title: body.title.trim() }
  const [created] = await db.insert(todos).values(newTodo).returning()
  res.status(201).json(created)
})

// 更新
todosRouter.patch('/:id', async (req, res) => {
  const id = Number(req.params.id)
  const body = req.body as { completed?: boolean; title?: string }
  const [updated] = await db
    .update(todos)
    .set(body)
    .where(eq(todos.id, id))
    .returning()
  if (!updated) {
    res.status(404).json({ error: 'Not Found' })
    return
  }
  res.json(updated)
})

// 削除
todosRouter.delete('/:id', async (req, res) => {
  const id = Number(req.params.id)
  const [deleted] = await db
    .delete(todos)
    .where(eq(todos.id, id))
    .returning()
  if (!deleted) {
    res.status(404).json({ error: 'Not Found' })
    return
  }
  res.status(204).send()
})
```

### `src/index.ts`

```typescript
import { createApp } from './app.js'
import { db } from './db/index.js'
import { migrate } from 'drizzle-orm/better-sqlite3/migrator'
import path from 'node:path'
import { fileURLToPath } from 'node:url'

const __dirname = fileURLToPath(new URL('.', import.meta.url))

async function main() {
  // マイグレーション自動適用
  migrate(db, {
    migrationsFolder: path.join(__dirname, '../drizzle'),
  })

  const app = createApp()
  const port = Number(process.env.PORT ?? 3000)

  app.listen(port, () => {
    console.log(`Server running on http://localhost:${port}`)
  })
}

main().catch(console.error)
```

---

## 8. Vitest 設定

### `vitest.config.ts`

```typescript
import { defineConfig } from 'vitest/config'

export default defineConfig({
  test: {
    globals: true,
    environment: 'node',
    include: ['src/**/*.test.ts', 'src/**/*.spec.ts'],
    exclude: ['node_modules', 'dist'],
    coverage: {
      provider: 'v8',
      reporter: ['text', 'json', 'html'],
      include: ['src/**/*.ts'],
      exclude: ['src/**/*.test.ts', 'src/index.ts'],
    },
    // テスト間でのDB状態汚染を防ぐためにシリアル実行
    pool: 'forks',
    poolOptions: {
      forks: {
        singleFork: true,
      },
    },
  },
})
```

### 重要ポイント

1. **`globals: true`** — `describe`, `it`, `expect` をimportなしで使える。`tsconfig.json` に `"types": ["vitest/globals"]` を追加することで型補完も有効になる。
2. **`pool: 'forks'` + `singleFork: true`** — better-sqlite3はネイティブモジュールのため、ワーカースレッド（`threads` プール）で動かすと問題が起きることがある。`forks` モードで安定動作する。
3. **カバレッジプロバイダー `v8`** — `@vitest/coverage-v8` をインストールする必要がある。`istanbul` より軽量。

### テストでのDB設定（インメモリSQLite）

```typescript
// src/__tests__/todos.test.ts
import { describe, it, expect, beforeAll, afterEach } from 'vitest'
import request from 'supertest'
import Database from 'better-sqlite3'
import { drizzle } from 'drizzle-orm/better-sqlite3'
import { migrate } from 'drizzle-orm/better-sqlite3/migrator'
import * as schema from '../db/schema.js'
import { createApp } from '../app.js'
import path from 'node:path'
import { fileURLToPath } from 'node:url'

// テスト用インメモリDB
const __dirname = fileURLToPath(new URL('.', import.meta.url))

// DI（依存性注入）パターン: app.ts を修正してdbを注入できるようにする
// 例: createApp(db) の形にするとテストが容易になる
```

**テスト用DBの推奨パターン:**

テストでは、本番DBを汚染しないために `':memory:'` を使ったインメモリSQLiteを使います。そのために `createApp()` はDBインスタンスを引数として受け取れるよう設計するのが理想的です。

```typescript
// app.ts を修正
import { drizzle } from 'drizzle-orm/better-sqlite3'
import type { BetterSQLite3Database } from 'drizzle-orm/better-sqlite3'
import * as schema from './db/schema.js'

type AppDB = BetterSQLite3Database<typeof schema>

export function createApp(db: AppDB) {
  const app = express()
  // ... db を各ルートに渡す
  return app
}
```

```typescript
// vitest セットアップ例
import Database from 'better-sqlite3'
import { drizzle } from 'drizzle-orm/better-sqlite3'
import { migrate } from 'drizzle-orm/better-sqlite3/migrator'
import * as schema from '../db/schema.js'

let testDb: ReturnType<typeof drizzle>

beforeAll(() => {
  const sqlite = new Database(':memory:')
  sqlite.pragma('foreign_keys = ON')
  testDb = drizzle(sqlite, { schema })
  migrate(testDb, { migrationsFolder: './drizzle' })
})

afterEach(() => {
  // テスト後にデータをクリア
  testDb.delete(schema.todos).run()
})
```

---

## 9. マイグレーション運用

```bash
# スキーマからマイグレーションファイルを生成
npm run db:generate

# マイグレーションを適用
npm run db:migrate

# スキーマ変更後は再生成
npm run db:generate -- --name add_user_id
```

生成されるファイル例:
```
drizzle/
├── 0000_initial.sql
├── 0001_add_user_id.sql
└── meta/
    ├── _journal.json
    └── 0000_snapshot.json
```

### 重要: マイグレーションファイルはGit管理する

`drizzle/` ディレクトリはGitにコミットしてください。これによりチームメンバーが同じスキーマ変更を適用できます。

---

## 10. よくある落とし穴と対処法

### ESMでの `__dirname` / `__filename`

ESMモジュールでは `__dirname` が使えません。代わりに以下を使います:

```typescript
import { fileURLToPath } from 'node:url'
import path from 'node:path'

const __filename = fileURLToPath(import.meta.url)
const __dirname = path.dirname(__filename)
```

### better-sqlite3 と ESM

`better-sqlite3` はCommonJSモジュールです。`"type": "module"` の場合でも、Node.jsのESM→CJS相互運用機能により `import Database from 'better-sqlite3'` で読み込めます。

### drizzle-kit の `dialect` vs `driver`

drizzle-kit 0.21.0以降でAPIが変更されました。旧バージョンのドキュメントをそのまま使うと動きません:

```typescript
// 旧（非推奨・エラーになる場合がある）
export default {
  driver: 'better-sqlite',
  dbCredentials: { url: './dev.db' }
}

// 新（推奨）
export default defineConfig({
  dialect: 'sqlite',
  dbCredentials: { url: './dev.db' }
})
```

### Express 5 と `res.json()` の後の `return`

Express 5でも、ルートハンドラ内でレスポンス送信後に処理を続けないよう `return` は必要です:

```typescript
// NG: ヘッダー送信後にレスポンスを送ろうとしてエラーになる
router.get('/', async (req, res) => {
  if (!req.query.id) {
    res.status(400).json({ error: 'id required' })
    // return がないため処理が続く
  }
  const result = await db.select()... // ここも実行されてしまう
  res.json(result)
})

// OK
router.get('/', async (req, res) => {
  if (!req.query.id) {
    res.status(400).json({ error: 'id required' })
    return
  }
  const result = await db.select()...
  res.json(result)
})
```

### Vitest と Node.js のネイティブモジュール

`better-sqlite3` のようなネイティブモジュールをVitestで使うときは `pool: 'forks'` を指定してください。デフォルトの `threads` プールはV8ワーカースレッドを使うため、ネイティブバインディングと相性が悪いことがあります。

### `drizzle-orm` の returning() と SQLite

`returning()` はSQLite 3.35.0以降で対応しています。`better-sqlite3` に同梱されているSQLiteは通常この要件を満たしていますが、システムインストールのSQLiteを使う場合は注意してください。

---

## 11. 完成した `package.json` の全体像

```json
{
  "name": "my-api",
  "version": "1.0.0",
  "type": "module",
  "engines": {
    "node": ">=24.0.0"
  },
  "scripts": {
    "dev": "tsx watch src/index.ts",
    "build": "tsc --build",
    "start": "node dist/index.js",
    "db:generate": "drizzle-kit generate",
    "db:migrate": "drizzle-kit migrate",
    "db:push": "drizzle-kit push",
    "db:studio": "drizzle-kit studio",
    "test": "vitest run",
    "test:watch": "vitest",
    "test:coverage": "vitest run --coverage",
    "typecheck": "tsc --noEmit"
  },
  "dependencies": {
    "better-sqlite3": "^11.0.0",
    "drizzle-orm": "^0.38.0",
    "express": "^5.0.0"
  },
  "devDependencies": {
    "@types/better-sqlite3": "^7.6.0",
    "@types/express": "^5.0.0",
    "@types/node": "^22.0.0",
    "@vitest/coverage-v8": "^2.0.0",
    "drizzle-kit": "^0.29.0",
    "tsx": "^4.0.0",
    "typescript": "^5.0.0",
    "vitest": "^2.0.0"
  }
}
```

---

## 12. セットアップ手順まとめ

```bash
# 1. プロジェクト作成
mkdir my-api && cd my-api
npm init -y

# 2. 依存関係インストール
npm install express better-sqlite3 drizzle-orm
npm install -D typescript tsx @types/node @types/express @types/better-sqlite3 \
  drizzle-kit vitest @vitest/coverage-v8

# 3. 設定ファイルを作成（tsconfig.json, drizzle.config.ts, vitest.config.ts）

# 4. スキーマ定義 (src/db/schema.ts)

# 5. 初回マイグレーション生成
npm run db:generate

# 6. 開発サーバー起動
npm run dev

# 7. テスト実行
npm test
```

---

## 参考: Node.js 24 固有の機能

Node.js 24（2024年4月リリース）の主な特徴:

- **`--experimental-strip-types`** フラグ（Node.js 22.6で追加、24で改善）: TypeScriptファイルを直接実行可能（型アノテーションをstrip）。ただし、型チェックは行われないため開発用途のみ。本番では引き続きtsxやtscを使うことを推奨。
- **V8エンジンの更新**: 最新のJavaScript機能（`Promise.withResolvers`, `Array.fromAsync` 等）をサポート。
- **`node:` プレフィックス推奨**: 標準ライブラリのimportには `import path from 'node:path'` のように `node:` プレフィックスをつけることを推奨（組み込みモジュールとnpmパッケージの区別が明確になる）。
