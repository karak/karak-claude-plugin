# .NET 10 WPF + Serilog: Generic Host + appsettings.json による完全セットアップ

## 前提パッケージ

```xml
<!-- MyWpfApp.csproj -->
<Project Sdk="Microsoft.NET.Sdk">
  <PropertyGroup>
    <OutputType>WinExe</OutputType>
    <TargetFramework>net10.0-windows</TargetFramework>
    <UseWPF>true</UseWPF>
    <Nullable>enable</Nullable>
    <ImplicitUsings>enable</ImplicitUsings>
  </PropertyGroup>

  <ItemGroup>
    <!-- Generic Host -->
    <PackageReference Include="Microsoft.Extensions.Hosting" Version="10.0.0" />

    <!-- Serilog コア -->
    <PackageReference Include="Serilog" Version="4.2.0" />
    <PackageReference Include="Serilog.Extensions.Hosting" Version="8.0.0" />
    <PackageReference Include="Serilog.Settings.Configuration" Version="8.0.4" />

    <!-- シンク -->
    <PackageReference Include="Serilog.Sinks.File" Version="6.0.0" />
    <PackageReference Include="Serilog.Sinks.EventLog" Version="4.0.0" />

    <!-- appsettings.json 読み込み -->
    <PackageReference Include="Microsoft.Extensions.Configuration.Json" Version="10.0.0" />
  </ItemGroup>

  <ItemGroup>
    <!-- appsettings.json をビルド出力にコピー -->
    <None Update="appsettings.json">
      <CopyToOutputDirectory>PreserveNewest</CopyToOutputDirectory>
    </None>
  </ItemGroup>
</Project>
```

> **バージョン選定の補足**
> Serilog 本体は 2025 年 4 月時点の最新安定版 4.x 系。`Serilog.Extensions.Hosting` 8.x は .NET 8/9/10 の `IHostBuilder` / `HostApplicationBuilder` に対応。パッケージバージョンは `dotnet outdated` で随時更新してください。

---

## appsettings.json

```json
{
  "Serilog": {
    "Using": [
      "Serilog.Sinks.File",
      "Serilog.Sinks.EventLog"
    ],
    "MinimumLevel": {
      "Default": "Information",
      "Override": {
        "Microsoft": "Warning",
        "System": "Warning"
      }
    },
    "WriteTo": [
      {
        "Name": "File",
        "Args": {
          "path": "logs/myapp-.log",
          "rollingInterval": "Day",
          "retainedFileCountLimit": 30,
          "outputTemplate": "{Timestamp:yyyy-MM-dd HH:mm:ss.fff zzz} [{Level:u3}] {SourceContext} {Message:lj}{NewLine}{Exception}"
        }
      },
      {
        "Name": "Logger",
        "Args": {
          "configureLogger": {
            "Filter": [
              {
                "Name": "ByIncludingOnly",
                "Args": {
                  "expression": "@l = 'Warning' or @l = 'Error' or @l = 'Fatal'"
                }
              }
            ],
            "WriteTo": [
              {
                "Name": "EventLog",
                "Args": {
                  "source": "MyWpfApp",
                  "logName": "Application",
                  "outputTemplate": "{Timestamp:yyyy-MM-dd HH:mm:ss} [{Level}] {SourceContext}{NewLine}{Message:lj}{NewLine}{Exception}"
                }
              }
            ]
          }
        }
      }
    ],
    "Enrich": [
      "FromLogContext",
      "WithMachineName",
      "WithThreadId"
    ]
  }
}
```

### ポイント

| 設定キー | 説明 |
|---|---|
| `rollingInterval: "Day"` | ファイル名に `yyyyMMdd` が付き日次ローテーション |
| `retainedFileCountLimit: 30` | 30 日分を上限に古いファイルを自動削除 |
| 子 `Logger` + `Filter` | `Warning` 以上のみ EventLog シンクへ流すサブロガー |
| `source` (EventLog) | Windows イベントビューアーの「ソース」名。初回書き込み時に自動登録される（要管理者権限） |

---

## Program.cs（エントリーポイント）

```csharp
using Microsoft.Extensions.DependencyInjection;
using Microsoft.Extensions.Hosting;
using Serilog;

// ---- ブートストラップロガー（Host 構築失敗時のクラッシュログ用） ----
Log.Logger = new LoggerConfiguration()
    .MinimumLevel.Warning()
    .WriteTo.File(
        "logs/bootstrap-.log",
        rollingInterval: RollingInterval.Day,
        retainedFileCountLimit: 7)
    .CreateBootstrapLogger();

try
{
    var host = Host.CreateDefaultBuilder(args)
        .UseSerilog((ctx, services, lc) =>
            lc.ReadFrom.Configuration(ctx.Configuration)
              .ReadFrom.Services(services))
        .ConfigureServices((ctx, services) =>
        {
            // WPF Application をシングルトンとして登録
            services.AddSingleton<App>();
            services.AddSingleton<MainWindow>();
        })
        .Build();

    // WPF の STA スレッドで Application.Run を起動
    var app = host.Services.GetRequiredService<App>();
    var mainWindow = host.Services.GetRequiredService<MainWindow>();

    // Host のライフタイム管理を開始（バックグラウンドサービス等）
    await host.StartAsync();

    app.Run(mainWindow);

    await host.StopAsync();
}
catch (Exception ex)
{
    Log.Fatal(ex, "アプリケーションの起動に失敗しました");
}
finally
{
    // バッファされたログを確実にフラッシュしてからプロセスを終了
    await Log.CloseAndFlushAsync();
}
```

