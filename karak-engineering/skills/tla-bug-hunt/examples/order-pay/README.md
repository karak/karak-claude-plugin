# 例: 注文の支払い API（REPORT.md の手本）

`app/` は検証対象の小さな 2-tier アプリ、`tla/` はモデルである。この README は、スキルが求める `REPORT.md` の構成で書いてある。結果はすべて TLC v1.7.4（Java 11）で実行して得た。

## 1. 対象と結論

`POST /orders/:id/pay`（`app/server/payments.js`）と、クライアントのリトライ（`app/client/PayButton.jsx`）を調べた。

- **バグ 1（確認済み）:** クライアントがタイムアウト後に再送すると、カードが 2 回課金される。
- **バグ 2（確認済み）:** バグ 1 を条件付き UPDATE で直しても、課金直後にサーバーが落ちると注文が `charging` のまま止まる。以後どのリクエストも、その注文を支払い済みにできない。

## 2. コード ↔ モデル対応表

| 変数 | 分類 | 値域 | コード |
|---|---|---|---|
| `status` | DB | `"pending"`, `"paid"`（修正版は `"charging"` を追加） | `app/schema.sql` `orders.status` |
| `gatewayCharges` | DB 側の外部副作用 | `0..MaxAttempts` | `payments.js:15` `gateway.charge` |
| `chargeRows` | DB | `0..MaxAttempts` | `payments.js:16` `INSERT INTO charges` |
| `sent`, `responded` | ネットワーク | `SUBSET Attempts` | `PayButton.jsx:5-6` `fetch` |
| `clientDone`, `i` | クライアント | `BOOLEAN`, `1..MaxAttempts` | `PayButton.jsx:3-12` |
| `seen` | ハンドラ局所 | `status` の値域 | `payments.js:10` SELECT の結果 |

| アクション（ラベル） | 1 ステップの範囲 | コード |
|---|---|---|
| `Send` | 1 回の `fetch` を送る | `PayButton.jsx:6` |
| `Wait` | レスポンス受信か、5 秒のタイムアウトで次の試行へ | `PayButton.jsx:6-10` |
| `Read` | `SELECT status`（オートコミット 1 本） | `payments.js:10` |
| `Check` | `paid` なら 409 | `payments.js:13` |
| `Charge` | `gateway.charge`（外部 API 1 回） | `payments.js:15` |
| `InsertCharge` | `INSERT INTO charges`（1 本） | `payments.js:16` |
| `MarkPaid` | `UPDATE ... status='paid'`（1 本） | `payments.js:17` |
| `Respond` | レスポンスを返す | `payments.js:18` |

仮定: 注文は 1 件で、クライアントは 1 つ。ダブルクリック（`PayButton.jsx` はボタンを無効化しない）は今回の範囲外である。

## 3. 不変量

| 不変量 | 損害 | 壊れる版で落ちたか |
|---|---|---|
| `NoDoubleCharge == gatewayCharges <= 1` | 1 回の注文でカードが複数回課金される | 落ちた。元のコードのモデルで違反した |
| `PaidHasChargeRow == status = "paid" => chargeRows >= 1` | 支払済みなのに課金記録がない | 落ちた。修正版で `MarkPaid` を `InsertCharge` の前に移した変異版で違反した |
| `NoStuckCharging`（全プロセス終了 ⇒ `status # "charging"`） | 注文が永久に支払い不能になる | 落ちた。`OrderPayCrash` で違反した（バグ 2） |

## 4. 結果

```bash
export TLA2TOOLS=/path/to/tla2tools.jar
bash ../../scripts/tlc.sh tla/OrderPay.tla        # バグ版
bash ../../scripts/tlc.sh tla/OrderPayFixed.tla   # 修正版
bash ../../scripts/tlc.sh tla/OrderPayCrash.tla   # 修正版 + クラッシュ
```

| モデル | 定数 | TLC の最終結果 | 状態数（distinct） |
|---|---|---|---|
| `OrderPay` | `MaxAttempts = 2` | `Error: Invariant NoDoubleCharge is violated.` | 約 180（並列実行のため前後する） |
| `OrderPayFixed` | `MaxAttempts = 2` | `Model checking completed. No error has been found.` | 139 |
| `OrderPayFixed` | `MaxAttempts = 3` | `Model checking completed. No error has been found.` | 755 |
| `OrderPayCrash` | `MaxAttempts = 2, MaxCrashes = 1` | `Error: Invariant NoStuckCharging is violated.` | 191 |

