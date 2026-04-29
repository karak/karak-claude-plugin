# .NET 10 WPF + Serilog — Generic Host / appsettings.json ベース完全セットアップ

---

## 1. NuGet パッケージ

```xml
<!-- MyApp.csproj -->
<PackageReference Include="Serilog.Extensions.Hosting"   Version="8.*" />
<PackageReference Include="Serilog.Settings.Configuration" Version="8.*" />
<PackageReference Include="Serilog.Sinks.File"            Version="5.*" />
<PackageReference Include="Serilog.Sinks.EventLog"        Version="3.*" />
<PackageReference Include="Serilog.Enrichers.Thread"      Version="3.*" />
<PackageReference Include="Serilog.Enrichers.Environment" Version="2.*" />
```

---

## 2. appsettings.json

```json
{
  "Serilog": {
    "MinimumLevel": {
      "Default": "Information",
      "Override": {
        "Microsoft": "Warning",
        "System":    "Warning"
      }
    },
    "WriteTo": [
      {
        "Name": "File",
        "Args": {
          "path":                   "%LOCALAPPDATA%/MyApp/logs/app-.log",
          "rollingInterval":        "Day",
          "retainedFileCountLimit": 30,
          "outputTemplate":         "{Timestamp:yyyy-MM-dd HH:mm:ss.fff zzz} [{Level:u3}] {Message:lj}{NewLine}{Exception}"
        }
      },
      {
        "Name": "EventLog",
        "Args": {
          "source":                    "MyApp",
          "logName":                   "Application",
          "restrictedToMinimumLevel":  "Warning"
        }
      }
    ]
  }
}
```

**ポイント:**
- `rollingInterval: "Day"` + `retainedFileCountLimit: 30` で日次ローテーション・30 日分保持。
- `EventLog` sink の `restrictedToMinimumLevel: "Warning"` により Warning 以上のみ Windows イベントログへ書き込む。
- `Microsoft.*` / `System.*` を `Warning` に上書きすることで、フレームワーク内部ログによるログ肥大を防ぐ。

---

## 3. App.xaml.cs — ブートストラップ + Global Exception 処理

```csharp
using System.Diagnostics;
using System.Windows;
using Microsoft.Extensions.DependencyInjection;
using Microsoft.Extensions.Hosting;
using Serilog;

namespace MyApp;

public partial class App : Application
{
    private IHost? _host;

    protected override async void OnStartup(StartupEventArgs e)
    {
        // ─── グローバル例外ハンドラ（ホスト起動前に登録） ───────────────────
        DispatcherUnhandledException += (_, args) =>
        {
            Log.Fatal(args.Exception, "Unhandled UI thread exception");
            Log.CloseAndFlush();          // 非同期シンクを確実にフラッシュ
            args.Handled = false;         // Windows にクラッシュダイアログを表示させる
        };

        TaskScheduler.UnobservedTaskException += (_, args) =>
        {
            Log.Error(args.Exception, "Unobserved Task exception");
            args.SetObserved();           // プロセス終了を回避
        };

        AppDomain.CurrentDomain.UnhandledException += (_, args) =>
        {
            Log.Fatal(args.ExceptionObject as Exception,
                      "AppDomain unhandled exception");
            Log.CloseAndFlush();
        };

        // ─── 設定ファイルを先読みしてブートストラップロガーを生成 ────────────
        var configuration = new ConfigurationBuilder()
            .SetBasePath(AppContext.BaseDirectory)
            .AddJsonFile("appsettings.json", optional: false, reloadOnChange: true)
            .Build();

        Log.Logger = new LoggerConfiguration()
            .ReadFrom.Configuration(configuration)
            .Enrich.FromLogContext()
            .Enrich.WithThreadId()
            .Enrich.WithMachineName()
            .CreateBootstrapLogger();

        // ─── Windows イベントログのソース登録チェック ─────────────────────
        if (!EventLog.SourceExists("MyApp"))
            Log.Warning("EventLog source 'MyApp' is not registered. " +
                        "Run the installer as administrator.");

        // ─── Generic Host 構築 ────────────────────────────────────────────
        _host = Host.CreateDefaultBuilder(e.Args)
            .UseSerilog((ctx, services, cfg) => cfg
                .ReadFrom.Configuration(ctx.Configuration)  // appsettings.json を参照
                .ReadFrom.Services(services)                 // DI 登録済みエンリッチャーも反映
                .Enrich.FromLogContext())
            .ConfigureServices((ctx, services) =>
            {
                // ViewModel や Window を DI 登録
                services.AddSingleton<MainWindow>();
                // 例: services.AddSingleton<IMyService, MyService>();
            })
            .Build();

        await _host.StartAsync();

        var mainWindow = _host.Services.GetRequiredService<MainWindow>();
        mainWindow.Show();

        base.OnStartup(e);
    }

    protected override async void OnExit(ExitEventArgs e)
    {
        if (_host is not null)
        {
            await _host.StopAsync(TimeSpan.FromSeconds(5));
            _host.Dispose();
        }
        Log.CloseAndFlush();   // 終了時も必ずフラッシュ
        base.OnExit(e);
    }
}
```

