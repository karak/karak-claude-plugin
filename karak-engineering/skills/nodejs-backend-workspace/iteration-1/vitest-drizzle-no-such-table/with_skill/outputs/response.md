# `SqliteError: no such table: todos` の原因と修正

## 問題の全体像

提示されたテスト設定には **2 つの独立したバグ** がある。どちらか一方だけでもテストが壊れる。

---

## 問題 1: `pool: 'forks'` が未設定（クラッシュ・不安定動作）

### 現状の設定

```ts
// vitest.config.ts
export default defineConfig({
  test: { environment: 'node', env: { DB_FILE: ':memory:' } }
})
```

`pool` が省略されているため、Vitest はデフォルトの `pool: 'threads'`（worker_threads）を使う。

### なぜ問題か

`better-sqlite3` はネイティブアドオン（`.node` バイナリ）である。
`pool: 'threads'` の worker_threads は V8 ヒープを共有するため、ネイティブアドオンをロードするとセグメンテーションフォルトやメモリ破壊が発生する。
症状は環境によって異なり、クラッシュ・`no such table` エラー・意図しないデータ共有として現れる。

### 修正

```ts
// vitest.config.ts
import { defineConfig } from 'vitest/config'

export default defineConfig({
  test: {
    pool: 'forks',          // ← 追加: better-sqlite3 ネイティブ addon に必須
    environment: 'node',
    env: { DB_FILE: ':memory:' },
    setupFiles: ['./src/__tests__/setup.ts'],
  },
})
```

`pool: 'forks'` では各テストファイルが独立した child_process（fork）で実行される。
ネイティブアドオンは各プロセスに独立してロードされるため安全に動作する。

---

## 問題 2: `migrationsFolder` のパスが相対パスのまま（`no such table` の直接原因）

### 現状の設定

```ts
// setup.ts
beforeAll(() => {
  migrate(db, { migrationsFolder: './drizzle' })
})
```

### なぜ問題か

`'./drizzle'` は **相対パス** であり、Node.js の `fs` API はこれを `process.cwd()` 基準で解決する。
Vitest が `pool: 'forks'` で各テストファイルを実行するとき、`process.cwd()` がプロジェクトルートとは異なるディレクトリになる場合がある。
その結果 `./drizzle` フォルダが見つからず、マイグレーションが一切適用されないまま `db` が空の状態でテストが走る。
テーブルが存在しない状態で `db.select().from(todos)` 等を呼び出すと `SqliteError: no such table: todos` が発生する。

また、ESM 環境では `__dirname` が未定義なので `path.join(__dirname, ...)` も使えない。

### 修正

`import.meta.dirname` を使って setup.ts ファイルの絶対パスを起点にパスを解決する。
さらに、`drizzle` フォルダが存在しない場合（`drizzle-kit generate` 未実行）に分かりやすいエラーを出す guard を追加する。

```ts
// src/__tests__/setup.ts
import { existsSync } from 'node:fs'
import { join } from 'node:path'
import { beforeAll } from 'vitest'  // setupFiles では globals が自動注入されないため明示 import
import { migrate } from 'drizzle-orm/better-sqlite3/migrator'
import { db } from '../db/client.ts'

// import.meta.dirname = このファイル(setup.ts)が置かれているディレクトリの絶対パス
// ../../drizzle = プロジェクトルートの drizzle/ フォルダ
const migrationsFolder = join(import.meta.dirname, '../../drizzle')

beforeAll(() => {
  if (!existsSync(migrationsFolder)) {
    throw new Error(
      `Migration folder not found: ${migrationsFolder}\nRun \`npm run generate\` (drizzle-kit generate) before \`npm test\`.`
    )
  }
  migrate(db, { migrationsFolder })
})
```

---

## 修正後の完全な設定

### `vitest.config.ts`

```ts
import { defineConfig } from 'vitest/config'

export default defineConfig({
  test: {
    pool: 'forks',                              // better-sqlite3 ネイティブ addon 必須
    environment: 'node',
    env: { DB_FILE: ':memory:' },
    setupFiles: ['./src/__tests__/setup.ts'],   // マイグレーション適用
  },
})
```

### `src/__tests__/setup.ts`

```ts
import { existsSync } from 'node:fs'
import { join } from 'node:path'
import { beforeAll } from 'vitest'
import { migrate } from 'drizzle-orm/better-sqlite3/migrator'
import { db } from '../db/client.ts'

const migrationsFolder = join(import.meta.dirname, '../../drizzle')

beforeAll(() => {
  if (!existsSync(migrationsFolder)) {
    throw new Error(
      `Migration folder not found: ${migrationsFolder}\nRun \`npm run generate\` before \`npm test\`.`
    )
  }
  migrate(db, { migrationsFolder })
})
```

---

## テスト間のデータ分離（推奨）

`:memory:` DB は `pool: 'forks'` によってテストファイル単位で分離されるが、
同一ファイル内の複数テストはデータを共有する。テスト間の干渉を防ぐために `beforeEach` でテーブルを空にする。

```ts
import { beforeEach } from 'vitest'
import { db } from '../db/client.ts'
import { todos } from '../db/schema.ts'

beforeEach(() => {
  db.delete(todos).run()  // better-sqlite3 は同期 API なので await 不要
})
```

---

## 問題のまとめ

| # | 問題 | 症状 | 修正 |
|---|---|---|---|
| 1 | `pool: 'forks'` が未設定 | クラッシュ・不安定・no such table | `vitest.config.ts` に `pool: 'forks'` を追加 |
| 2 | `migrationsFolder` が相対パス `'./drizzle'` | マイグレーション未適用 → no such table | `join(import.meta.dirname, '../../drizzle')` で絶対パスに変換 |

問題 2 が `SqliteError: no such table: todos` の直接原因。問題 1 は環境によってはサイレントに問題を引き起こすため、両方の修正が必須。