> **STA スレッドの注意**
> WPF は STA（Single-Threaded Apartment）を必須とします。`[STAThread]` 属性は `Program.cs` のエントリーポイントに付与するか、SDK スタイルプロジェクトでは `<ApplicationManifest>` 経由で設定してください。`Host.CreateDefaultBuilder` はデフォルトで MTA スレッドを使うため、`app.Run(mainWindow)` は必ず STA スレッド上で呼ぶ必要があります。詳細は後述の「STA スレッド対応」セクションを参照してください。

---

## App.xaml の変更

`StartupUri` を削除し、Generic Host 経由でウィンドウを生成します。

```xml
<!-- App.xaml -->
<Application x:Class="MyWpfApp.App"
             xmlns="http://schemas.microsoft.com/winfx/2006/xaml/presentation"
             xmlns:x="http://schemas.microsoft.com/winfx/2006/xaml">
    <!-- StartupUri は削除 — Program.cs が MainWindow をインジェクトする -->
    <Application.Resources />
</Application>
```

```csharp
// App.xaml.cs
using System.Windows;

namespace MyWpfApp;

public partial class App : Application
{
    // OnStartup をオーバーライドしない。
    // Program.cs の app.Run(mainWindow) が Startup イベントを代替する。
}
```

---

## MainWindow（ログ使用例）

```csharp
// MainWindow.xaml.cs
using Microsoft.Extensions.Logging;
using System.Windows;

namespace MyWpfApp;

public partial class MainWindow : Window
{
    private readonly ILogger<MainWindow> _logger;

    public MainWindow(ILogger<MainWindow> logger)
    {
        _logger = logger;
        InitializeComponent();
    }

    protected override void OnInitialized(EventArgs e)
    {
        base.OnInitialized(e);
        _logger.LogInformation("MainWindow が初期化されました");
    }

    private void Button_Click(object sender, RoutedEventArgs e)
    {
        // Information → ファイルのみ
        _logger.LogInformation("ボタンがクリックされました");

        // Warning → ファイル + Windows イベントログ
        _logger.LogWarning("警告: 何か問題が発生しました");

        // Error → ファイル + Windows イベントログ
        try
        {
            throw new InvalidOperationException("テスト例外");
        }
        catch (Exception ex)
        {
            _logger.LogError(ex, "エラーが発生しました");
        }
    }
}
```

---

## STA スレッド対応（重要）

.NET SDK スタイルプロジェクトでは `[STAThread]` が自動付与されません。以下いずれかの方法で対応してください。

### 方法 A: `Program.cs` に明示的に付与

```csharp
// Program.cs の先頭 — async エントリーポイントには直接付与できないため
// EntryPoint クラスを分離する方法を採用する

using Microsoft.Extensions.DependencyInjection;
using Microsoft.Extensions.Hosting;
using Serilog;

// async エントリーポイントを別クラスに移譲するパターン
internal static class Program
{
    [STAThread]
    public static void Main(string[] args)
    {
        // ブートストラップロガー
        Log.Logger = new LoggerConfiguration()
            .MinimumLevel.Warning()
            .WriteTo.File("logs/bootstrap-.log", rollingInterval: RollingInterval.Day)
            .CreateBootstrapLogger();

        try
        {
            var host = Host.CreateDefaultBuilder(args)
                .UseSerilog((ctx, services, lc) =>
                    lc.ReadFrom.Configuration(ctx.Configuration)
                      .ReadFrom.Services(services))
                .ConfigureServices((ctx, services) =>
                {
                    services.AddSingleton<App>();
                    services.AddSingleton<MainWindow>();
                })
                .Build();

            host.Start();

            var app = host.Services.GetRequiredService<App>();
            var mainWindow = host.Services.GetRequiredService<MainWindow>();

            // STA スレッド上で実行されているため app.Run は安全
            app.Run(mainWindow);

            host.StopAsync().GetAwaiter().GetResult();
        }
        catch (Exception ex)
        {
            Log.Fatal(ex, "アプリケーションの起動に失敗しました");
        }
        finally
        {
            Log.CloseAndFlushAsync().GetAwaiter().GetResult();
        }
    }
}
```

### 方法 B: プロジェクトファイルで ApplicationManifest を指定

```xml
<PropertyGroup>
  <ApplicationManifest>app.manifest</ApplicationManifest>
</PropertyGroup>
```

---

## Windows イベントログのソース登録（管理者権限が必要）

初回実行時に `Serilog.Sinks.EventLog` が自動でイベントソースを登録しようとしますが、**管理者権限がない場合は失敗**します。インストーラーやセットアップスクリプトで事前登録することを推奨します。

```powershell
# インストール時に一度だけ実行（管理者権限）
New-EventLog -LogName Application -Source "MyWpfApp"
```

または C# のセットアップコードから:

```csharp
using System.Diagnostics;

// インストーラー等のセットアップコードで一度だけ呼ぶ
if (!EventLog.SourceExists("MyWpfApp"))
{
    EventLog.CreateEventSource("MyWpfApp", "Application");
}
```

---

## ディレクトリ構成（最終形）

```
MyWpfApp/
├── MyWpfApp.csproj
├── appsettings.json          ← Serilog 設定
├── Program.cs                ← [STAThread] + Generic Host エントリーポイント
├── App.xaml                  ← StartupUri なし
├── App.xaml.cs
└── MainWindow.xaml(.cs)      ← ILogger<T> インジェクション
```

---

## 動作確認チェックリスト

- [ ] `logs/myapp-yyyyMMdd.log` にログが書き出される
- [ ] `Warning` 以上のログが「Windows イベントビューアー > Windows ログ > アプリケーション」の「MyWpfApp」ソースに表示される
- [ ] アプリ終了後、翌日に起動すると新しい日付のログファイルが生成される
- [ ] 31 日以上経過したログファイルが自動削除される（`retainedFileCountLimit: 30`）
- [ ] DI コンテナから `ILogger<T>` を取得して各クラスでログを書けている
