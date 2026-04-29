---
name: nodejs-backend
description: |
  Node.js 24 + TypeScript 5.8 バックエンド開発ガイド。Express 5 API、Drizzle/Prisma ORM、
  Vitest 3 TDD、tsup/Vite 7・8 ビルドパイプラインの実装パターンと落とし穴を提供する。

  以下のシーンで必ず使うこと:
  (1) Node.js バックエンド、Express API、REST サーバーを新規作成・実装する
  (2) TypeScript の tsconfig、import type、NodeNext モジュール解決でエラーが出る
  (3) Drizzle または Prisma のスキーマ・マイグレーション・クエリを扱う
  (4) Vitest や supertest でバックエンドのテストを書く・デバッグする
  (5) tsup または Vite 7/8 でサーバーサイド TypeScript をビルドする
  (6) Express 5 のルーティング（404、wildcard、path-to-regexp）を修正する
  (7) Node.js 24 固有のエラー（erasableSyntaxOnly、import.meta.dirname、ESM）を解決する

  Trigger: "Node.js バックエンド", "Express API", "バックエンドエンジニア",
  "新しいAPIサーバー", "Prisma", "Drizzle", "マイグレーション",
  "Vitest", "supertest", "tsup", "vite build", "nodejs backend",
  "express server", "drizzle schema", "REST API", "バックエンド構築"
---

# Node.js 24 Backend Skill

Node.js 24 + TypeScript 5.8 バックエンド開発の完全ガイド。

## コマンド早見表

```bash
# 開発サーバー
tsx watch src/server.ts

# プロダクションビルド
tsup src/server.ts --format esm --target node24 \
  --external better-sqlite3 --external drizzle-orm

# テスト
vitest run
vitest --reporter=verbose

# Drizzle マイグレーション
drizzle-kit generate        # SQL マイグレーションファイル生成
drizzle-kit migrate         # ファイル DB に適用（:memory: 不可）

# Prisma マイグレーション
prisma migrate dev          # 開発用（shadow DB 使用）
prisma migrate deploy       # 本番用（非破壊的適用のみ）
prisma generate             # クライアント型生成
```

## 参照ファイル選択ガイド

| 状況 | 読むファイル |
|---|---|
| Node.js 24 の TypeScript エラー・tsconfig 設定 | `references/node24-ts.md` |
| Vite 7/8 ビルドエラー・tsup 設定 | `references/vite-config.md` |
| Express ルーティング・404・非同期エラー | `references/express5.md` |
| Prisma スキーマ・マイグレーション・N+1 | `references/prisma.md` |
| Drizzle スキーマ・マイグレーション・同期 API | `references/drizzle.md` |
| Vitest / TDD / supertest テスト設計 | `references/testing.md` |
| 新規プロジェクト作成（テンプレート） | `references/todo-app/` |

## プロジェクト初期設定チェックリスト

新規プロジェクトでは必ず確認:

- [ ] `package.json` に `"type": "module"` と `"engines": { "node": ">=24.0.0" }`
- [ ] `tsconfig.json` に `module: NodeNext`, `moduleResolution: NodeNext`, `erasableSyntaxOnly: true`, `verbatimModuleSyntax: true`
- [ ] import パスに `.ts` 拡張子を明記（`'./file'` → `'./file.ts'`）
- [ ] `__dirname` を `import.meta.dirname` に置換（ESM では未定義）
- [ ] Drizzle 使用時は `drizzle.config.ts` を作成
- [ ] Vitest で better-sqlite3 を使う場合は `pool: 'forks'` を設定

## 新規プロジェクトのクイックスタート

`references/todo-app/` を雛形として利用:

```bash
cp -r <skill-path>/references/todo-app/ ./my-api
cd my-api
npm install
npm run generate      # drizzle-kit generate
npm test              # 全テスト通過を確認
npm run dev           # 開発サーバー起動
```