各 `.cfg` には不変量を並べてある。違反した不変量を外し、残りを 1 つずつ別の `.cfg` で実行して確かめた。`OrderPay` で違反するのは `NoDoubleCharge` だけである。`OrderPayCrash` で違反するのは `NoStuckCharging` だけである。

デッドロック検査は有効のまま実行した（`-deadlock` は付けていない）。送られなかった試行のハンドラは、`Arrive` でクライアントの終了を見て抜ける。

## 5. 反例

**バグ 1（`OrderPay`）**

1. クライアントが試行 1 を送る。
2. ハンドラ 1 が `SELECT status` を実行し、`pending` を読む（`payments.js:10`）。
3. 5 秒が経ち、クライアントは試行 1 を諦めて試行 2 を送る。ハンドラ 1 は走り続けている。
4. ハンドラ 2 も `SELECT status` で `pending` を読む。まだ誰も `paid` を書いていない。
5. ハンドラ 1 が `gateway.charge` を呼ぶ（課金 1 回目）。
6. ハンドラ 2 も `paid` チェック（`payments.js:13`）を通過して `gateway.charge` を呼ぶ（課金 2 回目）。

**バグ 2（`OrderPayCrash`）**

1. ハンドラ 1 が条件付き UPDATE で `pending` を `charging` にする。
2. クライアントが諦めて試行 2 を送り、そのまま終わる。
3. ハンドラ 1 が `gateway.charge` を呼んだ直後にプロセスが落ちる。カードは課金済みで、`status` は `charging` のまま残る。
4. ハンドラ 2 は条件付き UPDATE で 0 行を得て、409 を返す。
5. 全リクエストが終わっても `charging` のままである。以後どのリクエストも、この注文を支払い済みにできない。

## 6. コード修正指示

**指示 1（バグ 1 を塞ぐ。`OrderPayFixed` で検証済み）**

`payments.js:10-13` の SELECT と `paid` チェックを、条件付き UPDATE 1 本に置き換える。

```sql
UPDATE orders SET status = 'charging'
WHERE id = $1 AND status = 'pending'
RETURNING amount
```

0 行なら課金せず、409（または「処理中」を示す 202）を返す。この変更で、反例のステップ 4 と 6 が起こらなくなる。判定と更新が 1 ステップになるので、2 つめのハンドラは `pending` を読めない。`app/schema.sql` の `status` の値域に `charging` を加える。

「0 行」には、注文が存在しない場合も含まれる。404 と 409 を区別するには、0 行のときに注文の有無を別に読む。

`OrderPayFixed` で検証したのは、バグ 1 の二重課金が消えることだけである。`gateway.charge` が例外を投げた場合（カードの拒否やタイムアウト）は、モデルに入れていない。その場合、`charging` のまま残る（バグ 2 と同じ状態）。`catch` で `pending` に戻す処理を加え、それもモデルに入れるまでは、この経路は未検証である。

**指示 2（バグ 2 への対策。未検証）**

`gateway.charge` に、注文 ID から作った冪等性キーを渡す。そのうえで、一定時間 `charging` のまま止まっている注文を、ゲートウェイに照会して `paid` か `pending` に戻す回収処理を加える。

これはまだモデル化していない。次の段では、回収処理と「ゲートウェイがキーを守る」という仮定をモデルに入れ、`NoStuckCharging` と `NoDoubleCharge` を同時に確かめる。それまでは、指示 2 は検証前の提案である。

## 7. 範囲

検証したのは、注文 1 件、試行 2 回（修正版は 3 回も）、クラッシュ 1 回の範囲である。

モデル化していないもの:

- 複数の注文
- ダブルクリックと複数タブ
- ゲートウェイの失敗や拒否
- `charges` の一意制約
- レスポンスの喪失（タイムアウトとしてだけ表している）
- 活性（「いつかは支払われる」）
- レスポンスの種類。`PayButton.jsx:7` は 409 でも成功として扱うが、モデルの `responded` は 200 と 409 を区別しない。そのため、クライアントと DB の食い違い（画面は完了、DB は `charging`）は確かめていない。次の段では、レスポンスコードを変数に入れて `clientDone => status = "paid"` を確かめる
- クラッシュの地点。`OrderPayCrash` は `Charge` の直後にだけ落ち、止まるのは 1 本のハンドラだけである。`Claim` の直後に落ちる場合や、プロセスごと全ハンドラが止まる場合は入れていない

## 8. 同期点

この例は `app/` の現行の内容に対応している。実際のプロジェクトでは、ここにモデルが対応するコミットの SHA を書く。

## 9. 再実行

```bash
bash ../../scripts/tlc.sh tla/OrderPay.tla
```
