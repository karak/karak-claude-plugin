# `SqliteError: no such table: todos` の原因と修正

## 問題の診断

提示されたテスト設定には **3 つの問題** が重なっています。

---

## 問題 1: `pool: 'forks'` が未設定（最重要）

`better-sqlite3` はネイティブアドオン（`.node` バイナリ）です。  
Vitest のデフォルト pool は `'threads'`（worker_threads）ですが、worker_threads は V8 ヒープを共有するためネイティブアドオンがセグメンテーションフォルトやテーブル未発見エラーを引き起こします。

**`pool: 'forks'` は better-sqlite3 を使うすべての Vitest 設定で必須・非交渉です。**

---

## 問題 2: `setupFiles` が未指定

`migrate()` を呼んでいる `setup.ts` が、`vitest.config.ts` の `setupFiles` に登録されていません。  
登録されていない setup ファイルはテスト実行前に呼ばれないため、マイグレーションが適用されずテーブルが存在しない状態でテストが走ります。

---

## 問題 3: `migrationsFolder` のパスが相対パスのまま

`migrate(db, { migrationsFolder: './drizzle' })` の相対パスは、テスト実行時の **カレントディレクトリ** に依存します。  
ESM 環境では `__dirname` が未定義のため、`import.meta.dirname` を使って絶対パスに変換しなければなりません。

---

## 修正後のコード

### `vitest.config.ts`

```ts
import { defineConfig } from 'vitest/config'

export default defineConfig({
  test: {
    // better-sqlite3 (native addon) には forks が必須
    pool: 'forks',
    environment: 'node',
    env: { DB_FILE: ':memory:' },
    // setup ファイルを登録する
    setupFiles: ['./src/__tests__/setup.ts'],
  },
})
```

### `src/__tests__/setup.ts`

```ts
import { existsSync } from 'node:fs'
import { join } from 'node:path'
import { beforeAll } from 'vitest'  // setupFiles では globals が自動注入されないため明示的 import
import { migrate } from 'drizzle-orm/better-sqlite3/migrator'
import { db } from '../db/client.ts'

// import.meta.dirname で絶対パスに変換（ESM では __dirname は未定義）
const migrationsFolder = join(import.meta.dirname, '../../drizzle')

beforeAll(() => {
  if (!existsSync(migrationsFolder)) {
    throw new Error('Run `npm run generate` before `npm test`.')
  }
  // drizzle-kit CLI は :memory: DB に届かないため、プログラム内で migrate() を使う
  migrate(db, { migrationsFolder })
})
```

---

## 各変更点のまとめ

| 変更箇所 | 変更前 | 変更後 | 理由 |
|---|---|---|---|
| `vitest.config.ts` | `pool` 未設定（= `'threads'`） | `pool: 'forks'` | better-sqlite3 native addon の必須要件 |
| `vitest.config.ts` | `setupFiles` 未設定 | `setupFiles: ['./src/__tests__/setup.ts']` | setup ファイルをテスト前に実行させる |
| `setup.ts` | `migrationsFolder: './drizzle'`（相対パス） | `join(import.meta.dirname, '../../drizzle')`（絶対パス） | カレントディレクトリ依存を排除 |
| `setup.ts` | `import` なしで `beforeAll` を使用 | `import { beforeAll } from 'vitest'` を明示 | setupFiles では Vitest globals が自動注入されない |

---

## 補足: `drizzle-kit migrate` と `:memory:` の非互換

`drizzle-kit migrate` はコマンドラインから **別プロセス** として起動し、ファイル DB に接続します。  
インメモリ DB（`':memory:'`）は別プロセスから接続できないため、テストでは必ず `drizzle-orm/better-sqlite3/migrator` の `migrate()` 関数をプログラム内で呼び出してください。

---

## `pool: 'forks'` の分離特性について

`pool: 'forks'` では各テストファイルが独立した child process で実行されます。  
これにより `:memory:` DB はファイル間で自然に分離されます。  
同一ファイル内のテスト間でデータを分離したい場合は `beforeEach` でテーブルをクリアしてください。

```ts
import { beforeEach } from 'vitest'
import { db } from '../db/client.ts'
import { todos } from '../db/schema.ts'

beforeEach(() => {
  db.delete(todos).run()  // 同期（better-sqlite3）
})
```
