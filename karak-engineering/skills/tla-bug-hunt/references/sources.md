# 参考資料

## 主要リファレンス（優先順）

| 優先 | 資料 | 用途 |
|---|---|---|
| 1 | Leslie Lamport, *Specifying Systems: The TLA+ Language and Tools for Hardware and Software Engineers* (2002) — https://lamport.azurewebsites.net/tla/book-21-07-04.pdf | TLA+ の言語仕様とツールの原典。`Init` / `Next`、不変量、TLC の設定 |
| 2 | Chris Newcombe et al., "How Amazon Web Services Uses Formal Methods" (CACM, 2015) — https://cacm.acm.org/research/how-amazon-web-services-uses-formal-methods/ | 小さなモデルで設計上のバグを見つける実務での根拠 |
| 3 | Leslie Lamport, John Matthews, Mark Tuttle, Yuan Yu, "Specifying and Verifying Systems with TLA+" (2002) — https://lamport.azurewebsites.net/pubs/spec-and-verifying.pdf | 仕様を書いてからモデル検査するまでの手順 |
| 4 | Hillel Wayne, *Learn TLA+* — https://www.learntla.com/ | PlusCal、ラベルと原子性、実務的な書き方 |
| 5 | M. A. Kuppe, L. Lamport, D. Ricketts et al., "The TLA+ Toolbox" (2019) — https://lamport.org/pubs/toolbox.pdf | IDE で TLC を実行し、トレースを調べる方法 |

## 追加資料

- TLA+ Wiki — Learning TLA+ and Model Checking: https://www.docs.tlapl.us/learning:start
- Awesome TLA+: https://github.com/tlaplus/awesome-tlaplus
- Leslie Lamport — TLA+ Papers: https://lamport.azurewebsites.net/tla/papers.html
- ツール本体: https://github.com/tlaplus/tlaplus/releases

## 着想元

`create-formal-verification-skill`（pstack）。そこから次の考え方を受け継いだ。

- コードに忠実であること
- 一度は落ちること
- 発見を弱めないこと
- 範囲を正直に書くこと
- 安く再実行できること
- コードとの同期点を残すこと
