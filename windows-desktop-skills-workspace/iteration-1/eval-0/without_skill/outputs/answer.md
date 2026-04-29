# WPF + .NET 10: ViewModel から DbContext を切り離すリファクタリング

## 問題の構造

ViewModel が直接 EF Core の `DbContext` を `new` してクエリを実行すると、以下の問題が生じます。

- **テスト不可能**: DbContext を差し替えられないため Unit Test が書けない
- **責務の混在**: UI ロジック (ViewModel) とデータアクセス (DB) が同一クラスに存在する
- **DbContext の誤用**: WPF では UI スレッドと非同期処理が混在し、DbContext をまたいだ操作で競合が起きやすい
- **DI コンテナの恩恵ゼロ**: ライフタイム管理・モック注入・差し替えができない

---

## ターゲットとするレイヤー構成

```
┌──────────────────────────────────┐
│  View (.xaml / code-behind)      │  UI のみ。バインディングするだけ
├──────────────────────────────────┤
│  ViewModel                       │  ICommand, ObservableCollection
│                                  │  IProductRepository を DI で受け取る
├──────────────────────────────────┤
│  Repository / Service            │  IProductRepository + 実装クラス
│  (Application / Infrastructure)  │  EF Core はここでのみ触る
├──────────────────────────────────┤
│  DbContext (EF Core)             │  Infrastructure 層
│  DI コンテナでライフタイム管理    │
└──────────────────────────────────┘
```

---

## Before: 問題のある ViewModel

```csharp
// ❌ ProductListViewModel.cs (リファクタリング前)
public class ProductListViewModel : ObservableObject
{
    public ObservableCollection<Product> Products { get; } = new();

    public async Task LoadAsync()
    {
        // ViewModel が DbContext を直接 new している
        using var db = new AppDbContext();
        var items = await db.Products.ToListAsync();
        Products.Clear();
        foreach (var item in items)
            Products.Add(item);
    }
}
```

---

## After: 3 ステップで直す

### ステップ 1 — Repository インターフェースを定義する

**場所:** `src/Application/Interfaces/IProductRepository.cs`

```csharp
// Application 層 (純粋なインターフェース。EF Core への依存なし)
public interface IProductRepository
{
    Task<IReadOnlyList<Product>> GetAllAsync(CancellationToken ct = default);
    Task<Product?> GetByIdAsync(int id, CancellationToken ct = default);
    Task AddAsync(Product product, CancellationToken ct = default);
    Task DeleteAsync(int id, CancellationToken ct = default);
}
```

---

### ステップ 2 — Repository の実装を Infrastructure 層に置く

**場所:** `src/Infrastructure/Repositories/EfProductRepository.cs`

```csharp
// Infrastructure 層。EF Core はここにだけ登場する
public sealed class EfProductRepository : IProductRepository
{
    private readonly AppDbContext _db;

    // DbContext は DI コンテナから注入される (new しない)
    public EfProductRepository(AppDbContext db)
    {
        _db = db;
    }

    public async Task<IReadOnlyList<Product>> GetAllAsync(CancellationToken ct = default)
        => await _db.Products.AsNoTracking().ToListAsync(ct);

    public async Task<Product?> GetByIdAsync(int id, CancellationToken ct = default)
        => await _db.Products.FindAsync(new object[] { id }, ct);

    public async Task AddAsync(Product product, CancellationToken ct = default)
    {
        _db.Products.Add(product);
        await _db.SaveChangesAsync(ct);
    }

    public async Task DeleteAsync(int id, CancellationToken ct = default)
    {
        var entity = await _db.Products.FindAsync(new object[] { id }, ct);
        if (entity is not null)
        {
            _db.Products.Remove(entity);
            await _db.SaveChangesAsync(ct);
        }
    }
}
```

---

### ステップ 3 — ViewModel はインターフェースだけに依存する

**場所:** `src/Presentation/ViewModels/ProductListViewModel.cs`

```csharp
// ✅ ViewModel は IProductRepository にのみ依存する
public partial class ProductListViewModel : ObservableObject
{
    private readonly IProductRepository _repository;

    // コンストラクタインジェクション
    public ProductListViewModel(IProductRepository repository)
    {
        _repository = repository;
    }

    [ObservableProperty]
    private ObservableCollection<Product> _products = new();

    [ObservableProperty]
    private bool _isLoading;

    [RelayCommand]
    private async Task LoadAsync(CancellationToken ct = default)
    {
        IsLoading = true;
        try
        {
            var items = await _repository.GetAllAsync(ct);
            Products = new ObservableCollection<Product>(items);
        }
        finally
        {
            IsLoading = false;
        }
    }

    [RelayCommand]
    private async Task DeleteAsync(Product product)
    {
        await _repository.DeleteAsync(product.Id);
        Products.Remove(product);
    }
}
```

