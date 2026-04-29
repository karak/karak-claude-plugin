# Express 5 ワイルドカードルーティングの問題と修正

## 根本原因

Express 5 では、パスマッチングエンジンが **path-to-regexp v8** に更新されました。この変更により、ワイルドカード `*` の書き方が変わっています。

Express 4 までは `*` を「0個以上の任意の文字列」として単独で使用できましたが、Express 5 では **名前付きワイルドカードパラメータ** として記述しなければなりません。

つまり、Express 5 では `*` を単独で使うとパターンが不正と見なされ、404 を返すか、場合によってはエラーになります。

---

## 修正方法

### 正しい構文（Express 5）

```ts
// Express 5: 名前付きワイルドカード {*splat} を使う
app.get('/api/v1/{*splat}', (req, res) => res.json({ ok: true }))
```

`splat` は任意の名前で構いません（`{*rest}`、`{*path}` なども有効です）。キャプチャされた値は `req.params.splat` として参照できます。

```ts
app.get('/api/v1/{*splat}', (req, res) => {
  console.log(req.params.splat) // 例: "users/123"
  res.json({ ok: true })
})
```

### Express 4（旧構文）との比較

| Express 4 | Express 5 |
|---|---|
| `/api/v1/*` | `/api/v1/{*splat}` |
| `/files/*/download` | `/files/{*name}/download` |
| `/:id(\\d+)*` | `/:id(\\d+){*rest}` |

---

## その他の関連するパスパターンの変更点

### 1. オプショナルパラメータの書き方

```ts
// Express 4
app.get('/user/:id?', handler)

// Express 5
app.get('/user/{:id}', handler)  // {} で囲むことでオプショナルを表現
```

### 2. 正規表現による制約

```ts
// Express 4（インライン正規表現）
app.get('/user/:id(\\d+)', handler)

// Express 5（同様に動作するが、より複雑なパターンは変更が必要な場合あり）
app.get('/user/:id(\\d+)', handler)  // 単純なケースはそのまま動作する
```

### 3. 文字クラスの使用

path-to-regexp v8 では、より厳密なパターン検証が行われるため、不正な正規表現構文はエラーになります。

```ts
// 注意: Express 5 では不正なパターンはエラーをスローする
// Express 4 では無視されていたものが Express 5 では問題になる場合がある
```

### 4. `app.use()` のパスマッチングの変更

`app.use()` は Express 4 ではプレフィックスマッチでしたが、Express 5 でもその動作は維持されています。ただし、ワイルドカードを明示したい場合は同様に名前付きワイルドカードを使います。

```ts
// Express 5 での app.use のワイルドカード
app.use('/api/{*splat}', router)
```

---

## まとめ

**問題のコード:**
```ts
app.get('/api/v1/*', (req, res) => res.json({ ok: true }))
//                ^ Express 5 では無効
```

**修正後のコード:**
```ts
app.get('/api/v1/{*splat}', (req, res) => res.json({ ok: true }))
//                ^^^^^^^^ 名前付きワイルドカード（波括弧 + アスタリスク + 名前）
```

Express 5 へのアップグレード時は、既存の `*` ワイルドカードを全て `{*paramName}` 形式に書き換える必要があります。
