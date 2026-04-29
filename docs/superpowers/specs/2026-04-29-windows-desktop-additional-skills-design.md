# karak-windows-desktop 追加スキル設計

**作成日:** 2026-04-29  
**ブランチ:** feat/windows-desktop-plugin  
**対象プラグイン:** karak-windows-desktop

---

## 背景・目的

既存スキル（`dotnet-wpf-expert`, `dotnet-testing`）は実装フェーズと品質保証をカバーしている。  
本設計では「詳細設計 → 出荷 → 保守」フェーズおよび .NET 固有のアーキテクチャパターンをカバーする5本のスキルを追加する。

---

## 対象範囲

- アプリ規模: 小〜大規模の両方（スキル内で分岐を設ける）
- 配布方式: MSIX / Windows Installer（エンタープライズ配布優先）
- アーキテクチャ: Clean Architecture / Vertical Slice
- 保守優先度: ログ・診断が最優先、DB移行・パフォーマンスは業界標準レベル

---

## スキル一覧

### 1. `dotnet-clean-architecture`（詳細設計フェーズ）

**目的:** .NET 10 WPF アプリに Clean Architecture または Vertical Slice Architecture を適用する際のガイド。

**カバー内容:**

- Clean Architecture の4レイヤー構成（Domain / Application / Infrastructure / Presentation）
- Vertical Slice Architecture（機能単位でフォルダを切る構成）
- 依存逆転の原則（DIP）とインターフェース設計
- WPF における Presentation 層の位置づけ（ViewModels は Application 層 or Presentation 層）
- `IMediator`（MediatR）によるコマンド・クエリ分離（CQRS lite）
- レイヤー境界でのモデル変換（DTO ↔ Domain Entity）
- よくある落とし穴（Over-engineering、ViewModel が Domain を直参照する問題）

**深さ:** 深（パターン選択の判断基準・コード例・アンチパターン表を含む）

**想定トリガー:** 「新規プロジェクトのフォルダ構成・レイヤー設計をどうするか」「レイヤー境界を引き直したい（リファクタリング文脈）」「どのレイヤーにクラスを置くべきか判断できない」

**隣接スキルとの区別:**
- `dotnet-wpf-expert` → コンポーネント実装レベルの配線（バインディング・コマンド）を扱う
- 本スキル → **レイヤー境界の設計判断**（どこに何を置くか、依存方向の設計）を扱う

---

### 2. `dotnet-packaging-msix`（出荷フェーズ）

**目的:** .NET 10 WPF アプリを MSIX パッケージとしてビルド・署名・配布するための完全ガイド。Windows Installer（WiX/MSI）は本スキルの非スコープとし、MSIX のみを扱う。

**カバー内容:**

- MSIX プロジェクト構成（Windows Application Packaging Project）
- Package.appxmanifest の必須設定（Identity, Capabilities, VisualElements）
- コード署名（自己署名証明書 vs EV 証明書、`signtool.exe`）
- エンタープライズ配布（GPO によるサイレントインストール、SCCM/Intune 連携の考え方）
- 自動更新（`PackageManager.AddPackageAsync` / AppInstaller ファイル）
- GitHub Actions による CI/CD パイプライン（`dotnet publish` → MSIX ビルド → 署名 → リリース）
- バージョン管理（`Package.appxmanifest` の Version と AssemblyVersion の同期）
- よくある落とし穴（証明書信頼エラー、capabilities 不足、バージョン番号フォーマット）

**深さ:** 深（手順・設定例・CI/CD YAML スニペットを含む）

**想定トリガー:** 「パッケージングしたい」「配布方法を決めたい」「署名エラーが出た」

---

### 3. `dotnet-logging-diagnostics`（保守フェーズ・最優先）

**目的:** .NET 10 WPF アプリのログ収集・診断・トラブルシュートの完全ガイド。Serilog を中心に ETW・Windows Event Log も扱う。

**カバー内容:**

- Serilog のセットアップ（Generic Host 統合、`appsettings.json` 設定）
- Sink 選択（File / Console / EventLog / Seq / Application Insights）
- Enricher（ThreadId, MachineName, Application version）
- 構造化ログの書き方（message template のベストプラクティス）
- ログレベル戦略（Verbose/Debug/Info/Warning/Error/Fatal の使い分け）
- ETW（Event Tracing for Windows）の基礎と `dotnet-trace` によるカスタム EventSource ログ収集（CPU/メモリプロファイリング用途の `dotnet-trace` は `dotnet-performance` スキルに委譲）
- Windows Event Log への書き込み（`EventLog` sink + ソース登録）
- グローバル例外ハンドリング（`Application.DispatcherUnhandledException`, `TaskScheduler.UnobservedTaskException`）
- ログファイルのローテーション・保持ポリシー
- よくある落とし穴（ログが出ない、PII をログに含めてしまう、非同期 Sink のフラッシュ漏れ）

