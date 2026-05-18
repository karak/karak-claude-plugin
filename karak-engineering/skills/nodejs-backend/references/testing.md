# Vitest 3 + supertest — TDD Patterns for Node.js Backends

## Vitest 設定（必須項目）

```ts
// vitest.config.ts
import { defineConfig } from 'vitest/config'

export default defineConfig({
  test: {
    // better-sqlite3 は native addon (.node バイナリ)。
    // pool: 'threads' (worker threads) はネイティブアドオンでクラッシュする。
    // pool: 'forks' (child_process) は必須・非交渉。
    pool: 'forks',
    environment: 'node',

    // テスト時のみ :memory: DB を使用
    // vitest.config.ts の env は pool: forks の各 fork プロセスに注入される
    env: { DB_FILE: ':memory:' },

    // スキーマ適用のセットアップファイル
    setupFiles: ['./src/__tests__/setup.ts'],

    // coverage (任意)
    coverage: { provider: 'v8' },
  },
})
```

**`pool: forks` が必須な理由:**
- `better-sqlite3` はネイティブ addon（`.node` バイナリ）
- `pool: threads`（worker_threads）は V8 ヒープを共有するためネイティブ addon のセグメンテーションフォルトを引き起こす
- `pool: forks` では各テストファイルが独立した child process で実行される

---

## テスト用スキーマセットアップ

```ts
// src/__tests__/setup.ts
import { existsSync } from 'node:fs'
import { join } from 'node:path'
import { beforeAll } from 'vitest'  // setupFiles では globals が自動注入されない
import { migrate } from 'drizzle-orm/better-sqlite3/migrator'
import { db } from '../db/client.ts'

// import.meta.dirname で絶対パスに変換（__dirname は ESM 未定義）
const migrationsFolder = join(import.meta.dirname, '../../drizzle')

beforeAll(() => {
  if (!existsSync(migrationsFolder)) {
    throw new Error('Run `npm run generate` before `npm test`.')
  }
  // プログラム内でマイグレーションを適用（drizzle-kit CLI は :memory: に届かない）
  migrate(db, { migrationsFolder })
})
```

**`beforeAll` でよい理由:**
`pool: forks` では各テストファイルが独立プロセスで実行される。
`beforeAll` は worker（= テストファイル）ごとに1回だけ実行 → `:memory:` DB の分離が自動で保たれる。
`afterEach` や `afterAll` でのテーブル削除は不要。

---

## supertest による HTTP テスト

```ts
import request from 'supertest'
import { app } from '../app.ts'  // listen() しない Express app

// supertest はサーバーをバインドせず in-process でリクエストを処理
const res = await request(app).get('/todos').expect(200)
```

**なぜ `app` を `server.ts` から分離するか:**
- `server.ts`: `app.listen()` を呼ぶエントリーポイント
- `app.ts`: `listen()` なしの Express app（テストでインポート）
- テストで `listen()` を呼ばないことで、ポート競合やプロセス終了処理が不要

---

## TDD サイクル (Red → Green → Refactor)

### 1. Red — テストを先に書く

```ts
// todos.test.ts を先に書く（実装なし = 全失敗）
describe('POST /todos', () => {
  it('creates a todo and returns 201', async () => {
    const res = await request(app).post('/todos').send({ title: 'buy milk' }).expect(201)
    expect(res.body.title).toBe('buy milk')
    expect(res.body.done).toBe(false)
  })
})
```

### 2. Green — テストが通る最小実装

```ts
// todos.ts に最小限のルートを実装
todosRouter.post('/', (req, res) => {
  const inserted = db.insert(todos).values(req.body).returning().get()
  res.status(201).json(inserted)
})
```

### 3. Refactor — コードを改善

入力バリデーション、エラーハンドリングを追加。テストは Green のまま維持。

---

## テストパターン集

### テスト間のデータ分離

```ts
import { beforeEach } from 'vitest'
import { db } from '../db/client.ts'
import { todos } from '../db/schema.ts'

// 各テスト前にテーブルを空にする
beforeEach(() => {
  db.delete(todos).run()   // 同期（better-sqlite3）
})
```

### 404 テスト

```ts
it('returns 404 for unknown id', async () => {
  await request(app).get('/todos/9999').expect(404)
})
```

### 正常系 + 異常系のセット

```ts
describe('PATCH /todos/:id', () => {
  it('updates done status', async () => {
    const created = await request(app).post('/todos').send({ title: 'test' })
    const res = await request(app)
      .patch(`/todos/${created.body.id}`)
      .send({ done: true })
      .expect(200)
    expect(res.body.done).toBe(true)
  })

  it('returns 404 for unknown id', async () => {
    await request(app).patch('/todos/9999').send({ done: true }).expect(404)
  })
})
```

### JSON レスポンス内容検証

```ts
// toBeInTheDocument() だけでなく内容も検証する
expect(res.body.title).toBe('buy milk')
expect(res.body.done).toBe(false)
expect(res.body.id).toBeTypeOf('number')
expect(res.body).toMatchObject({ title: 'buy milk', done: false })
```

---

## コンポーネントテスト志向（goldbergyoni 推奨）

バックエンドのテストは HTTP レイヤー（supertest）で行うことが多い。

| レベル | supertest | 直接関数呼び出し |
|---|---|---|
| テスト対象 | HTTP インターフェース全体 | 個別関数 |
| リグレッション検出 | ルート・ミドルウェア変更を検出 | 内部変更のみ |
| リファクタリング耐性 | 高（外部 I/F に依存） | 低（実装に依存） |
| 推奨度 | ◎ メインテスト | 複雑なビジネスロジック単体 |

---

## mock の配置ルール

- **直接成果 mock**（そのテストだけに影響）→ テスト本体内に inline で書く
- **共有セットアップ**（全テストで必要）→ `beforeAll` または `beforeEach`
- **外部サービス mock**（メール、決済等）→ `vitest.mock()` をファイルの先頭に書く

```ts
import { vi } from 'vitest'

// ファイル先頭: モジュールレベルの mock
vi.mock('../services/email.ts', () => ({
  sendEmail: vi.fn().mockResolvedValue(undefined),
}))

// テスト内: 特定テスト用の動作設定
it('sends welcome email on signup', async () => {
  const { sendEmail } = await import('../services/email.ts')
  vi.mocked(sendEmail).mockResolvedValueOnce(undefined)
  // ...
})
```

---

## Jest vs Vitest (2026年)

**新規プロジェクトは Vitest を選択する。**

| 観点 | Vitest 3 | Jest 30 |
|---|---|---|
| ESM サポート | ネイティブ | 設定が複雑 |
| 速度 | 30〜70% 速い | 標準 |
| TypeScript | 設定不要 | transform 設定要 |
| React Native | ❌ | ✅ |
| 既存コードベース | 移行コスト | そのまま使う |

---

## 参考リンク

- [Vitest ドキュメント](https://vitest.dev/)
- [Vitest pool config](https://vitest.dev/config/#pool)
- [supertest](https://github.com/ladjs/supertest)
- [goldbergyoni/nodejs-testing-best-practices](https://github.com/goldbergyoni/nodejs-testing-best-practices)
