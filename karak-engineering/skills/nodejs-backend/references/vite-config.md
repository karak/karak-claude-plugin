# Vite 7 / 8 — Node.js バックエンド向けビルド設定

## 結論: 純粋な Node.js バックエンドには tsup を推奨

Vite は本質的にフロントエンド向けビルドツール。Express + native addon（better-sqlite3 等）を含む
純粋バックエンドには **tsup（esbuild ベース）** を使うのが 2026 年の標準:

```bash
# tsup によるバックエンドビルド
tsup src/server.ts --format esm --target node24 \
  --external better-sqlite3 --external drizzle-orm

# tsup.config.ts を使う場合
```
```ts
import { defineConfig } from 'tsup'

export default defineConfig({
  entry: ['src/server.ts'],
  format: ['esm'],
  target: 'node24',
  external: ['better-sqlite3', 'drizzle-orm'],
  clean: true,
})
```

**Vite を使う場面:** フルスタック（Next.js-like な SSR）や、フロントエンドと同一 monorepo でビルドパイプラインを共有したい場合。

---

## Vite バージョン別 Breaking Changes

### Vite 6 → 7 (主な変更)

| 変更点 | 詳細 |
|---|---|
| Node.js 最低バージョン | Node.js 20.19+ または 22.12+ が必要 |
| `resolve.conditions` デフォルト変更 | SSR と クライアント用で conditions が分離 |
| `build.cssCodeSplit` デフォルト変更 | `true` がデフォルトに（以前は状況依存） |
| `server.fs.deny` 強化 | `.env` ファイルのデフォルト除外が追加 |
| `optimizeDeps` の挙動改善 | CJS → ESM 変換のキャッシュが改善 |

### Vite 7 → 8 (主な変更) ※ 2026 年初旬リリース

| 変更点 | 詳細 |
|---|---|
| **Rolldown 採用** | esbuild + Rollup を Rust 製 Rolldown に置換。ビルド速度が大幅向上 |
| `build.rollupOptions` 互換 | Rolldown は Rollup の API と互換性があるが、完全ではない |
| `emitDecoratorMetadata` 組み込み | 追加プラグイン不要 |
| `resolve.tsconfigPaths` 組み込み | `vite-tsconfig-paths` プラグイン不要に |
| `build.lib` 変更 | ライブラリモードの API が整理 |

---

## Vite lib mode を Node.js バックエンドに使う場合の設定

**警告:** Vite 8 の Rolldown は native addon（.node バイナリ）の外部化が不安定。
`better-sqlite3` 等を含む場合は tsup を使うこと。

Vite lib mode を使う場合（native addon なしの場合のみ）:

```ts
// vite.config.ts
import { defineConfig } from 'vite'
import { builtinModules } from 'node:module'

export default defineConfig({
  build: {
    lib: {
      entry: 'src/server.ts',
      formats: ['es'],
      fileName: 'server',
    },
    rollupOptions: {
      // Node.js 組み込みモジュールをすべて外部化
      external: [
        ...builtinModules,
        ...builtinModules.map(m => `node:${m}`),
        // npm パッケージも外部化（バンドルしない）
        /^[^./]/,
      ],
    },
    sourcemap: true,
    target: 'node24',
  },
  ssr: {
    target: 'node',
  },
})
```

**注意点:**
- `builtinModules` のエントリは `'fs'` 形式と `'node:fs'` 形式の両方を列挙
- `node_modules` を外部化するには `/^[^./]/` か全パッケージの明示列挙が必要
- native addon をバンドルすると `.node` ファイルが正しくロードされない

---

## vite-node (開発ランナー)

`tsx watch` の Vite エコシステム版。Vitest が内部で使用:

```bash
# インストール
npm install -D vite-node

# 実行
vite-node src/server.ts

# ウォッチモード
vite-node --watch src/server.ts
```

`tsx watch` と比べて:
- メリット: Vite のプラグインシステムが使える
- デメリット: `tsx watch` より起動が遅い場合がある、less battle-tested for pure server restarts

---

## ツール比較

| ツール | 用途 | DTS 出力 | 速度 | Node バックエンド適性 |
|---|---|---|---|---|
| **tsup** | バックエンド/ライブラリ | ✅ | 速い (esbuild) | ◎ ベスト選択 |
| **esbuild** | CLI/バンドル | ❌ (プラグイン要) | 最速 | ◎ シンプル |
| **tsx** | 開発ランナーのみ | ❌ | N/A | ◎ 開発時 |
| **Vite lib mode** | フルスタック/ライブラリ | プラグイン要 | 速い (Rolldown) | △ native addon 注意 |
| **tsdown** | ライブラリ (次世代 tsup) | ✅ | 最速 (Rolldown) | ○ 2026 注目 |
| **tsc** | 型チェック+トランスパイル | ✅ | 遅い | △ バンドルなし |

## 参考リンク

- [Vite 8.0 アナウンス](https://vite.dev/blog/announcing-vite8)
- [Vite SSR ガイド](https://vite.dev/guide/ssr)
- [tsup ドキュメント](https://tsup.egoist.dev/)
- [esbuild ドキュメント](https://esbuild.github.io/)