**深さ:** 最深（設定例・コード例・トラブルシュートフロー付き）

**想定トリガー:** 「ログを設定したい」「本番でクラッシュした原因を調べたい」「ETW/イベントログを使いたい」

---

### 4. `dotnet-db-migration`（保守フェーズ・標準）

**目的:** .NET WPF アプリの SQLite/SQL Server DB スキーマ管理とデータ移行の業界標準プラクティス。

**カバー内容:**

- EF Core Migrations の基本ワークフロー（`add-migration` / `update-database` / `script-migration`）
- FluentMigrator の基本（EF Core 非使用時の代替）
- アプリ起動時のマイグレーション自動適用（`dbContext.Database.MigrateAsync()`）
- ロールバック戦略（`Down()` メソッドの書き方）
- スキーマバージョン管理テーブル（`__EFMigrationsHistory`）
- データ移行のシードとべき等性
- よくある落とし穴（マイグレーション競合、本番 DB への誤適用防止）
- デスクトップ特有: 起動前の SQLite ファイルバックアップ（`MigrateAsync` 前に `.db` をコピー）
- バージョンギャップ検出（v1 → v3 へのスキップアップグレード）と失敗時のユーザー通知パターン

**深さ:** 薄〜中（標準的なワークフローと主要コマンド、よくある落とし穴に絞る）

**想定トリガー:** 「DB スキーマを変更したい」「マイグレーションが失敗した」「起動時に自動マイグレーションしたい」

---

### 5. `dotnet-performance`（保守フェーズ・標準）

**目的:** .NET 10 WPF アプリのパフォーマンス計測・診断の業界標準プラクティス。

**カバー内容:**

- `dotnet-trace` / `dotnet-counters` による CPU・メモリ収集（カスタム EventSource ログ収集は `dotnet-logging-diagnostics` スキルに委譲）
- PerfView の基本操作（フレームグラフ・GC ビュー）
- Visual Studio Diagnostic Tools（メモリスナップショット・CPU サンプリング）
- WPF UI パフォーマンスの落とし穴（不必要な DataTemplate 再生成、Visual Tree の肥大化、頻繁な `INotifyPropertyChanged` 発火）
- `Stopwatch` / `BenchmarkDotNet` による計測
- GC プレッシャー対策（Large Object Heap、ArrayPool の使いどころ）
- よくある落とし穴（UI スレッドのブロック、仮想化されていない大量アイテムリスト）

**深さ:** 薄〜中（ツールの使い方と WPF 固有の罠に絞る）

**想定トリガー:** 「アプリが重い」「メモリが増え続ける」「UI がもたつく」

---

## 全体スキルマップ（追加後）

```
開発フェーズ  スキル
─────────────────────────────────────────────────────
詳細設計     dotnet-clean-architecture  ← NEW
実装         dotnet-wpf-expert          既存
品質保証     dotnet-testing             既存
出荷         dotnet-packaging-msix      ← NEW
保守(主)     dotnet-logging-diagnostics ← NEW
保守(DB)     dotnet-db-migration        ← NEW
保守(性能)   dotnet-performance         ← NEW
```

---

## 実装方針

- 各スキルは `karak-windows-desktop/skills/<name>/SKILL.md` に配置
- `plugin.json` の `skills` 配列に `"./skills/<name>"` 形式で追加
- `marketplace.json` の version を `2.2.0` にインクリメント
- スキル構築には `skill-creator` スキルを使用

---

## 非スコープ

- WinUI 3 / MAUI への移行ガイド（別スキルとして将来検討）
- Azure DevOps パイプライン（GitHub Actions のみカバー）
- MEF プラグインシステム（今回のスコープ外）
- Windows Installer（WiX / MSI / NSIS）— `dotnet-packaging-msix` は MSIX 専用。WiX は将来スキルとして検討
- `dotnet-trace` のカスタム EventSource 以外のログ収集機能 → `dotnet-logging-diagnostics` に集約
- CPU/メモリプロファイリング目的の `dotnet-trace` → `dotnet-performance` に集約
