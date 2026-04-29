# .NET 10 WPF + SQLite + EF Core — 起動時マイグレーションのバックアップとエラーハンドリング

## 基本方針

デスクトップアプリにおける鉄則は **「`MigrateAsync()` を呼ぶ前に必ず SQLite ファイルをバックアップする」** です。  
サーバーと違い、ユーザーの PC でマイグレーションが失敗しても DBA がロールバックすることはできません。リカバリパスはアプリ側が完全に責任を持ちます。

---

## 1. 起動時マイグレーションの全体構成

```csharp
// App.xaml.cs または Generic Host の Startup
public static class DbStartup
{
    public static async Task MigrateAsync(IServiceProvider services, ILogger logger)
    {
        using var scope = services.CreateScope();
        var db = scope.ServiceProvider.GetRequiredService<AppDbContext>();

        // Step 1: バックアップ（マイグレーション前）
        await BackupIfSqliteAsync(db, logger);

        // Step 2: バージョンギャップ確認（任意）
        if (!await CheckVersionGapAsync(db, logger))
            return; // ユーザーがキャンセル → アプリ終了済み

        // Step 3: マイグレーション実行
        try
        {
            await db.Database.MigrateAsync();
        }
        catch (Exception ex)
        {
            logger.LogError(ex, "Migration failed");
            // Step 4: ユーザーへの通知
            MessageBox.Show(
                "データベースの更新に失敗しました。\nサポートにお問い合わせください。\n\n" + ex.Message,
                "起動エラー", MessageBoxButton.OK, MessageBoxImage.Error);
            throw; // アプリを終了させる
        }
    }
}
```

---

## 2. バックアップ実装（BackupIfSqliteAsync）

```csharp
private static async Task BackupIfSqliteAsync(AppDbContext db, ILogger logger)
{
    var connStr = db.Database.GetConnectionString() ?? "";
    // 接続文字列から DB ファイルパスを取得
    var match = Regex.Match(connStr, @"Data Source=([^;]+)", RegexOptions.IgnoreCase);
    if (!match.Success) return;

    var dbPath = match.Groups[1].Value.Trim();
    if (!File.Exists(dbPath)) return; // 初回起動時はファイルなし → スキップ

    var backupPath = dbPath + $".bak.{DateTime.Now:yyyyMMddHHmmss}";
    File.Copy(dbPath, backupPath, overwrite: true);
    logger.LogInformation("Database backed up to {BackupPath}", backupPath);

    // 古いバックアップを削除（直近 5 件だけ保持）
    var backups = Directory.GetFiles(Path.GetDirectoryName(dbPath)!, "*.bak.*")
                            .OrderByDescending(f => f)
                            .Skip(5);
    foreach (var old in backups)
        File.Delete(old);
}
```

### ポイント
- `File.Copy` は同期処理ですが、SQLite の小規模ファイルでは十分高速です。
- バックアップは `app.db.bak.20260429153000` のようなタイムスタンプ付きファイル名にします。
- 直近 5 件だけ保持することで、ディスクを圧迫しません。
- 初回起動時（ファイル未存在）は安全にスキップします。

---

## 3. バージョンギャップ検出（大量マイグレーション警告）

EF Core は `MigrateAsync` で複数の未適用マイグレーションを順番に自動適用します。ただし、長期間アップデートしていなかったユーザーには事前に通知すると親切です。

```csharp
public static async Task<bool> CheckVersionGapAsync(AppDbContext db, ILogger logger)
{
    var pending = (await db.Database.GetPendingMigrationsAsync()).ToList();

    if (pending.Count > 5)
    {
        logger.LogWarning("Large migration gap: {Count} pending", pending.Count);

        var result = MessageBox.Show(
            $"データベースを {pending.Count} バージョン更新する必要があります。\n" +
            "この処理には時間がかかる場合があります。続行しますか？",
            "データベース更新", MessageBoxButton.YesNo, MessageBoxImage.Question);

        if (result == MessageBoxResult.No)
        {
            Application.Current.Shutdown();
            return false;
        }
    }
    return true;
}
```

---

## 4. ロールバック戦略

SQLite では EF Core の `Down()` メソッドによるロールバックより、**バックアップの復元** が安全で確実です。

| シナリオ | 対応方法 |
|----------|----------|
| マイグレーション失敗（例外発生） | バックアップファイルを元のパスに上書きコピー |
| 新バージョンで問題が発覚 | ユーザーに `*.bak.*` の復元手順をサポートで案内 |
| 開発・テスト環境 | `Down()` を実装して `dotnet ef database update <前のMigration名>` で巻き戻し |

`Down()` は開発の便宜のために実装しておきますが、本番リカバリはバックアップ復元を正式手順とします。

```csharp
// 開発時のみ使用。本番リカバリはバックアップ復元で対応
protected override void Down(MigrationBuilder migrationBuilder)
{
    migrationBuilder.DropTable("Projects");
}
```

---

## 5. よくある失敗パターンと対策

| 失敗パターン | 対策 |
|-------------|------|
| バックアップなしで `MigrateAsync` を呼ぶ | 必ず `BackupIfSqliteAsync` を先に実行する |
| 例外をキャッチせずアプリがクラッシュ | `try/catch` でユーザー向けダイアログを表示してから再スロー |
| 誤った DB ファイルにマイグレーション適用 | 起動時に DB パスをログ出力して確認できるようにする |
| `Migrations/` フォルダをコミットし忘れ | `<timestamp>_<name>.cs` とスナップショットをすべてコミットする |
| マルチインスタンス起動による競合 | ファイルロックまたは `Mutex` で起動を直列化する |

---

## 6. まとめ：推奨起動フロー

```
アプリ起動
  ↓
BackupIfSqliteAsync()  ← SQLite ファイルをタイムスタンプ付きでコピー
  ↓
CheckVersionGapAsync() ← 大量ギャップがあればユーザーに確認
  ↓
db.Database.MigrateAsync()
  ↓ 成功           ↓ 失敗
MainWindow 表示   MessageBox でエラー通知 → アプリ終了
                  （バックアップが残っているので復元可能）
```

バックアップは「保険」ではなく「必須インフラ」として位置づけ、マイグレーションと常にセットで実装してください。
