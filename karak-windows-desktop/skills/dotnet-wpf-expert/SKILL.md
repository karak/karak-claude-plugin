---
name: dotnet-wpf-expert
description: Use when developing WPF/XAML applications with .NET 10, designing MVVM architecture, implementing UI components, or working with data binding, commands, and navigation patterns. Covers PresentationCore, dependency properties, and common pitfalls in WPF desktop app development.
---

# .NET 10 WPF / XAML Expert

## Overview

WPF（Windows Presentation Foundation）は .NET 10 上の XAML ベースデスクトップ UI フレームワーク。MVVM パターンと豊富なデータバインディングが強み。

**Core principle:** ViewModel は View を知らず、View は ViewModel を INotifyPropertyChanged 経由で観察する。

## MVVM 構造

```
App/
  Models/         # ドメインエンティティ・データ構造
  ViewModels/     # INotifyPropertyChanged / ObservableObject 継承
  Views/          # XAML + コードビハインド（最小限）
  Services/       # ビジネスロジック・インフラ抽象化（インターフェース）
  Converters/     # IValueConverter 実装
```

## 依存性注入（.NET 10 Generic Host）

```csharp
// App.xaml.cs
protected override void OnStartup(StartupEventArgs e)
{
    var host = Host.CreateDefaultBuilder()
        .ConfigureServices(services =>
        {
            services.AddSingleton<MainWindow>();
            services.AddSingleton<MainViewModel>();
            services.AddTransient<IUserService, UserService>();
        })
        .Build();
    host.Services.GetRequiredService<MainWindow>().Show();
}
```

## ViewModel 基本パターン（CommunityToolkit.Mvvm）

```csharp
using CommunityToolkit.Mvvm.ComponentModel;
using CommunityToolkit.Mvvm.Input;

public partial class MainViewModel : ObservableObject
{
    [ObservableProperty]
    private string _title = "Hello";

    [ObservableProperty]
    [NotifyCanExecuteChangedFor(nameof(SaveCommand))]
    private bool _isDirty;

    private bool CanSaveAsync() => IsDirty;

    [RelayCommand(CanExecute = nameof(CanSaveAsync))]
    private async Task SaveAsync(CancellationToken ct)
    {
        await _service.SaveAsync(ct);
        IsDirty = false;
    }
}
```

**なぜ CommunityToolkit.Mvvm か:** ソースジェネレータで INotifyPropertyChanged ボイラープレートを排除。Prism より軽量で .NET 10 native 対応。

## Prism（大規模アプリ・モジュール分割）

Prism はモジュール分割・リージョン・ナビゲーションが必要な大規模アプリ向け。

```csharp
// PrismApplication 継承
protected override void RegisterTypes(IContainerRegistry container)
{
    container.RegisterForNavigation<UserView, UserViewModel>("User");
    container.Register<IUserService, UserService>();
}

// ViewModel でナビゲーション
_regionManager.RequestNavigate("ContentRegion", "User",
    new NavigationParameters { { "id", userId } });
```

**CommunityToolkit vs Prism 選択:**
- 小〜中規模、シンプルな DI → CommunityToolkit.Mvvm
- モジュール分割、プラグイン構成、シェルアプリ → Prism

## データバインディング

```xml
<!-- 双方向バインディング -->
<TextBox Text="{Binding UserName, Mode=TwoWay, UpdateSourceTrigger=PropertyChanged}" />

<!-- コマンドバインディング -->
<Button Command="{Binding SaveCommand}" CommandParameter="{Binding SelectedItem}" />

<!-- DataTemplate -->
<ItemsControl ItemsSource="{Binding Items}">
    <ItemsControl.ItemTemplate>
        <DataTemplate DataType="{x:Type vm:ItemViewModel}">
            <TextBlock Text="{Binding Name}" />
        </DataTemplate>
    </ItemsControl.ItemTemplate>
</ItemsControl>
```

## よくある落とし穴

| 落とし穴 | 原因 | 対策 |
|---------|------|------|
| バインディングが更新されない | INotifyPropertyChanged 未実装 / プロパティ名ミス | ObservableObject 継承 + `[ObservableProperty]` |
| UI スレッドエラー | バックグラウンドスレッドから UI 操作 | `Application.Current.Dispatcher.InvokeAsync` or `await` で UI スレッドへ戻す |
| メモリリーク | イベントハンドラの購読解除忘れ | WeakEventManager / `IDisposable` + Unsubscribe |
| CollectionChanged が来ない | `List<T>` を直接使用 | `ObservableCollection<T>` に変更 |
| XAML デザイナーがクラッシュ | ViewModel コンストラクタで重い処理 | デザイン時は `DesignerProperties.GetIsInDesignMode` でスキップ |
| DependencyProperty の変更通知なし | CLR プロパティで DependencyProperty をラップしていない | `GetValue`/`SetValue` 経由のみでアクセス |

## Dependency Property 定義

```csharp
public static readonly DependencyProperty IsActiveProperty =
    DependencyProperty.Register(
        nameof(IsActive), typeof(bool), typeof(MyControl),
        new PropertyMetadata(false, OnIsActiveChanged));

public bool IsActive
{
    get => (bool)GetValue(IsActiveProperty);
    set => SetValue(IsActiveProperty, value);
}
```

## Dapper でデータアクセス

```csharp
public class UserRepository(IDbConnection db)
{
    public async Task<IEnumerable<User>> GetAllAsync() =>
        await db.QueryAsync<User>("SELECT * FROM Users");

    public async Task<int> InsertAsync(User user) =>
        await db.ExecuteAsync(
            "INSERT INTO Users (Name, Email) VALUES (@Name, @Email)", user);
}
```

**注意:** WPF アプリでは SQLite（Microsoft.Data.Sqlite）が軽量で一般的。接続文字列は `appsettings.json` + Generic Host で管理。

## .NET 10 固有の注意点

- **NativeAOT** は WPF 非対応（PresentationCore は Reflection 依存）
- **Trimming** 部分対応 — XAML の型解決に注意（`[DynamicallyAccessedMembers]`）
- **Hot Reload** は `dotnet watch` または Visual Studio の XAML Hot Reload が有効

## LSP / ツール

このスキルは **csharp-lsp**（OmniSharp / C# Dev Kit）と組み合わせて使う。  
定義ジャンプ・インレイヒント・リファクタリングは LSP 経由で実行する。

```bash
# ビルド
dotnet build

# 実行
dotnet run --project src/MyApp/MyApp.csproj

# 発行（自己完結）
dotnet publish -c Release -r win-x64 --self-contained
```

## Quick Reference

| 操作 | 方法 |
|------|------|
| プロパティ変更通知 | `[ObservableProperty]` (CommunityToolkit) |
| コマンド定義 | `[RelayCommand]` |
| 非同期コマンド | `[RelayCommand]` on `async Task` method |
| コレクション | `ObservableCollection<T>` |
| DI 登録 | `services.AddSingleton<T>` / `AddTransient<T>` |
| スレッドマーシャリング | `await Dispatcher.InvokeAsync(...)` |
| ナビゲーション (Prism) | `_regionManager.RequestNavigate(...)` |