---

## 4. ViewModel での ILogger 使用例

```csharp
using Microsoft.Extensions.Logging;

namespace MyApp.ViewModels;

public class MainViewModel
{
    private readonly ILogger<MainViewModel> _logger;

    public MainViewModel(ILogger<MainViewModel> logger)
    {
        _logger = logger;
    }

    public void LoadProject(string projectId)
    {
        var sw = System.Diagnostics.Stopwatch.StartNew();

        // 構造化ログ — メッセージテンプレートを使い、文字列結合は絶対に使わない
        _logger.LogInformation("Project {ProjectId} load started", projectId);

        try
        {
            // ... 実際のロード処理 ...
            sw.Stop();
            _logger.LogInformation("Project {ProjectId} loaded in {ElapsedMs}ms",
                                   projectId, sw.ElapsedMilliseconds);
        }
        catch (Exception ex)
        {
            _logger.LogError(ex, "Failed to load project {ProjectId}", projectId);
            throw;
        }
    }
}
```

---

## 5. Windows イベントログ ソース登録（インストール時・管理者権限）

```powershell
# インストーラーまたは管理者 PowerShell で一度だけ実行
New-EventLog -LogName Application -Source "MyApp"
```

---

## 6. よくある落とし穴と対策

| 落とし穴 | 対策 |
|----------|------|
| クラッシュ直前のログが消える | `DispatcherUnhandledException` / `AppDomain.UnhandledException` の両方に `Log.CloseAndFlush()` を追加 |
| 非同期シンクがフラッシュされない | `OnExit` で `Log.CloseAndFlush()` を必ず呼ぶ |
| EventLog への書き込みが失敗する | 起動時に `EventLog.SourceExists("MyApp")` を確認し、未登録なら Warning ログを出す |
| Microsoft.*/System.* のログが大量に出る | `appsettings.json` の `Override` で `Warning` に絞る |
| 構造化プロパティが失われる | 文字列結合 (`"Value: " + x`) でなく必ずメッセージテンプレート (`"Value: {X}", x`) を使う |
| 複数プロセスでログファイルがロックされる | File sink の Args に `"shared": true` を追加 |

---

## 設定サマリー

| 要件 | 実装箇所 |
|------|----------|
| Generic Host への統合 | `Host.CreateDefaultBuilder().UseSerilog(...)` |
| appsettings.json からの設定読み込み | `ReadFrom.Configuration(ctx.Configuration)` |
| 日次ローテーション | `rollingInterval: "Day"` + `retainedFileCountLimit: 30` |
| Warning 以上のみ Windows イベントログ | EventLog sink の `restrictedToMinimumLevel: "Warning"` |
| グローバルクラッシュキャプチャ | `DispatcherUnhandledException` + `AppDomain.UnhandledException` + `Log.Fatal` + `CloseAndFlush` |
