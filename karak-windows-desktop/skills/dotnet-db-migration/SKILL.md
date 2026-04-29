---
name: dotnet-db-migration
description: Use when managing database schema changes for a .NET 10 WPF application — adding EF Core migrations, applying them at startup, handling rollback, or dealing with SQLite offline upgrade scenarios (backup-before-migrate, version gap detection, user notification on failure). Also use when choosing between EF Core Migrations and FluentMigrator.
---

# .NET 10 WPF — Database Migration

## Overview

EF Core Migrations is the default for most WPF apps. FluentMigrator is the alternative when EF Core isn't used or when migration scripts need to be version-controlled independently.

**Desktop-specific rule:** Always back up the SQLite file before calling `MigrateAsync()`. A failed migration on a user's machine cannot be rolled back by a DBA — you own the recovery path.

---

## EF Core Migrations — Core Workflow

```bash
# Add a migration
dotnet ef migrations add AddProjectTable --project src/Infrastructure --startup-project src/MyApp

# Generate a SQL script (for review before prod)
dotnet ef migrations script --idempotent --output migrations.sql

# Apply to database
dotnet ef database update
```

**Key files:**
- `Migrations/<timestamp>_<name>.cs` — `Up()` and `Down()` methods
- `Migrations/<name>ModelSnapshot.cs` — current schema snapshot (commit this)

---

## Apply Migrations at App Startup

```csharp
// In host startup, before MainWindow shows
public static class DbStartup
{
    public static async Task MigrateAsync(IServiceProvider services, ILogger logger)
    {
        using var scope = services.CreateScope();
        var db = scope.ServiceProvider.GetRequiredService<AppDbContext>();

        await BackupIfSqliteAsync(db, logger);

        try
        {
            await db.Database.MigrateAsync();
        }
        catch (Exception ex)
        {
            logger.LogError(ex, "Migration failed");
            // Show user-facing error dialog before exiting
            MessageBox.Show(
                "データベースの更新に失敗しました。\nサポートにお問い合わせください。\n\n" + ex.Message,
                "起動エラー", MessageBoxButton.OK, MessageBoxImage.Error);
            throw; // let the app exit
        }
    }
}
```

---

## Desktop-Specific: Backup Before Migrate

```csharp
private static async Task BackupIfSqliteAsync(AppDbContext db, ILogger logger)
{
    var connStr = db.Database.GetConnectionString() ?? "";
    // Extract file path from "Data Source=C:\...\app.db"
    var match = Regex.Match(connStr, @"Data Source=([^;]+)", RegexOptions.IgnoreCase);
    if (!match.Success) return;

    var dbPath = match.Groups[1].Value.Trim();
    if (!File.Exists(dbPath)) return;

    var backupPath = dbPath + $".bak.{DateTime.Now:yyyyMMddHHmmss}";
    File.Copy(dbPath, backupPath, overwrite: true);
    logger.LogInformation("Database backed up to {BackupPath}", backupPath);

    // Keep only last 5 backups
    var backups = Directory.GetFiles(Path.GetDirectoryName(dbPath)!, "*.bak.*")
                            .OrderByDescending(f => f).Skip(5);
    foreach (var old in backups) File.Delete(old);
}
```

---

## Version Gap Detection (v1 → v3 skip upgrade)

EF Core handles gaps automatically (`MigrateAsync` applies all pending migrations in order), but you should detect and warn for large gaps:

```csharp
public static async Task<bool> CheckVersionGapAsync(AppDbContext db, ILogger logger)
{
    var applied = await db.Database.GetAppliedMigrationsAsync();
    var pending = (await db.Database.GetPendingMigrationsAsync()).ToList();

    if (pending.Count > 5)
    {
        logger.LogWarning("Large migration gap detected: {Count} pending migrations", pending.Count);

        var proceed = MessageBox.Show(
            $"データベースを {pending.Count} バージョン更新する必要があります。\n" +
            "この処理には時間がかかる場合があります。続行しますか？",
            "データベース更新", MessageBoxButton.YesNo, MessageBoxImage.Question);

        if (proceed == MessageBoxResult.No)
        {
            Application.Current.Shutdown();
            return false;
        }
    }
    return true;
}
```

---

## Rollback Strategy

EF Core's `Down()` is rarely used in production desktop scenarios — it's safer to restore the backup. Document this in team conventions:

```csharp
// Down() — implement for dev convenience, but production recovery = restore backup
protected override void Down(MigrationBuilder migrationBuilder)
{
    migrationBuilder.DropTable("Projects");
}
```

For SQL Server (non-SQLite), `Down()` + a transaction is viable. For SQLite, prefer backup restore.

---

## FluentMigrator (EF Core alternative)

Use when: migration scripts must be DB-agnostic, reviewed as plain SQL, or run outside the app.

```csharp
[Migration(202410010001)]
public class AddProjectTable : Migration
{
    public override void Up()
    {
        Create.Table("Projects")
            .WithColumn("Id").AsGuid().PrimaryKey()
            .WithColumn("Name").AsString(200).NotNullable()
            .WithColumn("CreatedAt").AsDateTime2().NotNullable();
    }

    public override void Down() => Delete.Table("Projects");
}
```

```csharp
// Registration
services.AddFluentMigratorCore()
    .ConfigureRunner(rb => rb
        .AddSQLite()
        .WithGlobalConnectionString(connectionString)
        .ScanIn(typeof(AddProjectTable).Assembly).For.Migrations())
    .AddLogging(lb => lb.AddSerilog());

// Apply
var runner = host.Services.GetRequiredService<IMigrationRunner>();
runner.MigrateUp();
```

---

## Common Mistakes

| Mistake | Fix |
|---------|-----|
| No backup before `MigrateAsync` | Always copy SQLite file first — see BackupIfSqliteAsync above |
| Migration applied to wrong database | Use environment-specific connection strings; log the DB path at startup |
| `__EFMigrationsHistory` not committed | Commit all `Migrations/` files including the snapshot |
| Concurrent migration on multi-instance startup | Use `Database.EnsureCreated()` with a file lock, or serialize startup |
| User sees crash on migration failure | Wrap `MigrateAsync` in try/catch with a user-friendly dialog |

---

## Quick Reference

| Task | Command / API |
|------|---------------|
| Add migration | `dotnet ef migrations add <Name>` |
| Apply at startup | `db.Database.MigrateAsync()` |
| Check pending | `db.Database.GetPendingMigrationsAsync()` |
| Generate SQL script | `dotnet ef migrations script --idempotent` |
| Backup SQLite | `File.Copy(dbPath, backupPath)` before migrate |
| Remove last migration | `dotnet ef migrations remove` |
