# WPF 在庫管理アプリのアーキテクチャ選定：Clean Architecture vs Vertical Slice Architecture

## 結論：Vertical Slice Architecture を推奨

10画面程度・CRUD 中心・複雑なドメインロジックなし、という条件では **Vertical Slice Architecture（VSA）** が適切です。

---

## 比較

### Clean Architecture（CA）

| 観点 | 評価 |
|------|------|
| 適合するプロジェクト規模 | 大規模・長期・複雑なドメインロジックあり |
| WPF との相性 | MVVM と組み合わせると層が増えすぎる傾向 |
| 学習コスト | 高い（Domain / Application / Infrastructure / Presentation の 4 層） |
| CRUD 中心アプリへの適用 | オーバースペック。Mapper・Interface・UseCase クラスが大量発生する |
| 変更容易性 | 横断的変更（例：新フィールド追加）のたびに 4 層すべてを修正する必要がある |

CA を使うべき条件：チームが既に CA に習熟している、将来的にドメインロジックが複雑化することが確実、またはテスト戦略が高度に組織化されている場合。

### Vertical Slice Architecture（VSA）

| 観点 | 評価 |
|------|------|
| 適合するプロジェクト規模 | 小〜中規模・機能追加ペースが速い |
| WPF との相性 | ViewModel 単位 = 機能スライス単位と自然に対応する |
| 学習コスト | 低い（機能ディレクトリを切ってそこに完結させるだけ） |
| CRUD 中心アプリへの適用 | 最適。新機能追加時に既存コードをほぼ触らない |
| 変更容易性 | スライス内で完結するため影響範囲が明確 |

---

## 推奨フォルダ構成（VSA + MVVM）

```
InventoryApp/
├── InventoryApp.sln
│
├── InventoryApp/                        # WPF プロジェクト（唯一のプロジェクト）
│   ├── App.xaml
│   ├── App.xaml.cs
│   ├── appsettings.json
│   │
│   ├── Common/                          # 全スライス共通インフラ
│   │   ├── Data/
│   │   │   ├── AppDbContext.cs
│   │   │   └── DbContextFactory.cs
│   │   ├── Navigation/
│   │   │   ├── INavigationService.cs
│   │   │   └── NavigationService.cs
│   │   ├── Dialogs/
│   │   │   ├── IDialogService.cs
│   │   │   └── DialogService.cs
│   │   ├── Converters/                  # IValueConverter 実装
│   │   └── Extensions/
│   │       └── ServiceCollectionExtensions.cs
│   │
│   ├── Features/                        # 機能スライス群
│   │   │
│   │   ├── Products/                    # 商品マスタ管理
│   │   │   ├── ProductListView.xaml
│   │   │   ├── ProductListView.xaml.cs
│   │   │   ├── ProductListViewModel.cs
│   │   │   ├── ProductEditView.xaml
│   │   │   ├── ProductEditView.xaml.cs
│   │   │   ├── ProductEditViewModel.cs
│   │   │   ├── ProductRepository.cs     # IProductRepository + 実装を同居
│   │   │   └── ProductDto.cs
│   │   │
│   │   ├── Inventory/                   # 在庫一覧・調整
│   │   │   ├── InventoryListView.xaml
│   │   │   ├── InventoryListView.xaml.cs
│   │   │   ├── InventoryListViewModel.cs
│   │   │   ├── InventoryAdjustView.xaml
│   │   │   ├── InventoryAdjustView.xaml.cs
│   │   │   ├── InventoryAdjustViewModel.cs
│   │   │   ├── InventoryRepository.cs
│   │   │   └── InventoryDto.cs
│   │   │
│   │   ├── Warehouses/                  # 倉庫マスタ
│   │   │   ├── WarehouseListView.xaml
│   │   │   ├── WarehouseListView.xaml.cs
│   │   │   ├── WarehouseListViewModel.cs
│   │   │   ├── WarehouseEditView.xaml
│   │   │   ├── WarehouseEditView.xaml.cs
│   │   │   ├── WarehouseEditViewModel.cs
│   │   │   └── WarehouseRepository.cs
│   │   │
│   │   ├── StockMovements/              # 入出庫履歴
│   │   │   ├── StockMovementListView.xaml
│   │   │   ├── StockMovementListView.xaml.cs
│   │   │   ├── StockMovementListViewModel.cs
│   │   │   └── StockMovementRepository.cs
│   │   │
│   │   ├── Reports/                     # レポート・集計
│   │   │   ├── ReportDashboardView.xaml
│   │   │   ├── ReportDashboardView.xaml.cs
│   │   │   └── ReportDashboardViewModel.cs
│   │   │
│   │   └── Shell/                       # メインウィンドウ・ナビゲーション
│   │       ├── MainWindow.xaml
│   │       ├── MainWindow.xaml.cs
│   │       └── MainWindowViewModel.cs
│   │
│   └── Assets/                          # 画像・フォントリソース
│
└── InventoryApp.Tests/                  # 単体・統合テスト
    ├── Features/
    │   ├── Products/
    │   │   ├── ProductListViewModelTests.cs
    │   │   └── ProductRepositoryTests.cs
    │   └── Inventory/
    │       └── InventoryAdjustViewModelTests.cs
    └── Common/
        └── NavigationServiceTests.cs
```

