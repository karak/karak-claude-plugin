# Node.js 24 + Express 5 + Drizzle ORM + better-sqlite3 + Vitest 新規プロジェクトセットアップ

## 前提

- Node.js 24（ESM ネイティブ対応、`--experimental-strip-types` によるネイティブ TypeScript 実行が利用可能）
- TypeScript 5.x
- パッケージマネージャー: npm または pnpm

---

## 1. ディレクトリ構造

```
my-api/
├── src/
│   ├── db/
│   │   ├── schema.ts        # Drizzle スキーマ定義
│   │   └── index.ts         # DB 接続
│   ├── routes/
│   │   └── todos.ts
│   ├── app.ts               # Express アプリ定義（サーバー起動なし）
│   └── server.ts            # エントリポイント（listen）
├── tests/
│   └── todos.test.ts
├── drizzle/                 # マイグレーションファイル（自動生成）
├── drizzle.config.ts
├── package.json
├── tsconfig.json
└── vitest.config.ts
```

---

## 2. package.json

```json
{
  "name": "my-api",
  "version": "0.1.0",
  "type": "module",
  "engines": {
    "node": ">=24"
  },
  "scripts": {
    "dev": "node --watch --experimental-strip-types src/server.ts",
    "build": "tsc -p tsconfig.build.json",
    "start": "node dist/server.js",
    "db:generate": "drizzle-kit generate",
    "db:migrate": "drizzle-kit migrate",
    "db:studio": "drizzle-kit studio",
    "test": "vitest run",
    "test:watch": "vitest",
    "test:coverage": "vitest run --coverage"
  },
  "dependencies": {
    "better-sqlite3": "^9.4.3",
    "drizzle-orm": "^0.30.10",
    "express": "^5.0.1"
  },
  "devDependencies": {
    "@types/better-sqlite3": "^7.6.10",
    "@types/express": "^5.0.0",
    "@types/node": "^20.12.0",
    "@vitest/coverage-v8": "^1.6.0",
    "drizzle-kit": "^0.21.4",
    "typescript": "^5.4.5",
    "vitest": "^1.6.0"
  }
}
```

### 重要ポイント

- **`"type": "module"`** を必ず設定する。Node.js 24 + ESM の組み合わせではこれが前提となり、`import/export` 構文がそのまま使える。
- **`--experimental-strip-types`** を `dev` スクリプトで使うと、`tsc` ビルドなしに TypeScript を直接実行できる（Node.js 22.6+ で導入、24 では安定度が向上）。ただし型チェックは行わないため、CI では別途 `tsc --noEmit` を走らせること。
- Express 5 は 2024 年に正式リリース済み。`@types/express` も v5 対応版（`^5.0.0`）を使う。

---

## 3. tsconfig.json

```json
{
  "compilerOptions": {
    "target": "ES2022",
    "module": "NodeNext",
    "moduleResolution": "NodeNext",
    "outDir": "dist",
    "rootDir": "src",
    "strict": true,
    "esModuleInterop": true,
    "skipLibCheck": true,
    "resolveJsonModule": true,
    "declaration": true,
    "declarationMap": true,
    "sourceMap": true
  },
  "include": ["src"],
  "exclude": ["node_modules", "dist", "tests"]
}
```

### 重要ポイント

- **`module: "NodeNext"` + `moduleResolution: "NodeNext"`** のペアが ESM + Node.js で必須。`"module": "ESNext"` + `"moduleResolution": "Bundler"` はバンドラー向けであり、Node.js 直接実行では使わない。
- `NodeNext` を使うと TypeScript は `.js` 拡張子付きのインポートを要求する（`import { foo } from './foo.js'`）。これが ESM の仕様に沿った正しい書き方。
- テスト用に型チェックを通したい場合は `tsconfig.test.json` で `include: ["src", "tests"]` を追加する。
- ビルド専用の `tsconfig.build.json` を用意し `extends: "./tsconfig.json"` + `exclude: ["tests"]` とするのがベストプラクティス。

---

## 4. Drizzle 設定

