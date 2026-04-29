# Drizzle ORM + better-sqlite3 + Vitest: `SqliteError: no such table: todos` の原因と修正

## 問題の概要

`SqliteError: no such table: todos` は、テスト実行時にマイグレーションが適切に完了していないか、マイグレーション対象のDBインスタンスとテストが使うDBインスタンスが異なるために発生します。以下に、考えられる全原因と対処法を示します。

---

## 問題 1: `db` インスタンスの共有問題（最頻出）

### 原因

`setup.ts` の `migrate(db, ...)` で渡している `db` と、実際のテストコードが使う `db` が**別インスタンス**になっている場合です。

`:memory:` データベースは **接続ごとに独立した揮発メモリ空間** を持ちます。別々の `new Database(':memory:')` 呼び出しで作られた接続は、同じ `:memory:` という文字列を指定していても **互いに隔離されており、スキーマを共有しません**。

典型的なアンチパターン:

```ts
// db.ts（アプリ用）
import Database from 'better-sqlite3';
import { drizzle } from 'drizzle-orm/better-sqlite3';

const sqlite = new Database(process.env.DB_FILE!);
export const db = drizzle(sqlite);
```

```ts
// setup.ts
import Database from 'better-sqlite3';
import { drizzle } from 'drizzle-orm/better-sqlite3';
import { migrate } from 'drizzle-orm/better-sqlite3/migrator';

// ← db.ts とは別の new Database(':memory:') → 別インスタンス！
const sqlite = new Database(':memory:');
const db = drizzle(sqlite);

beforeAll(() => {
  migrate(db, { migrationsFolder: './drizzle' });
});
```

```ts
// some.test.ts
import { db } from './db'; // ← migrate されていない別インスタンスを使う
```

### 修正

`db` インスタンスをシングルトンとして一か所で生成し、setup とテスト両方で**同じオブジェクト**をインポートするよう統一する。

```ts
// test/helpers/db.ts（テスト専用のシングルトン）
import Database from 'better-sqlite3';
import { drizzle } from 'drizzle-orm/better-sqlite3';
import { migrate } from 'drizzle-orm/better-sqlite3/migrator';

const sqlite = new Database(':memory:');
export const db = drizzle(sqlite);

// テスト用初期化関数
export function setupTestDb() {
  migrate(db, { migrationsFolder: './drizzle' });
}
```

```ts
// setup.ts
import { setupTestDb } from './helpers/db';

beforeAll(() => {
  setupTestDb();
});
```

```ts
// some.test.ts
import { db } from './helpers/db'; // 同じインスタンスを使う
```

**なぜ重要か:** `:memory:` DB は接続単位でスコープされるため、migrate した接続と異なる接続では常にスキーマが空になります。

---

## 問題 2: `migrate` の非同期処理の扱い

### 原因

Drizzle の `migrate()` は **非同期（Promise を返す）** 関数です。`beforeAll` コールバック内で `await` せずに呼び出すと、マイグレーションが完了する前にテストが走り始めます。

```ts
// NG: await していない
beforeAll(() => {
  migrate(db, { migrationsFolder: './drizzle' }); // Promise を無視
});
```

### 修正

```ts
// OK: async/await で完了を待つ
beforeAll(async () => {
  await migrate(db, { migrationsFolder: './drizzle' });
});
```

**なぜ重要か:** Vitest の `beforeAll` は、コールバックが Promise を返す場合はその解決を待ちます。`await` を省略すると、マイグレーション SQL の実行がテスト開始後に行われる競合状態が生まれます。

---

## 問題 3: `vitest.config.ts` の `env` でのDB_FILE設定タイミング

### 原因

```ts
// vitest.config.ts
export default defineConfig({
  test: { environment: 'node', env: { DB_FILE: ':memory:' } }
})
```

`vitest.config.ts` の `test.env` はワーカープロセスに環境変数を渡しますが、アプリ側の `db.ts` でモジュールロード時（トップレベル）に `process.env.DB_FILE` を読んでいる場合、**モジュールのキャッシュタイミング**によっては環境変数が設定される前にDBインスタンスが生成されることがあります。

```ts
// db.ts（問題のあるパターン）
// モジュール読み込み時に即座にDB接続を確立 → 環境変数が未設定の可能性
const sqlite = new Database(process.env.DB_FILE ?? 'prod.db');
export const db = drizzle(sqlite);
```

### 修正

テスト用にはアプリの `db.ts` から独立した、テスト専用のDB初期化モジュールを使うのがベストプラクティスです（問題1の解決策と同じ）。

あるいは `vitest.config.ts` に `setupFiles` を指定し、環境変数の確実な設定後にDBを初期化する:

