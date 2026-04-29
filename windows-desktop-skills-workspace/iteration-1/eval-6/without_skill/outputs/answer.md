# .NET 10 WPF + SQLite + EF Core: 自動マイグレーションのバックアップとエラーハンドリング ベストプラクティス

## 概要

デスクトップアプリの起動時自動マイグレーションは、失敗するとデータが破損する可能性があります。以下のパターンを組み合わせることで、安全なリカバリ体制を構築できます。

---

## 1. マイグレーション前のバックアップ

### 1-1. 保留中マイグレーションの確認とバックアップの条件分岐

```csharp
public static class DatabaseInitializer
{
    public static async Task InitializeAsync(IServiceProvider services, ILogger logger)
    {
        await using var scope = services.CreateAsyncScope();
        var db = scope.ServiceProvider.GetRequiredService<AppDbContext>();

        // 保留中マイグレーションが存在するときだけバックアップを取る
        var pending = (await db.Database.GetPendingMigrationsAsync()).ToList();
        if (pending.Count == 0)
        {
            logger.LogInformation("No pending migrations.");
            return;
        }

        logger.LogInformation("Pending migrations: {Migrations}", string.Join(", ", pending));

        var dbPath = GetDatabasePath(db);
        var backupPath = CreateBackup(dbPath, logger);

        try
        {
            await db.Database.MigrateAsync();
            logger.LogInformation("Migration completed successfully.");
        }
        catch (Exception ex)
        {
            logger.LogError(ex, "Migration failed. Restoring backup from {BackupPath}", backupPath);
            RestoreBackup(dbPath, backupPath, logger);
            throw; // 上位でユーザーに通知する
        }
    }
}
```

### 1-2. バックアップの実装

```csharp
private static string CreateBackup(string dbPath, ILogger logger)
{
    if (!File.Exists(dbPath))
        return string.Empty; // 新規インストールはバックアップ不要

    var timestamp = DateTime.Now.ToString("yyyyMMdd_HHmmss");
    var backupDir = Path.Combine(Path.GetDirectoryName(dbPath)!, "backups");
    Directory.CreateDirectory(backupDir);

    var backupPath = Path.Combine(backupDir, $"app_{timestamp}.db.bak");

    // SQLite は WAL モードでも File.Copy が安全（接続を閉じてから）
    File.Copy(dbPath, backupPath, overwrite: false);
    logger.LogInformation("Backup created: {BackupPath}", backupPath);

    // 古いバックアップを 5 世代まで保持
    PruneOldBackups(backupDir, keepCount: 5, logger);

    return backupPath;
}

private static void RestoreBackup(string dbPath, string backupPath, ILogger logger)
{
    if (string.IsNullOrEmpty(backupPath) || !File.Exists(backupPath))
    {
        logger.LogWarning("No backup to restore.");
        return;
    }

    File.Copy(backupPath, dbPath, overwrite: true);
    logger.LogInformation("Database restored from backup.");
}

private static void PruneOldBackups(string backupDir, int keepCount, ILogger logger)
{
    var files = Directory.GetFiles(backupDir, "*.db.bak")
                         .OrderByDescending(File.GetCreationTime)
                         .Skip(keepCount)
                         .ToList();

    foreach (var file in files)
    {
        File.Delete(file);
        logger.LogDebug("Deleted old backup: {File}", file);
    }
}
```

### 1-3. データベースファイルパスの取得

```csharp
private static string GetDatabasePath(DbContext db)
{
    var connectionString = db.Database.GetConnectionString()!;
    // "Data Source=C:\Users\...\app.db" 形式を想定
    var builder = new Microsoft.Data.Sqlite.SqliteConnectionStringBuilder(connectionString);
    return Path.GetFullPath(builder.DataSource);
}
```

---

## 2. App.xaml.cs でのエラーハンドリング

```csharp
public partial class App : Application
{
    private IHost? _host;

    protected override async void OnStartup(StartupEventArgs e)
    {
        base.OnStartup(e);

        _host = Host.CreateDefaultBuilder()
            .ConfigureServices(ConfigureServices)
            .Build();

        try
        {
            await DatabaseInitializer.InitializeAsync(_host.Services, GetLogger());
        }
        catch (MigrationException ex)
        {
            ShowMigrationError(ex);
            Shutdown(exitCode: 1);
            return;
        }
        catch (Exception ex)
        {
            ShowUnexpectedError(ex);
            Shutdown(exitCode: 1);
            return;
        }

        await _host.StartAsync();
        new MainWindow().Show();
    }

    private void ShowMigrationError(Exception ex)
    {
        var message =
            "データベースの更新中にエラーが発生しました。\n\n" +
            "バックアップから自動的に復元しました。\n" +
            "アプリを再起動してください。\n\n" +
            $"詳細: {ex.Message}";

        MessageBox.Show(message, "起動エラー", MessageBoxButton.OK, MessageBoxImage.Error);
    }
}
```