### src/db/schema.ts

```typescript
import { sqliteTable, text, integer } from 'drizzle-orm/sqlite-core';

export const todos = sqliteTable('todos', {
  id: integer('id').primaryKey({ autoIncrement: true }),
  title: text('title').notNull(),
  completed: integer('completed', { mode: 'boolean' }).notNull().default(false),
  createdAt: integer('created_at', { mode: 'timestamp' })
    .notNull()
    .$defaultFn(() => new Date()),
});

export type Todo = typeof todos.$inferSelect;
export type NewTodo = typeof todos.$inferInsert;
```

### src/db/index.ts

```typescript
import Database from 'better-sqlite3';
import { drizzle } from 'drizzle-orm/better-sqlite3';
import * as schema from './schema.js';

const DB_PATH = process.env.DATABASE_URL ?? 'local.db';

const sqlite = new Database(DB_PATH);
sqlite.pragma('journal_mode = WAL');
sqlite.pragma('foreign_keys = ON');

export const db = drizzle(sqlite, { schema });
```

### drizzle.config.ts

```typescript
import type { Config } from 'drizzle-kit';

export default {
  schema: './src/db/schema.ts',
  out: './drizzle',
  dialect: 'sqlite',
  dbCredentials: {
    url: process.env.DATABASE_URL ?? 'local.db',
  },
} satisfies Config;
```

### 重要ポイント

- **`dialect: 'sqlite'`** は drizzle-kit 0.21 以降で必須フィールドになった（旧来の `driver` フィールドは非推奨）。
- **`sqlite.pragma('journal_mode = WAL')`** は better-sqlite3 使用時のパフォーマンス推奨設定。読み取り並行性が向上する。
- **`$inferSelect` / `$inferInsert`** で型を自動導出しておくと、ルートハンドラでの型安全性が保たれる。
- テスト時は `DATABASE_URL=':memory:'` を環境変数に設定してインメモリ DB を使う。

---

## 5. Express 5 アプリ定義

### src/app.ts

```typescript
import express from 'express';
import { todosRouter } from './routes/todos.js';

export const app = express();

app.use(express.json());

app.get('/health', (_req, res) => {
  res.json({ status: 'ok' });
});

app.use('/todos', todosRouter);

// Express 5: エラーハンドラは 4 引数。async ルートの throw は自動的にここへ伝搬する
app.use(
  (
    err: Error,
    _req: express.Request,
    res: express.Response,
    _next: express.NextFunction,
  ) => {
    console.error(err);
    res.status(500).json({ error: err.message });
  },
);
```

### src/server.ts

```typescript
import { app } from './app.js';

const PORT = process.env.PORT ?? 3000;
app.listen(PORT, () => {
  console.log(`Server running on http://localhost:${PORT}`);
});
```

### Express 5 の重要変更点

- **async ルートのエラー自動伝搬**: Express 5 では async 関数内で `throw` または rejected Promise が発生すると、自動的に `next(err)` が呼ばれる。`try/catch` + `next(err)` の手動記述が不要になった。
- **`path-to-regexp` v8 採用**: ワイルドカード構文が変わった（`*` → `(.*)` または `{*path}`）。`app.use('*', ...)` は `app.use('*path', ...)` または `app.use('/{*path}', ...)` に変更。
- **`res.json()` 等の戻り値**: Express 5 では `res.json()` が `void` ではなく `Promise<void>` を返す場合があるが、`return` しないのが通常パターン。

---

## 6. Vitest 設定

### vitest.config.ts

```typescript
import { defineConfig } from 'vitest/config';

export default defineConfig({
  test: {
    globals: true,
    environment: 'node',
    setupFiles: ['./tests/setup.ts'],
    coverage: {
      provider: 'v8',
      reporter: ['text', 'lcov', 'html'],
      include: ['src/**/*.ts'],
      exclude: ['src/server.ts', 'src/db/index.ts'],
    },
    // ESM 環境では pool を 'forks' にすると安定しやすい
    pool: 'forks',
  },
});
```

### tests/setup.ts

```typescript
import { migrate } from 'drizzle-orm/better-sqlite3/migrator';
import Database from 'better-sqlite3';
import { drizzle } from 'drizzle-orm/better-sqlite3';
import * as schema from '../src/db/schema.js';