```ts
// vitest.config.ts
export default defineConfig({
  test: {
    environment: 'node',
    setupFiles: ['./test/setup.ts'],
    env: { DB_FILE: ':memory:' },
  },
});
```

**なぜ重要か:** `test.env` は Node.js の `process.env` にマージされますが、その前にモジュールが評価されていると変数が読まれません。

---

## 問題 4: `setupFiles` vs `globalSetup` の選択ミス

### 原因

Vitest には2つのセットアップ機構があります:

| 設定キー | 実行タイミング | `db` インスタンスの共有 |
|---|---|---|
| `setupFiles` | 各テストファイルのワーカー内で実行 | テストファイルと同じスコープ（共有可） |
| `globalSetup` | メインプロセスで一度だけ実行 | テストファイルとスコープが異なる（DBは共有不可） |

`globalSetup` 内でインメモリDBをセットアップしても、テストワーカーは別プロセスのため **そのDBインスタンスにアクセスできません**。

### 修正

インメモリDBのセットアップには **`setupFiles`** を使う:

```ts
// vitest.config.ts
export default defineConfig({
  test: {
    environment: 'node',
    setupFiles: ['./test/setup.ts'], // globalSetup ではなく setupFiles
  },
});
```

**なぜ重要か:** `globalSetup` はメインプロセスで動き、テストワーカーとメモリを共有しません。`:memory:` DBはプロセスをまたいで共有できないため、マイグレーション結果がテストから見えません。

---

## 問題 5: マイグレーションファイルのパス解決

### 原因

```ts
migrate(db, { migrationsFolder: './drizzle' })
```

`./drizzle` は**実行時の `cwd`（カレントワーキングディレクトリ）**に対する相対パスです。Vitestがプロジェクトルート以外のディレクトリから実行された場合、または `setupFiles` のパス解決が異なる場合、マイグレーションファイルが見つからず、エラーなく終了した結果スキーマが空になることがあります。

### 修正

`__dirname` または `import.meta.url` を使った絶対パスにする:

```ts
// setup.ts (ESM)
import { fileURLToPath } from 'url';
import path from 'path';

const __dirname = path.dirname(fileURLToPath(import.meta.url));

beforeAll(async () => {
  await migrate(db, {
    migrationsFolder: path.resolve(__dirname, '../drizzle'),
  });
});
```

```ts
// setup.ts (CJS)
beforeAll(async () => {
  await migrate(db, {
    migrationsFolder: path.resolve(__dirname, '../drizzle'),
  });
});
```

**なぜ重要か:** 相対パスは `cwd` 依存であり、CIや異なる実行環境でパス解決が変わるとマイグレーションがサイレントに失敗します。

---

## 修正後の完全な設定例

```ts
// test/helpers/db.ts
import Database from 'better-sqlite3';
import { drizzle } from 'drizzle-orm/better-sqlite3';
import { migrate } from 'drizzle-orm/better-sqlite3/migrator';
import path from 'path';
import { fileURLToPath } from 'url';

const __dirname = path.dirname(fileURLToPath(import.meta.url));

const sqlite = new Database(':memory:');
export const db = drizzle(sqlite);

export async function setupTestDb() {
  await migrate(db, {
    migrationsFolder: path.resolve(__dirname, '../../drizzle'),
  });
}
```

```ts
// test/setup.ts
import { setupTestDb } from './helpers/db';

beforeAll(async () => {
  await setupTestDb();
});
```

```ts
// vitest.config.ts
import { defineConfig } from 'vitest/config';

export default defineConfig({
  test: {
    environment: 'node',
    setupFiles: ['./test/setup.ts'],
    // env.DB_FILE は不要（test/helpers/db.ts 内でハードコード）
  },
});
```

```ts
// some.test.ts
import { db } from './helpers/db'; // 同じシングルトンインスタンス

test('todos テーブルにレコードを挿入できる', async () => {
  // ...
});
```

---

## 原因の優先度まとめ

| 優先度 | 問題 | 症状の特徴 |
|---|---|---|
| 高 | DBインスタンスの非共有（問題1） | 常に発生する |
| 高 | `migrate()` の `await` 忘れ（問題2） | 散発的・タイミング依存で発生 |
| 中 | `globalSetup` の誤用（問題4） | 並列実行時に顕著 |
| 中 | マイグレーションパスの解決失敗（問題5） | CI環境やサブディレクトリ実行時に発生 |
| 低 | 環境変数のタイミング（問題3） | モジュールキャッシュ条件で発生 |

最初に**問題1と問題2**を確認することで、大多数のケースは解決します。
