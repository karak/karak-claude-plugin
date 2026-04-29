# WPF 在庫管理アプリ — Clean Architecture vs Vertical Slice Architecture

## 結論: Vertical Slice Architecture を推奨

### 判断根拠

スキルの選択基準に照らすと、今回のプロジェクトは Vertical Slice Architecture に該当するシグナルが揃っています。

| 判断シグナル | 今回のプロジェクト | 推奨パターン |
|---|---|---|
| リッチなドメインロジック・複数 Aggregate・DDD 概念 | なし | Clean Architecture |
| フィーチャー志向チーム・CRUD 中心・小〜中規模ドメイン | **該当** | **Vertical Slice** |
| 不明・プロトタイプ | 非該当 | Clean Architecture |

CRUD 中心・画面 10 枚程度という規模では、Clean Architecture の 4 層を律儀に維持しようとすると「1 つの機能を追うために 4 つのフォルダを行き来する」コストが発生します。Vertical Slice はその摩擦をゼロにし、機能単位で完結した追加・変更ができます。

---

## 推奨フォルダ構成（Vertical Slice）

```
InventoryApp/
├── App.xaml
├── App.xaml.cs                    ← Generic Host + DI wiring
│
├── Features/
│   ├── Items/                     ← 在庫品目
│   │   ├── List/
│   │   │   ├── ListItemsQuery.cs
│   │   │   ├── ListItemsHandler.cs
│   │   │   └── ItemListViewModel.cs
│   │   ├── Create/
│   │   │   ├── CreateItemCommand.cs
│   │   │   ├── CreateItemHandler.cs
│   │   │   └── CreateItemViewModel.cs
│   │   ├── Edit/
│   │   │   ├── EditItemCommand.cs
│   │   │   ├── EditItemHandler.cs
│   │   │   └── EditItemViewModel.cs
│   │   └── Delete/
│   │       ├── DeleteItemCommand.cs
│   │       ├── DeleteItemHandler.cs
│   │       └── DeleteItemViewModel.cs
│   │
│   ├── Stock/                     ← 在庫数・入出庫
│   │   ├── Receive/
│   │   ├── Ship/
│   │   └── History/
│   │
│   ├── Suppliers/                 ← 仕入先
│   │   ├── List/
│   │   ├── Create/
│   │   └── Edit/
│   │
│   └── Reports/                   ← 帳票・集計
│       ├── StockSummary/
│       └── LowStockAlert/
│
├── Shared/
│   ├── Entities/                  ← EF Core エンティティ（シンプルな POCO）
│   │   ├── Item.cs
│   │   ├── StockMovement.cs
│   │   └── Supplier.cs
│   ├── Persistence/
│   │   ├── AppDbContext.cs
│   │   └── Migrations/
│   ├── Exceptions/
│   │   └── NotFoundException.cs
│   └── Behaviors/                 ← MediatR パイプライン（ログ・バリデーション）
│       └── ValidationBehavior.cs
│
└── Presentation/
    ├── Views/                     ← XAML ウィンドウ・ページ
    │   ├── MainWindow.xaml
    │   ├── Items/
    │   │   ├── ItemListView.xaml
    │   │   └── ItemEditView.xaml
    │   └── ...
    └── Converters/                ← IValueConverter 共通部品
```

---

## 実装パターンの例（Items/List スライス）

```csharp
// Features/Items/List/ListItemsQuery.cs
public record ListItemsQuery(string? SearchText) : IRequest<IReadOnlyList<ItemDto>>;

public record ItemDto(Guid Id, string Name, int Stock, string Unit);

// Features/Items/List/ListItemsHandler.cs
public class ListItemsHandler(AppDbContext db) : IRequestHandler<ListItemsQuery, IReadOnlyList<ItemDto>>
{
    public async Task<IReadOnlyList<ItemDto>> Handle(ListItemsQuery req, CancellationToken ct)
    {
        var query = db.Items.AsQueryable();
        if (!string.IsNullOrWhiteSpace(req.SearchText))
            query = query.Where(i => i.Name.Contains(req.SearchText));

        return await query
            .Select(i => new ItemDto(i.Id, i.Name, i.Stock, i.Unit))
            .ToListAsync(ct);
    }
}

// Features/Items/List/ItemListViewModel.cs
public partial class ItemListViewModel(IMediator mediator) : ObservableObject
{
    [ObservableProperty] private ObservableCollection<ItemDto> _items = new();
    [ObservableProperty] private string _searchText = string.Empty;

    [RelayCommand]
    private async Task LoadAsync() =>
        Items = new ObservableCollection<ItemDto>(
            await mediator.Send(new ListItemsQuery(SearchText)));
}
```

---

## DI ワイヤリング（App.xaml.cs）

```csharp
_host = Host.CreateDefaultBuilder()
    .ConfigureServices((ctx, services) =>
    {
        // MediatR — Features アセンブリをスキャン
        services.AddMediatR(cfg =>
            cfg.RegisterServicesFromAssembly(typeof(App).Assembly));

        // EF Core（SQLite or SQL Server）
        services.AddDbContext<AppDbContext>(o =>
            o.UseSqlite(ctx.Configuration.GetConnectionString("Default")));

        // ViewModels（スライスごとに Transient 登録）
        services.AddTransient<ItemListViewModel>();
        services.AddTransient<CreateItemViewModel>();
        // ...

        // Windows
        services.AddSingleton<MainWindow>();
    })
    .Build();
```

---

## よくある間違いとその対策

| 間違い | 対策 |
|---|---|
| ViewModel が `AppDbContext` を直接 inject する | `IMediator` 経由でハンドラに委譲する |
| `Shared/Entities/` に EF ナビゲーションプロパティの setter を公開 | `private set` にして Fluent API で設定 |
| Features 間でハンドラを再利用しようとする | 軽い重複は許容。本当に共通なら `Shared/` に Query/Command を置く |
| Application 層が `Microsoft.EntityFrameworkCore` を参照 | VSA では Handler が直接 `AppDbContext` を使う設計でよい（層を増やさない） |

---

## Clean Architecture が適切になるタイミング

将来、以下のようになった場合は Clean Architecture への移行を検討してください。

- 在庫計算・引当ロジックなど、純粋なビジネスルールが増えてきた
- 複数の UI（WPF + Web API など）でドメインロジックを共有したい
- チームが拡大し、Infrastructure の詳細を隠蔽したい

スキルの注記通り「間違った選択をしても軽いリファクタで移行できる」ので、今は VSA でシンプルに始め、必要になった時点で Clean Architecture に移行するのが現実的な判断です。
