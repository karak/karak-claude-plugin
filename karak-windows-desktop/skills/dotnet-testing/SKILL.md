---
name: dotnet-testing
description: Use when writing unit or integration tests for .NET 10 WPF/XAML applications using xUnit, Moq, and FluentAssertions. Covers ViewModel testing, service mocking, async tests, and common test patterns for desktop apps.
---

# .NET 10 テスト（xUnit + Moq）

## Overview

xUnit はコンストラクタ注入ベースのテストフレームワーク（テストごとに新インスタンス生成）。Moq でインターフェースをモックし、ViewModel と Service 層を分離してテストする。

**Core principle:** ViewModel は UI を知らないから、純粋な C# クラスとしてテスト可能。

## プロジェクト構成

```
MyApp.Tests/
  ViewModels/
  Services/
  Fixtures/
  MyApp.Tests.csproj
```

```xml
<!-- MyApp.Tests.csproj -->
<!-- xUnit v2 (stable, .NET 10 対応)。v3 に移行する場合は xunit.v3 + xunit.v3.runner.visualstudio パッケージに差し替える。
     v3 の主要な破壊的変更:
       1. `async void` テストは廃止 — 必ず `Task` / `ValueTask` を返す (analyzer xUnit1048)。
       2. 旧 `Xunit.Sdk` 配下の型 (`DataAttribute`, runner 系, `MaxConcurrencySyncContext` 等) は `Xunit.v3` 名前空間へ移動。 -->
<PackageReference Include="xunit" Version="2.*" />
<PackageReference Include="xunit.runner.visualstudio" Version="2.*" />
<PackageReference Include="Moq" Version="4.*" />
<!-- FluentAssertions v7+ は商用利用に有料ライセンスが必要。OSS/個人は v6 系を使用 -->
<PackageReference Include="FluentAssertions" Version="6.*" />
<PackageReference Include="Microsoft.NET.Test.Sdk" Version="17.*" />
```

## xUnit 基本パターン

```csharp
public class UserViewModelTests
{
    private readonly Mock<IUserService> _mockService = new();
    private readonly UserViewModel _sut;

    public UserViewModelTests()
    {
        _sut = new UserViewModel(_mockService.Object);
    }

    [Fact]
    public async Task LoadAsync_SetsUsers_WhenServiceReturnsData()
    {
        // Arrange
        var users = new[] { new User { Id = 1, Name = "Alice" } };
        _mockService.Setup(s => s.GetAllAsync()).ReturnsAsync(users);

        // Act
        await _sut.LoadCommand.ExecuteAsync(null);

        // Assert
        _sut.Users.Should().HaveCount(1);
        _sut.Users[0].Name.Should().Be("Alice");
    }

    [Theory]
    [InlineData("", false)]
    [InlineData("Alice", true)]
    public void SaveCommand_CanExecute_DependsOnName(string name, bool expected)
    {
        _sut.Name = name;
        _sut.SaveCommand.CanExecute(null).Should().Be(expected);
    }
}
```

## Moq パターン集

```csharp
// 戻り値設定
_mock.Setup(s => s.GetAsync(42)).ReturnsAsync(new User());

// 例外スロー
_mock.Setup(s => s.DeleteAsync(It.IsAny<int>()))
     .ThrowsAsync(new NotFoundException());

// 呼び出し検証
_mock.Verify(s => s.SaveAsync(It.Is<User>(u => u.Name == "Alice")), Times.Once);

// プロパティモック
_mock.SetupProperty(s => s.IsConnected, true);

// コールバック
_mock.Setup(s => s.SaveAsync(It.IsAny<User>()))
     .Callback<User>(u => capturedUser = u)
     .ReturnsAsync(true);
```

## 非同期テスト

```csharp
[Fact]
public async Task SaveAsync_ThrowsOnDuplicate_ShowsError()
{
    _mockService.Setup(s => s.SaveAsync(It.IsAny<User>()))
                .ThrowsAsync(new DuplicateKeyException());

    await _sut.SaveCommand.ExecuteAsync(null);

    _sut.ErrorMessage.Should().Contain("既に存在します");
}
```

**注意:** `async Task` を返すテストは xUnit が自動的に await する。`async void` は避ける。

## ObservableProperty の変更検知テスト

```csharp
[Fact]
public void Name_Changed_RaisesPropertyChanged()
{
    var raised = new List<string?>();
    _sut.PropertyChanged += (_, e) => raised.Add(e.PropertyName);

    _sut.Name = "Bob";

    raised.Should().Contain(nameof(_sut.Name));
}
```

## よくある落とし穴

| 落とし穴 | 原因 | 対策 |
|---------|------|------|
| `SynchronizationContext` エラー | WPF Dispatcher を単体テストで呼ぶ | Service 層で UI 操作を行わず、ViewModel は `async/await` で UI スレッドに戻す設計にする |
| Moq の `Setup` が効かない | `virtual` でないメソッドをモック | インターフェース経由でモックするか、メソッドを `virtual` にする |
| コレクション変更が届かない | テストで `ObservableCollection` の内容を直接参照 | `CollectionChanged` イベントを Subscribe してテスト |
| 非同期テストが常に Pass | `async void` を使っている | `async Task` に変更 |
| `RelayCommand` が null | CommunityToolkit のソースジェネレータが未実行 | `dotnet build` を一度実行してソースジェネレータを走らせる |

## テスト実行

```bash
# 全テスト実行
dotnet test

# フィルタ
dotnet test --filter "FullyQualifiedName~UserViewModel"

# カバレッジ（coverlet）
dotnet test --collect:"XPlat Code Coverage"
```

## Quick Reference

| 要素 | xUnit |
|------|-------|
| 単一テスト | `[Fact]` |
| パラメータ化 | `[Theory]` + `[InlineData]` |
| 共有フィクスチャ | `IClassFixture<T>` |
| セットアップ | コンストラクタ |
| クリーンアップ | `IDisposable.Dispose` |
| 非同期 | `async Task` (void 禁止) |
