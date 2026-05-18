# `SqliteError: no such table: todos` の原因と修正方法

## 根本原因

このエラーは **マイグレーションが実行される前にテストが走ってしまう** ことで発生します。具体的には以下の 2 つの問題が絡み合っています。

---

## 問題 1: `db` インスタンスの生成タイミングとスコープ

`vitest.config.ts` で `env: { DB_FILE: ':memory:' }` を設定していても、`db` インスタンスをモジュールのトップレベルで生成している場合、**環境変数が注入されるより前に `db` が初期化されてしまう**ことがあります。

```ts
// bad: モジュール評価時（環境変数注入前）に実行される
const db = drizzle(new Database(process.env.DB_FILE!))
```

さらに `:memory:` の SQLite は **接続ごとに独立したデータベース**を持ちます。`migrate()` を呼び出した `db` インスタンスと、テストで実際にクエリを投げる `db` インスタンスが別オブジェクトであれば、テスト側のインスタンスにはテーブルが存在しません。

---

## 問題 2: `beforeAll` の非同期処理を `await` していない

Drizzle の `migrate()` は `Promise` を返します。`beforeAll` コールバック内で `await` せずに呼び出すと、マイグレーション完了前にテストが開始されます。

```ts
// bad: await 忘れ
beforeAll(() => {
  migrate(db, { migrationsFolder: './drizzle' }) // Promise を無視
})
```

---

## 修正方法

### 修正 1: `db` をシングルトンとして遅延生成し、同じインスタンスを使い回す

```ts
// src/db.ts
import Database from 'better-sqlite3'
import { drizzle } from 'drizzle-orm/better-sqlite3'

// インスタンスはモジュール評価時に 1 度だけ生成
const sqlite = new Database(process.env.DB_FILE ?? ':memory:')
export const db = drizzle(sqlite)
```

テストと本番コードの両方がこの `db` を `import` することで、同一接続を参照します。

### 修正 2: `beforeAll` で `await` する

```ts
// setup.ts
import { migrate } from 'drizzle-orm/better-sqlite3/migrator'
import { db } from '../src/db'

beforeAll(async () => {
  await migrate(db, { migrationsFolder: './drizzle' })
})
```

### 修正 3: `vitest.config.ts` に `setupFiles` を登録する

```ts
// vitest.config.ts
import { defineConfig } from 'vitest/config'

export default defineConfig({
  test: {
    environment: 'node',
    env: { DB_FILE: ':memory:' },
    setupFiles: ['./setup.ts'],  // ← これがないと setup.ts は実行されない
  },
})
```

`setupFiles` に指定しないと `setup.ts` は実行されず、マイグレーション自体が走りません。

---

## よくある追加パターン: テスト間のデータ汚染を防ぐ

`:memory:` DB はプロセス内で共有されるため、テストスイート間でデータが残ります。各テスト後にリセットするには次のいずれかを使います。

```ts
// 方法 A: テーブルを truncate する
afterEach(async () => {
  await db.delete(todos)
})

// 方法 B: DB 自体を再生成する（コストは高いが確実）
let db: ReturnType<typeof drizzle>
beforeEach(async () => {
  const sqlite = new Database(':memory:')
  db = drizzle(sqlite)
  await migrate(db, { migrationsFolder: './drizzle' })
})
```

---

## まとめ: チェックリスト

| # | 確認項目 | 修正方法 |
|---|----------|----------|
| 1 | `beforeAll` で `await migrate(...)` しているか | `async` + `await` を追加 |
| 2 | `setupFiles` に `setup.ts` を登録しているか | `vitest.config.ts` に追記 |
| 3 | マイグレーションとテストで同じ `db` インスタンスを使っているか | シングルトンモジュールに切り出す |
| 4 | テスト間でデータが汚染されていないか | `afterEach` でテーブルをリセット |