> `[ObservableProperty]` / `[RelayCommand]` は CommunityToolkit.Mvvm のソースジェネレーターを使っています。不使用の場合は手書きの `INotifyPropertyChanged` + `ICommand` に置き換えてください。

---

## DI コンテナへの登録 (App.xaml.cs)

.NET 10 の WPF では `Microsoft.Extensions.DependencyInjection` + `Microsoft.Extensions.Hosting` を使うのが標準的です。

```csharp
// App.xaml.cs
public partial class App : Application
{
    private readonly IHost _host;

    public App()
    {
        _host = Host.CreateDefaultBuilder()
            .ConfigureServices((ctx, services) =>
            {
                // DbContext: Scoped が基本
                // WPF では "1 操作 = 1 スコープ" の方針にする
                services.AddDbContext<AppDbContext>(options =>
                    options.UseSqlite(ctx.Configuration.GetConnectionString("Default")));

                // Repository を Scoped で登録
                services.AddScoped<IProductRepository, EfProductRepository>();

                // ViewModel も Scoped (または Transient) で登録
                services.AddScoped<ProductListViewModel>();

                // MainWindow は Transient
                services.AddTransient<MainWindow>();
            })
            .Build();
    }

    protected override async void OnStartup(StartupEventArgs e)
    {
        await _host.StartAsync();

        var mainWindow = _host.Services.GetRequiredService<MainWindow>();
        mainWindow.Show();

        base.OnStartup(e);
    }

    protected override async void OnExit(ExitEventArgs e)
    {
        await _host.StopAsync();
        _host.Dispose();
        base.OnExit(e);
    }
}
```

**MainWindow のコードビハインドでは `DataContext` を DI から受け取る:**

```csharp
// MainWindow.xaml.cs
public partial class MainWindow : Window
{
    public MainWindow(ProductListViewModel viewModel)
    {
        InitializeComponent();
        DataContext = viewModel;
    }
}
```

---

## DbContext のスコープ戦略 (WPF 固有の注意点)

Web と違い WPF には「リクエスト単位のスコープ」がないため、以下の方針から選択します。

| 方針 | 向いている場面 |
|---|---|
| **Transient DbContext** (操作ごとに新規作成) | 操作が短命・変更検知不要 |
| **IDbContextFactory を使う** (推奨) | 非同期操作が多い・並列読み込みがある |
| **Scoped + 手動スコープ** | ウィザードや編集フォームなど"編集セッション"が明確な場合 |

### IDbContextFactory を使う実装例

```csharp
// DI 登録
services.AddDbContextFactory<AppDbContext>(options =>
    options.UseSqlite(connectionString));

// Repository 側
public sealed class EfProductRepository : IProductRepository
{
    private readonly IDbContextFactory<AppDbContext> _factory;

    public EfProductRepository(IDbContextFactory<AppDbContext> factory)
    {
        _factory = factory;
    }

    public async Task<IReadOnlyList<Product>> GetAllAsync(CancellationToken ct = default)
    {
        // 操作ごとに短命なコンテキストを作成・破棄
        await using var db = await _factory.CreateDbContextAsync(ct);
        return await db.Products.AsNoTracking().ToListAsync(ct);
    }
}
```

---

## Unit Test が書けるようになる

リファクタリング後は `IProductRepository` をモックするだけでテストが可能です。

```csharp
// xUnit + NSubstitute の例
public class ProductListViewModelTests
{
    [Fact]
    public async Task LoadAsync_PopulatesProducts()
    {
        // Arrange
        var repo = Substitute.For<IProductRepository>();
        repo.GetAllAsync(default).ReturnsForAnyArgs(
            new List<Product>
            {
                new() { Id = 1, Name = "Widget A" },
                new() { Id = 2, Name = "Widget B" },
            });

        var vm = new ProductListViewModel(repo);

        // Act
        await vm.LoadCommand.ExecuteAsync(null);

        // Assert
        Assert.Equal(2, vm.Products.Count);
        Assert.Equal("Widget A", vm.Products[0].Name);
    }
}
```

---

## まとめ: 何をどこに移動するか

| 移動前 (ViewModel 内) | 移動後 | レイヤー |
|---|---|---|
| `new AppDbContext()` | DI コンテナへ登録 | Infrastructure / DI |
| `db.Products.ToListAsync()` | `EfProductRepository.GetAllAsync()` | Infrastructure |
| `db.Products.Add(...)` / `SaveChangesAsync()` | `EfProductRepository.AddAsync()` | Infrastructure |
| `using var db = ...` のライフタイム管理 | `IDbContextFactory` または DI スコープ | Infrastructure / DI |
| DB に依存した `LoadAsync` ロジック | ViewModel は `IProductRepository` を呼ぶだけ | Application / Presentation |

**鉄則: ViewModel は `IProductRepository` (インターフェース) にのみ依存し、EF Core / DbContext の型名は一切登場させない。**
