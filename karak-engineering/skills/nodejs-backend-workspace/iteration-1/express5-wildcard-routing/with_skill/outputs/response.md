# Express 5 ワイルドカードルーティング — 原因と修正方法

## 根本原因

Express 5 は内部で使用するパスパターンライブラリを **path-to-regexp 0.x → 8.x** に更新した。  
path-to-regexp 8.x では `*` をそのままワイルドカードとして使う記法（Express 4 の書き方）が**無効**となり、該当ルートが一切マッチしなくなる（結果として 404）。

Express 5 は起動時に無効なパターンを**例外としてスロー**する場合もある。

---

## 修正方法

### 正しい Express 5 の構文（2 通り）

```ts
// 推奨記法 — 名前付きワイルドカード
app.get('/api/v1/{*path}', (req, res) => res.json({ ok: true }))

// 代替記法 — キャプチャグループ
app.get('/api/v1/(.*)', (req, res) => res.json({ ok: true }))
```

`{*path}` の `path` は任意の識別子で、`req.params.path` でマッチした部分を取得できる。

---

## 関連する Express 5 のパスパターン変更点

Express 4 から 5 へ移行する際、ワイルドカード以外にも以下の書き方が動かなくなる。

### Optional パラメータ

```ts
// Express 4 (NG in Express 5)
app.get('/users/:id?', handler)

// Express 5
app.get('/users{/:id}', handler)
```

### 正規表現を含むパターン

```ts
// Express 4 (NG in Express 5)
app.get('/[discussion|page]/:slug', handler)

// Express 5 — ルート文字列に正規表現は使えない
// prefix 一致を app.use() で行い、内部で処理する設計に変更する
```

### 削除されたメソッド（ルーティング関連）

| Express 4 | Express 5 代替 |
|---|---|
| `app.del(path, handler)` | `app.delete(path, handler)` |
| `req.param(name)` | `req.params.name` / `req.query.name` / `req.body.name` を明示使用 |

---

## 注意点

- Express 5 は**無効なパスパターンをサーバー起動時に例外としてスロー**する。サードパーティミドルウェアが内部で `app.use(regex, ...)` を呼んでいる場合も同様に失敗する。
- `npm ls express` で Express のバージョンを確認し、5.x であることを把握した上で移行する。

---

## 参考

- [Express 4→5 移行ガイド](https://expressjs.com/en/guide/migrating-5.html)
- [path-to-regexp 8.x 変更点](https://github.com/pillarjs/path-to-regexp/releases)
