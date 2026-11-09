---
name: disk-saver
description: Diagnoses Windows disk usage beyond simple cache cleanup - checks whether each large item is actually used (running apps, VS Code extension lists, nvm/Playwright references, superseded drivers, pagefile peak use, stale workspaces) and produces a prioritized Japanese proposal; nothing is removed without per-item approval. Use when the user wants to free disk space on Windows, says C: drive is full, or asks what is safe to delete.
---

# disk-saver（Windows ディスク容量の診断と提案）

## 原則

- 解析スクリプト（scan / probes / classify）は読み取り専用。削除・移動のコードは持たない（`tests/test_safety.py` で検査）。
- 削除するのはカタログ（`catalog/windows.json`）に載っていて、利用者がこの会話で**項目名を挙げて承認したもの**だけ。承認は次回に持ち越さない。
- プロセスを終了させない。アプリ起動中で保留になった項目は「終了してから再スキャン」と伝える。
- 管理者権限が必要な操作は自分で昇格せず、コマンドを提示して利用者に実行してもらう。

## 手順

1. **スキャン**（約 30〜60 秒）。出力先はスクラッチパッドなどの一時フォルダー:
   ```
   python <skill>/scripts/scan.py --out <tmp>/scan.json
   python <skill>/scripts/probes.py --out <tmp>/probes.json
   python <skill>/scripts/classify.py <tmp>/scan.json --probes <tmp>/probes.json --report <tmp>/report.md --plan <tmp>/plan.json
   ```
2. **報告**: `report.md` の要点を日本語で示す。順番は「1. 提案」（優先度順）→「2. 判断が必要」→「3. 助言のみ」。
   空き容量、回収見込み、保留の合計と、その理由を必ず書く。この段階では何も選ばない。
3. **承認**: AskUserQuestion を使う。
   - FREE / CHEAP はまとめて 1 問にし、項目名をすべて並べる。
   - COSTLY / PROJECT は 1 件ずつ聞く。再取得の手間を必ず添える。
   - 方法が「ごみ箱を経由せず完全削除」の項目は、質問文にもそう書く。
   - 「判断が必要」の項目は、選択肢を示して利用者に決めてもらう。
   - 「助言のみ」の項目は承認を求めない。手順を示すだけにする。
4. **実行**: 承認が済んだら、`apply/execute.py` だけを使って実行する。自分で削除コマンドを組み立てない。
   ```
   python <skill>/apply/execute.py --plan <tmp>/plan.json --hash <承認時に示した plan_hash> --ids <承認された id をカンマ区切り> --out <tmp>/result.json
   ```
   - 実行の直前にスキャンし直す。計画が 1 時間より古い場合は、実行スクリプトが実行を拒否する。
   - 承認を求めるときは、計画の `plan_hash` も示す。手順 1 をやり直したら、承認も取り直す。
   - 保留の行、助言の行、判断待ちの行、管理者向けの行、見送った行は、実行スクリプトが拒否する。管理者向けの項目は手順を示すだけにする。
   - 結果は 1 件ずつ報告する（done / partial / failed / refused と、そのエラー文）。
5. **検証**: 空き容量を測り直し、見込みとの差と、その理由（ごみ箱に残っている、保留中など）を報告する。

## ファイル

- `catalog/windows.json`: 対象の一覧。分類は FREE / CHEAP / COSTLY / PROJECT / DECISION / ADVICE / PRESERVE。各項目に理由、再取得の手間、方法を持つ
- `scripts/scan.py`: カタログに載った場所の容量を測る。クラウドのみのファイルは 0 として数え、ジャンクションはたどらない
- `scripts/probes.py`: 使用状況を調べる（nvm、Playwright、VS Code の拡張と作業データ、pnputil、ページファイル、ごみ箱）
- `scripts/classify.py`: 保護対象の判定、優先度（GB × 確度 ÷ 再取得の手間）の計算、日本語レポートの出力
- `apply/execute.py`: 承認された行だけを実行する唯一のスクリプト。保護対象と起動中のアプリを実行直前に確認し直し、コマンドは許可リストで検査する
- `scripts/policy.py`: 実行してよいコマンドの許可リストと、削除処理が紛れ込んでいないかの検査

## テスト

`python -m pytest`（スキルのフォルダーで実行）
