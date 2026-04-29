# Prisma ORM — Patterns & Pitfalls

Prisma v5.x / Node.js 24 + TypeScript 5.8

## セットアップ

```bash
npm install prisma @prisma/client
npx prisma init --datasource-provider postgresql
```

`prisma/schema.prisma`:
```prisma
datasource db {
  provider = "postgresql"
  url      = env("DATABASE_URL")
}

generator client {
  provider = "prisma-client-js"
}

model Todo {
  id        Int      @id @default(autoincrement())
  title     String
  done      Boolean  @default(false)
  createdAt DateTime @default(now())
}
```

---

## シングルトンクライアント（必須）

```ts
// src/db/client.ts
import { PrismaClient } from '@prisma/client'

// モジュール単位でインスタンスを1つだけ作成
export const prisma = new PrismaClient()

// development 環境でのホットリロード対策
if (process.env.NODE_ENV !== 'production') {
  const g = global as typeof globalThis & { prisma?: PrismaClient }
  g.prisma = g.prisma ?? prisma
}
```

**なぜシングルトンか:** PrismaClient は内部で接続プールを管理。リクエストごとに `new PrismaClient()` するとプール枯渇になる。

---

## マイグレーション

| コマンド | 用途 | 動作 |
|---|---|---|
| `prisma migrate dev` | 開発 | shadow DB を使い差分 SQL を生成・適用 |
| `prisma migrate deploy` | 本番/CI | 保留中のマイグレーションのみ適用（破壊的操作なし） |
| `prisma migrate reset` | 開発のみ | DB を削除→再作成→全マイグレーション適用 |
| `prisma db push` | プロトタイピング | マイグレーションファイルなしで schema を直接 push |

**本番では絶対に `migrate dev` を実行しない** — shadow DB の作成・削除が発生し危険。

---

## N+1 クエリの回避

```ts
// NG — N+1: todos を取得後、各 todo のタグを個別取得
const todos = await prisma.todo.findMany()
for (const todo of todos) {
  todo.tags = await prisma.tag.findMany({ where: { todoId: todo.id } })
}

// OK — include で1クエリ
const todos = await prisma.todo.findMany({
  include: { tags: true },
})

// OK — select で必要なフィールドのみ（include より効率的）
const todos = await prisma.todo.findMany({
  select: {
    id: true,
    title: true,
    tags: { select: { name: true } },
  },
})
```

---

## トランザクション

```ts
// バッチトランザクション（独立した操作）
const [todo, log] = await prisma.$transaction([
  prisma.todo.create({ data: { title: 'Buy milk' } }),
  prisma.activityLog.create({ data: { action: 'create_todo' } }),
])

// インタラクティブトランザクション（条件分岐あり）
await prisma.$transaction(async (tx) => {
  const todo = await tx.todo.create({ data: { title: 'test' } })
  if (!todo) throw new Error('creation failed')
  await tx.activityLog.create({ data: { todoId: todo.id } })
})
```

---

## サーバーレス・コネクション問題

Lambda/Vercel/Cloud Run などのサーバーレス環境では、コールドスタートのたびに新しいプロセスが起動し `new PrismaClient()` が繰り返される。

**解決策:**
1. **Prisma Accelerate** (推奨): マネージド接続プールサービス
2. **pgBouncer** + 接続文字列に `?pgbouncer=true&connection_limit=1` を追加:
   ```
   DATABASE_URL="postgresql://user:pass@host:6432/db?pgbouncer=true&connection_limit=1"
   ```

---

## DateTime JSON シリアライズの落とし穴

Prisma の `DateTime` フィールドは TypeScript では `Date` 型。`res.json()` で返すと ISO 文字列になるが、受け取り側が `Date` 型として扱えなくなる。

```ts
// Prisma から返る型
type Todo = { id: number; createdAt: Date }

// res.json() でシリアライズすると
// { "id": 1, "createdAt": "2026-04-29T00:00:00.000Z" } — string!

// 必要なら explicit に変換
const response = { ...todo, createdAt: todo.createdAt.toISOString() }
res.json(response)
```

---

## テスト戦略

### 推奨: Testcontainers + Vitest (CI)

```ts
// vitest.setup.ts
import { PostgreSqlContainer } from '@testcontainers/postgresql'

let container: StartedPostgreSqlContainer

beforeAll(async () => {
  container = await new PostgreSqlContainer().start()
  process.env.DATABASE_URL = container.getConnectionUri()
  // prisma migrate deploy
})

afterAll(async () => {
  await container.stop()
})
```

### 簡易: $transaction + rollback（各テストをトランザクションで包む）

```ts
let tx: PrismaClient

beforeEach(async () => {
  tx = await prisma.$transaction(async (t) => t, { timeout: 30000 })
})

afterEach(async () => {
  await tx.$executeRaw`ROLLBACK`
})
```

---

## Prisma vs Drizzle 選択基準

| 観点 | Prisma を選ぶ | Drizzle を選ぶ |
|---|---|---|
| スキーマ定義 | `.prisma` ファイル（可読性高い） | TypeScript ファイル（コード補完強力） |
| バンドルサイズ | 重い（クエリエンジンバイナリ +15〜50MB） | 軽量（バイナリなし） |
| サーバーレス | Accelerate が必要 | ネイティブ対応 |
| GUI ツール | Prisma Studio あり | なし |
| SQL の透過性 | 抽象化されている | SQL-transparent |
| 型安全性 | コード生成ベース | TypeScript 直接推論 |

## 参考リンク

- [Prisma ドキュメント](https://www.prisma.io/docs)
- [Prisma Accelerate](https://www.prisma.io/accelerate)
- [Testcontainers for Node.js](https://testcontainers.com/guides/getting-started-with-testcontainers-for-nodejs/)