---

## 設計の要点

### 1. スライス内自己完結の原則

各 `Features/XXX/` ディレクトリは、その機能に必要な View・ViewModel・Repository・DTO をすべて含みます。他スライスのクラスを直接 `new` するのではなく、`Common/` の共通サービスまたはDI経由でのみ参照します。

```csharp
// Features/Products/ProductListViewModel.cs
public sealed class ProductListViewModel : ObservableObject
{
    private readonly ProductRepository _repo;
    private readonly INavigationService _nav;

    // DI コンストラクタ
    public ProductListViewModel(ProductRepository repo, INavigationService nav)
    {
        _repo = repo;
        _nav = nav;
        LoadCommand = new AsyncRelayCommand(LoadAsync);
        EditCommand = new RelayCommand<ProductDto>(Edit);
    }

    public ObservableCollection<ProductDto> Products { get; } = new();
    public IAsyncRelayCommand LoadCommand { get; }
    public IRelayCommand<ProductDto> EditCommand { get; }

    private async Task LoadAsync()
    {
        var items = await _repo.GetAllAsync();
        Products.Clear();
        foreach (var item in items) Products.Add(item);
    }

    private void Edit(ProductDto? dto)
    {
        if (dto is null) return;
        _nav.NavigateTo<ProductEditViewModel>(dto.Id);
    }
}
```

### 2. Repository はスライス内でシンプルに

CA のように `IRepository<T>` 汎用インターフェースを作ると CRUD の薄いアプリでは過剰です。スライスごとに具体的な Repository クラスを置き、テスト時はその具体クラスをモック or InMemory DB で差し替えます。

```csharp
// Features/Products/ProductRepository.cs
public sealed class ProductRepository(AppDbContext db)
{
    public Task<List<ProductDto>> GetAllAsync() =>
        db.Products
          .AsNoTracking()
          .Select(p => new ProductDto(p.Id, p.Name, p.Sku, p.Stock))
          .ToListAsync();

    public Task<ProductDto?> FindByIdAsync(int id) =>
        db.Products
          .AsNoTracking()
          .Where(p => p.Id == id)
          .Select(p => new ProductDto(p.Id, p.Name, p.Sku, p.Stock))
          .FirstOrDefaultAsync();

    public async Task SaveAsync(ProductDto dto)
    {
        var entity = await db.Products.FindAsync(dto.Id)
                     ?? db.Products.Add(new Product()).Entity;
        entity.Name  = dto.Name;
        entity.Sku   = dto.Sku;
        entity.Stock = dto.Stock;
        await db.SaveChangesAsync();
    }

    public async Task DeleteAsync(int id)
    {
        var entity = await db.Products.FindAsync(id);
        if (entity is not null)
        {
            db.Products.Remove(entity);
            await db.SaveChangesAsync();
        }
    }
}
```

### 3. DI 登録は機能ごとに Extension メソッドに集約

```csharp
// Common/Extensions/ServiceCollectionExtensions.cs
public static class ServiceCollectionExtensions
{
    public static IServiceCollection AddInventoryApp(this IServiceCollection services, IConfiguration config)
    {
        // インフラ
        services.AddDbContext<AppDbContext>(o =>
            o.UseSqlite(config.GetConnectionString("Default")));

        // 共通サービス
        services.AddSingleton<INavigationService, NavigationService>();
        services.AddSingleton<IDialogService, DialogService>();

        // 機能スライス（ViewModel は Transient、Repository は Scoped 推奨）
        services.AddTransient<ProductListViewModel>();
        services.AddTransient<ProductEditViewModel>();
        services.AddScoped<ProductRepository>();

        services.AddTransient<InventoryListViewModel>();
        services.AddTransient<InventoryAdjustViewModel>();
        services.AddScoped<InventoryRepository>();

        // ... 以下同様

        return services;
    }
}
```

### 4. 技術スタック推奨

| 用途 | ライブラリ |
|------|-----------|
| MVVM 基盤 | CommunityToolkit.Mvvm 8.x |
| ORM | EF Core 10 + Microsoft.EntityFrameworkCore.Sqlite |
| DI | Microsoft.Extensions.DependencyInjection |
| ダイアログ | 自前の `IDialogService`（または Wpf-UI） |
| 単体テスト | xUnit + Moq + EF Core InMemory Provider |

---

## CA を選ぶべき例外ケース

以下に該当する場合は CA を検討してください：

- 将来 Web API（ASP.NET Core）と同じドメインロジックを共有する予定がある
- チームの全員が既に CA に習熟しており、層の分離によるコストを許容できる
- ビジネスルール（在庫引当ロジック、有効期限管理等）が複雑化することが明確に見込まれている

今回の「社内向け・10画面・CRUD 中心」という要件ではいずれも該当しないため、VSA を選ぶ合理的な根拠が揃っています。