// テスト全体でインメモリ DB を共有する場合
// 各テストファイルで個別に作る場合はここではなくヘルパー関数を用意する
process.env.DATABASE_URL = ':memory:';
```

### テスト例: tests/todos.test.ts

```typescript
import { describe, it, expect, beforeEach } from 'vitest';
import request from 'supertest';  // npm i -D supertest @types/supertest
import Database from 'better-sqlite3';
import { drizzle } from 'drizzle-orm/better-sqlite3';
import { migrate } from 'drizzle-orm/better-sqlite3/migrator';
import * as schema from '../src/db/schema.js';
import express from 'express';
import { buildTodosRouter } from '../src/routes/todos.js';

// テストごとにクリーンなインメモリ DB を作成
function createTestDb() {
  const sqlite = new Database(':memory:');
  const db = drizzle(sqlite, { schema });
  migrate(db, { migrationsFolder: './drizzle' });
  return { db, sqlite };
}

describe('GET /todos', () => {
  let app: express.Application;

  beforeEach(() => {
    const { db } = createTestDb();
    app = express();
    app.use(express.json());
    app.use('/todos', buildTodosRouter(db));
  });

  it('空のリストを返す', async () => {
    const res = await request(app).get('/todos');
    expect(res.status).toBe(200);
    expect(res.body).toEqual([]);
  });
});
```

### 重要ポイント

- **`pool: 'forks'`**: Node.js 24 + ESM 環境では `worker_threads` より `forks` の方が ESM の動的インポートとの相性が良い場合がある。問題がなければデフォルト（`threads`）でも動作する。
- **`globals: true`**: `describe/it/expect` をインポートなしで使える。`tsconfig.json` に `"types": ["vitest/globals"]` を追記すると型補完も効く。
- **テスト用 DB の分離**: `beforeEach` でインメモリ DB を毎回作り直すことで、テスト間の状態汚染を防ぐ。`afterEach` でのリセットより確実。
- **ルーターへの DI**: `db` をルーター生成関数の引数として渡す設計にすると、テストで容易にスワップできる（上記 `buildTodosRouter(db)` パターン）。

---

## 7. セットアップ手順まとめ

```bash
# 1. プロジェクト作成
mkdir my-api && cd my-api
npm init -y

# 2. 依存インストール
npm install express drizzle-orm better-sqlite3
npm install -D typescript @types/node @types/express @types/better-sqlite3 \
  drizzle-kit vitest @vitest/coverage-v8 supertest @types/supertest

# 3. tsconfig 作成（上記内容）
# 4. package.json の "type": "module" と scripts を追加

# 5. スキーマ・設定ファイルを作成後、マイグレーション生成
npm run db:generate

# 6. マイグレーション適用（開発 DB）
npm run db:migrate

# 7. 開発サーバー起動
npm run dev

# 8. テスト実行
npm test
```

---

## 8. よくある落とし穴

| 問題 | 原因 | 対処 |
|------|------|------|
| `ERR_REQUIRE_ESM` | `"type":"module"` なのに `require()` を使っている | `import` 構文に統一する |
| `Cannot find module './foo'` | ESM では `.js` 拡張子が必要 | `import from './foo.js'` と書く |
| `drizzle-kit generate` がスキーマを認識しない | `drizzle.config.ts` の `schema` パスが間違い | 相対パスを `./src/db/schema.ts` に修正 |
| Vitest でテストが干渉する | DB 状態がテスト間で残る | `beforeEach` で DB を再生成する |
| Express 5 のルート型エラー | `@types/express` が v4 のまま | `@types/express@^5.0.0` にアップデート |
| `--experimental-strip-types` で型エラーが出ない | 型チェックをスキップしている | `tsc --noEmit` を CI に組み込む |
