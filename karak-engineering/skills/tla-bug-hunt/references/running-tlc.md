# TLC の実行と結果の読み方

## 導入

- Java 11 以上が必要である。
- `tla2tools.jar` を https://github.com/tlaplus/tlaplus/releases から取得する。v1.7.4 で動作を確認した。
- ダウンロードする前に、ファイル名、取得元、サイズをユーザーに示して承認を得る。
- jar はアプリのリポジトリに入れない。置いた場所を `TLA2TOOLS` で渡す。
- VS Code 拡張（tlaplus.vscode-ide）や TLA+ Toolbox でも同じ jar が動く。再実行の手順には CLI のコマンドを残す。

## コマンド

`bash scripts/tlc.sh Spec.tla [Spec.cfg] [TLC の追加引数]` は、次の処理を順に実行する。個別に実行するときは `J=$TLA2TOOLS` として、同じコマンドを使う。

| 段階 | コマンド | 成功の印 |
|---|---|---|
| PlusCal の変換 | `java -cp $J pcal.trans -nocfg Spec.tla` | `Translation completed.` |
| 構文・意味の検査 | `java -cp $J tla2sany.SANY Spec.tla` | `Semantic errors` が出ない |
| モデル検査 | `java -cp $J tlc2.TLC -workers auto -config Spec.cfg Spec.tla` | `Model checking completed. No error has been found.` |

- `pcal.trans` は `.tla` の `\* BEGIN TRANSLATION` から `\* END TRANSLATION` までを書き換える。この範囲は手で編集しない。
- `pcal.trans` は、変換前のファイルを `.old` として残す。ラッパーはこれを消す。
- `-nocfg` を付けないと、`pcal.trans` が手書きの `.cfg` を上書きする。
- TLC は作業ディレクトリに `states/` を作る。ラッパーは `-metadir` で一時ディレクトリに逃がす。

## .cfg の雛形

```text
SPECIFICATION Spec
CONSTANTS MaxAttempts = 2
          MaxCrashes = 1
INVARIANTS TypeOK NoDoubleCharge PaidHasChargeRow
```

- 定数は最小から始める。ハンドラ数、試行数、クラッシュ数を 1 ずつ増やすと、状態数はおおむね数倍ずつ増える。
- 1 分以内に終わる範囲を、再実行の既定値にする。
- バグを探すときは、不変量ごとに `.cfg` を分ける（例: `Spec_NoDouble.cfg`）。並列ワーカーで回すと、複数の不変量のうちどれが先に報告されるか、また違反時の状態数が実行ごとに変わる。決定的な結果が欲しいときは `-workers 1` を付ける。

## デッドロック

TLC は、次の状態がない状態に達するとデッドロックと報告する。原因は次の 3 種類である。

| 原因 | 見分け方 | 対処 |
|---|---|---|
| 正常終了（全プロセスが `Done`） | 最終状態の `pc` がすべて `"Done"` | PlusCal なら、変換結果に `Terminating` が入るので出ない。手書きの TLA+ なら、`Terminating == AllDone /\ UNCHANGED vars` を `Next` に加える |
| 来ない入力を待つプロセス | 最終状態の一部の `pc` が `await` のラベルで止まっている | その待ちを、終了条件でも抜けられるようにする（[modeling-2tier.md](modeling-2tier.md#来なかったリクエストの待ち)） |
| 本物のデッドロック | 待ちの条件が、モデルの外の事情なしには満たされない | **これは発見である。** 反例としてコードの言葉で報告する |

`-deadlock` フラグは、デッドロック検査を丸ごと無効にする。付けると、上の表の 3 行目（本物のデッドロック）も見えなくなる。このスキルでは使わない。偽デッドロックは、表の 1 行目か 2 行目の方法で消す。

## PlusCal の落とし穴

- `define` ブロックでは `ProcSet` を参照できない。`ProcSet` は `define` より後に定義されるからである。`pc` は変数宣言に含まれるので参照できる。`ProcSet` を読む不変量（「全プロセスが終わったら」など）は、`\* END TRANSLATION` の下、モジュール末尾の `====` の上に書く（[例](../examples/order-pay/tla/OrderPayCrash.tla)）。`define` の中に置きたい場合は、`ProcSet` の代わりにプロセス ID の集合を明示する（例: `{0} \union Attempts`）。
- ラベル 1 つが 1 つの原子的ステップになる。同じラベル内で同じ変数に 2 回代入すると、変換時にエラーになる。
- `either ... or ...` の各分岐の先頭に `await` を置くと、その分岐は条件が満たされたときにだけ選べる。
- `goto` の後には、次のラベルが必要である。そのため、`if c then goto L; end if; x := 1;` を 1 つのラベルの中に書くと `Missing label` になる。判定と実行を同じ原子的ステップにしたいときは、`if c then goto L; else x := 1; end if;` のように `else` の中に書く。
- `\* BEGIN TRANSLATION` と `\* END TRANSLATION` の目印は、なければ `pcal.trans` が自動で加える。新しく書く仕様では、`(* --algorithm ... end algorithm; *)` の後に何も書かずに変換してよい。

## 反例トレースの読み方

1. 1 行目の `Error: Invariant X is violated.` で、どの不変量が破れたかを確かめる。
2. 各 `State n: <Label line ...>` を見る。そのステップでどのラベル（アクション）が動いたかが分かる。
3. 変数の差分を追う。`pc` の変化で、どのプロセスが進んだかが分かる。
4. 各ステップをコードの `file:line` に写し、番号付きの日本語のステップ列に書き直す。

TLC は幅優先探索で、最短の反例を 1 つだけ返す。次のバグを探すときは、見つけたバグを塞いだモデルで再実行する。

反例は `-metadir` のディレクトリにも `*_TTrace_*.tla` として書き出される。ラッパーは終了時にこのディレクトリを消すので、トレースは標準出力から読むか、残したいときは TLC を直接実行する。

## 状態数が多すぎるとき

- 定数を減らす。
- 対称性を使う。ID の集合を整数ではなくモデル値にする（`.cfg` に `CONSTANT Clients = {c1, c2}`）。そのうえで、仕様に `Perms == Permutations(Clients)`（`TLC` モジュールを `EXTENDS` する）を定義し、`.cfg` に `SYMMETRY Perms` を書く。対称性を使うと、活性（liveness）の検査は正しくなくなる。安全性の不変量だけを確かめるときに使う。
- 不要な局所変数を、使い終わったら初期値に戻す。
- 探索の上限を付ける。`.cfg` の `CONSTRAINT` に「試行回数 <= N」のような状態制約を書く。それでも大きすぎる場合は、`-simulate -depth 50` でランダムな実行を試す。ランダムな実行で違反が出なくても、全探索ではないので「検証した」とは書かない。
- 不変量やモデルの意味を削って状態数を減らすことはしない。

## 活性（いつかは起こること）

このスキルは安全性（悪い状態に到達しない）を主に扱う。「いつかは支払われる」のような活性を確かめるときは、`.cfg` に `PROPERTY Termination` などの時相式を書く。PlusCal の変換結果には `Termination` が入っている。

活性を確かめるには公平性も必要になる。PlusCal なら `fair process`、TLA+ なら `WF_vars(Action)` を付ける。公平性がないと、TLC は「誰も何もしない」実行を反例として返す。