---

## 3. WAL モードと PRAGMA による SQLite の安定化

マイグレーション実行前に SQLite の耐障害性を高める設定を適用します。

```csharp
protected override void OnConfiguring(DbContextOptionsBuilder options)
{
    options.UseSqlite(
        "Data Source=app.db",
        o => o.CommandTimeout(60)
    );
}

// DbContext.SaveChanges の前に一度だけ実行する初期化
public static async Task ConfigureSqliteAsync(AppDbContext db)
{
    // Write-Ahead Logging: クラッシュ時のデータ破損リスクを低減
    await db.Database.ExecuteSqlRawAsync("PRAGMA journal_mode=WAL;");
    // バックアップ後にチェックポイントを強制実行しない（バックアップ整合性向上）
    await db.Database.ExecuteSqlRawAsync("PRAGMA wal_autocheckpoint=1000;");
    // 同期モードを NORMAL に（FULL より高速かつ十分安全）
    await db.Database.ExecuteSqlRawAsync("PRAGMA synchronous=NORMAL;");
}
```

---

## 4. ロールバック戦略の整理

| シナリオ | 対処方法 |
|---|---|
| マイグレーション実行中にクラッシュ | WAL モードにより自動ロールバック、コピーしたバックアップで上書き復元 |
| マイグレーション自体のバグ（データ消失） | バックアップから復元後、アプリ更新を待つ |
| 新規インストール（DB が存在しない） | バックアップ不要、`MigrateAsync` のみ実行 |
| ディスク容量不足でバックアップ失敗 | バックアップ失敗時は `IOException` をキャッチし、ユーザーに警告して続行を選択させる |

---

## 5. ユーザーへの選択肢提供（ダイアログ）

重要なマイグレーションの前にユーザーへ確認を取るパターンも有効です。

```csharp
private static async Task<bool> ConfirmMigrationWithUserAsync(List<string> pending)
{
    var message =
        $"アプリの更新に伴い、データベースを更新します（{pending.Count} 件）。\n\n" +
        "続行する前にバックアップが自動作成されます。\n" +
        "続行しますか？";

    var result = MessageBox.Show(
        message,
        "データベース更新",
        MessageBoxButton.YesNo,
        MessageBoxImage.Information
    );

    return result == MessageBoxResult.Yes;
}
```

---

## 6. ログの記録

`Microsoft.Extensions.Logging` を使い、マイグレーション前後の状態をログファイルに記録します。ユーザー PC でのサポート対応に役立ちます。

```csharp
// Program.cs または Host 設定
services.AddLogging(b =>
{
    b.AddConsole();
    b.AddFile(Path.Combine(
        Environment.GetFolderPath(Environment.SpecialFolder.LocalApplicationData),
        "YourApp", "logs", "app-.log"
    )); // Serilog や NLog を使う場合はそちらで設定
});
```

---

## 7. まとめ：推奨フロー

```
起動
  └─ 保留マイグレーション確認
       ├─ なし → そのまま起動
       └─ あり
            ├─ バックアップ作成（.db.bak）
            ├─ MigrateAsync() 実行
            │    ├─ 成功 → 古いバックアップを世代管理して起動
            │    └─ 失敗
            │         ├─ バックアップから .db を上書き復元
            │         ├─ エラーダイアログ表示
            │         └─ アプリ終了（exitCode: 1）
            └─ ログ記録（成功・失敗どちらも）
```

### ポイントまとめ

- バックアップは **マイグレーション前にのみ** 作成し、世代数を制限する（例：5世代）。
- `MigrateAsync()` は必ず `try-catch` で囲み、失敗時はバックアップから自動復元する。
- SQLite の WAL モードを有効にして、クラッシュ時の破損リスクを下げる。
- エラーは必ずログに記録し、ユーザーには分かりやすいメッセージを表示する。
- 新規インストール（DB ファイルなし）と既存DB更新を条件分岐で明確に区別する。
