# Node.js 24 + TypeScript 5.8 — Pitfalls & Patterns

## 推奨 tsconfig.json

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

**なぜこの設定か:**
- `target: ES2022` — ES2024 を指定すると drizzle-kit (esbuild v0.19) が設定ファイルのコンパイル時にエラーを出す。Node.js 24 はほぼすべての ES2024 構文をネイティブサポートするため、実害はない
- `module: NodeNext` + `moduleResolution: NodeNext` — Node.js ランタイムのモジュール解決と一致。`bundler` は extension-less import を許可するが Node.js ランタイムで失敗する
- `erasableSyntaxOnly: true` — Node.js 24 のネイティブ type-stripping に合わせ、ランタイム変換が必要な構文（enum, namespace with values, parameter decorators）をコンパイル時に禁止
- `verbatimModuleSyntax: true` — type-only symbol に `import type`/`export type` を強制。strip-types 時の不正動作を防ぐ
- `noUncheckedIndexedAccess: true` — 配列・オブジェクトの添字アクセスに `undefined` を含める

## 推奨 package.json

```json
{
  "type": "module",
  "engines": { "node": ">=24.0.0" }
}
```

## 重大な落とし穴

### 1. tsconfig.json の paths はランタイムで無視される

Node.js 24 は `tsconfig.json` を一切読まない。`paths: { "@/*": ["./src/*"] }` 等のエイリアスはコンパイルは通るが、ランタイムで `Cannot find module '@/...'` エラーになる。

**解決策:** `package.json` の `imports` フィールドを使う:
```json
{
  "imports": {
    "#db/*": "./src/db/*.js",
    "#routes/*": "./src/routes/*.js"
  }
}
```
tsconfig は `paths: { "#db/*": ["./src/db/*.ts"] }` で型チェックのみに使用。

### 2. import パスに .ts 拡張子が必須

```ts
// NG — Node.js が解決できない
import { db } from './db/client'

// OK
import { db } from './db/client.ts'
```

### 3. __dirname / __filename は ESM で未定義

```ts
// NG — ReferenceError: __dirname is not defined
const dir = path.join(__dirname, 'drizzle')

// OK — Node.js 21.2+ で利用可能
const dir = path.join(import.meta.dirname, 'drizzle')

// 互換性が必要な場合（Node.js 20 以前）
import { fileURLToPath } from 'node:url'
const __dirname = path.dirname(fileURLToPath(import.meta.url))
```

### 4. import type / export type の両方が必要

`verbatimModuleSyntax: true` では、型のみのシンボルは import も export も type キーワードが必要:

```ts
// NG — verbatimModuleSyntax エラー
import { Todo, db } from './db/client.ts'
export { Todo }

// OK
import type { Todo } from './db/client.ts'
import { db } from './db/client.ts'
export type { Todo }
```

### 5. erasableSyntaxOnly で禁止される構文

以下は `--experimental-transform-types` なしでは使用不可:
- `enum` → `as const` オブジェクトまたは文字列リテラル Union に置換
- `namespace` with values → plain オブジェクトに置換
- Parameter decorators (`@Body()`, `@Injectable()`) → plain function arguments に置換
- Decorator-based routing libraries (routing-controllers, tsyringe) → 非対応

```ts
// NG — enum は erasableSyntaxOnly で禁止
enum Status { Active, Inactive }

// OK — as const で代替
const Status = { Active: 'active', Inactive: 'inactive' } as const
type Status = typeof Status[keyof typeof Status]
```

### 6. JSON import assertions の変更

Node.js 22+ では `assert` → `with` へ変更:

```ts
// NG — Node.js 22+ で警告、将来廃止
import data from './data.json' assert { type: 'json' }

// OK
import data from './data.json' with { type: 'json' }
```

### 7. tsx watch (開発) と Node.js 24 ネイティブ type-stripping の関係

`tsx watch src/server.ts` は Node.js 24 のネイティブ type-stripping よりも先に実行を横取りする。これは**意図的な動作**:
- tsx は enum, decorator 等 erasableSyntaxOnly で禁止された構文も処理できる
- 開発時は tsx を使い、本番ビルドは tsup（erasableSyntaxOnly 準拠）で行うことで開発体験と本番安全性を両立
- 本番で tsx を使う場合は `--experimental-transform-types` フラグが必要

ローダー協調が必要な場合（既存の `--import` フックと共存）:
```bash
node --import tsx/esm src/server.ts
```

## Node.js 24 の主要新機能

| 機能 | 詳細 |
|---|---|
| Native type-stripping | `.ts` ファイルをデフォルトで直接実行（erasable syntax のみ） |
| `--experimental-transform-types` | enum/namespace/decorators のランタイム変換（不安定） |
| `import.meta.dirname` | ESM での `__dirname` 相当 (Node.js 21.2+) |
| V8 13.6 | `RegExp.escape()`, `Error.isError()` |
| Fetch / URLPattern | 安定版 |
| `--permission` | パーミッションモデル（`--experimental-permission` から昇格） |

## OpenSSL 3.5 暗号制限

Node.js 24 は OpenSSL 3.5 を使用。以下が**デフォルト拒否**:
- RSA/DSA/DH 鍵長 < 2048 bit
- ECC 鍵長 < 224 bit
- RC4

JWT ライブラリ（jsonwebtoken 等）が短い RSA 鍵を使っている場合は要確認。

## 参考リンク

- [Node.js 24.0.0 リリースノート](https://nodejs.org/en/blog/release/v24.0.0)
- [Node.js TypeScript ドキュメント](https://nodejs.org/api/typescript.html)
- [TypeScript 5.8 リリースノート](https://devblogs.microsoft.com/typescript/announcing-typescript-5-8/)
- [TypeScript tsconfig nodeNext](https://www.typescriptlang.org/tsconfig/moduleResolution.html)
