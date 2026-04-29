# WPF + .NET 10: ViewModel が DbContext を直接 new している問題の直し方

## 問題の整理

典型的なアンチパターンはこのようなコードです。

```csharp
// NG: Presentation 層が Infrastructure に直接依存している
public class ProjectViewModel : ObservableObject
{
    private ObservableCollection<ProjectDto> _projects = new();
    public ObservableCollection<ProjectDto> Projects
    {
        get => _projects;
        set => SetProperty(ref _projects, value);
    }

    public async Task LoadProjectsAsync()
    {
        // ViewModel が DbContext を直接生成 → 絶対にやってはいけない
        using var db = new AppDbContext();
        var list = await db.Projects
            .Select(p => new ProjectDto(p.Id, p.Name, p.Tasks.Count))
            .ToListAsync();
        Projects = new ObservableCollection<ProjectDto>(list);
    }
}
```

**何が問題か:**
- Presentation 層が EF Core (Infrastructure) に直接依存し、依存の方向が逆転している
- テストで DbContext をモックできない (単体テスト不可)
- ViewModel がデータアクセスの責務を持ち、単一責任の原則に違反する
- `using var db = new AppDbContext()` はライフサイクル管理が壊れており、接続リークや競合を生む

---

## 正しいレイヤー構成

Clean Architecture のレイヤーマップに従います。

```
Domain          (zero dependencies)
  └─ Application (depends on Domain only)
       └─ Infrastructure (depends on Application interfaces)
       └─ Presentation   (depends on Application + Domain)
```

各クラスをどのレイヤーに移動するかを以下で示します。

---

## Step 1: Domain 層 — エンティティとリポジトリ interface

```csharp
// Domain/Entities/Project.cs
public class Project
{
    public Guid Id { get; private set; }
    public string Name { get; private set; } = string.Empty;
    private readonly List<ProjectTask> _tasks = new();
    public IReadOnlyList<ProjectTask> Tasks => _tasks.AsReadOnly();

    // EF Core 用プロテクトコンストラクタ
    protected Project() { }

    public Project(Guid id, string name)
    {
        if (string.IsNullOrWhiteSpace(name))
            throw new DomainException("Project name is required.");
        Id = id;
        Name = name;
    }

    public void AddTask(string title)
    {
        if (string.IsNullOrWhiteSpace(title))
            throw new DomainException("Task title is required.");
        _tasks.Add(new ProjectTask(Guid.NewGuid(), title));
    }
}
```

```csharp
// Domain/Repositories/IProjectRepository.cs
// EF Core など Infrastructure の型は一切参照しない
public interface IProjectRepository
{
    Task<IReadOnlyList<Project>> GetAllAsync(CancellationToken ct = default);
    Task<Project?> GetByIdAsync(Guid id, CancellationToken ct = default);
    Task AddAsync(Project project, CancellationToken ct = default);
}
```

---

## Step 2: Application 層 — Query / Command / Handler / DTO

MediatR を使って CQRS スタイルで実装します。

```csharp
// Application/Projects/Queries/GetAllProjectsQuery.cs
public record GetAllProjectsQuery : IRequest<IReadOnlyList<ProjectDto>>;
```

```csharp
// Application/Projects/DTOs/ProjectDto.cs
public record ProjectDto(Guid Id, string Name, int TaskCount);
```

```csharp
// Application/Projects/Queries/GetAllProjectsHandler.cs
// Application 層は IProjectRepository (Domain) だけに依存する
// AppDbContext は参照しない
public class GetAllProjectsHandler(IProjectRepository repo)
    : IRequestHandler<GetAllProjectsQuery, IReadOnlyList<ProjectDto>>
{
    public async Task<IReadOnlyList<ProjectDto>> Handle(
        GetAllProjectsQuery request, CancellationToken ct)
    {
        var projects = await repo.GetAllAsync(ct);
        // Domain エンティティは Application の境界で DTO にマップして返す
        return projects
            .Select(p => new ProjectDto(p.Id, p.Name, p.Tasks.Count))
            .ToList();
    }
}
```

```csharp
// Application/Projects/Commands/CreateProjectCommand.cs
public record CreateProjectCommand(string Name) : IRequest<Guid>;

public class CreateProjectHandler(IProjectRepository repo)
    : IRequestHandler<CreateProjectCommand, Guid>
{
    public async Task<Guid> Handle(CreateProjectCommand request, CancellationToken ct)
    {
        var project = new Project(Guid.NewGuid(), request.Name);
        await repo.AddAsync(project, ct);
        return project.Id;
    }
}
```

---

## Step 3: Infrastructure 層 — DbContext とリポジトリ実装

```csharp
// Infrastructure/Persistence/AppDbContext.cs
public class AppDbContext(DbContextOptions<AppDbContext> options) : DbContext(options)
{
    public DbSet<Project> Projects => Set<Project>();

    protected override void OnModelCreating(ModelBuilder modelBuilder)
    {
        modelBuilder.Entity<Project>(b =>
        {
            b.HasKey(p => p.Id);
            b.Property(p => p.Name).HasMaxLength(200).IsRequired();
            // private フィールドのナビゲーションを EF に教える
            b.HasMany<ProjectTask>("_tasks")
             .WithOne()
             .OnDelete(DeleteBehavior.Cascade);
        });
    }
}
```

```csharp
// Infrastructure/Repositories/ProjectRepository.cs
// IProjectRepository (Domain) を実装する。EF Core はここだけに閉じ込める。
public class ProjectRepository(AppDbContext db) : IProjectRepository
{
    public async Task<IReadOnlyList<Project>> GetAllAsync(CancellationToken ct) =>
        await db.Projects.Include("_tasks").ToListAsync(ct);

    public async Task<Project?> GetByIdAsync(Guid id, CancellationToken ct) =>
        await db.Projects.Include("_tasks")
                         .FirstOrDefaultAsync(p => p.Id == id, ct);

    public async Task AddAsync(Project project, CancellationToken ct)
    {
        db.Projects.Add(project);
        await db.SaveChangesAsync(ct);
    }
}
```

---

## Step 4: Presentation 層 — ViewModel を IMediator だけに依存させる

```csharp
// Presentation/ViewModels/ProjectListViewModel.cs
// DbContext も IProjectRepository も参照しない — IMediator だけ
public partial class ProjectListViewModel(IMediator mediator) : ObservableObject
{
    [ObservableProperty]
    private ObservableCollection<ProjectDto> _projects = new();

    [ObservableProperty]
    private bool _isBusy;

    [RelayCommand]
    private async Task LoadAsync()
    {
        IsBusy = true;
        try
        {
            var result = await mediator.Send(new GetAllProjectsQuery());
            Projects = new ObservableCollection<ProjectDto>(result);
        }
        finally
        {
            IsBusy = false;
        }
    }

    [RelayCommand]
    private async Task CreateProjectAsync(string name)
    {
        if (string.IsNullOrWhiteSpace(name)) return;
        await mediator.Send(new CreateProjectCommand(name));
        await LoadAsync();   // 一覧を再取得
    }
}
```

---

## Step 5: DI の配線 (Generic Host)

```csharp
// App.xaml.cs
public partial class App : System.Windows.Application
{
    private IHost _host = null!;

    protected override async void OnStartup(StartupEventArgs e)
    {
        _host = Host.CreateDefaultBuilder()
            .ConfigureServices((ctx, services) =>
            {
                // --- Application ---
                // MediatR が Application アセンブリ内の Handler を自動登録
                services.AddMediatR(cfg =>
                    cfg.RegisterServicesFromAssembly(typeof(GetAllProjectsQuery).Assembly));

                // --- Infrastructure ---
                services.AddDbContext<AppDbContext>(o =>
                    o.UseSqlite(ctx.Configuration.GetConnectionString("Default")));
                services.AddScoped<IProjectRepository, ProjectRepository>();

                // --- Presentation ---
                services.AddTransient<ProjectListViewModel>();
                services.AddSingleton<MainWindow>();
            })
            .Build();

        await _host.StartAsync();

        var window = _host.Services.GetRequiredService<MainWindow>();
        window.Show();
    }

    protected override async void OnExit(ExitEventArgs e)
    {
        await _host.StopAsync();
        _host.Dispose();
        base.OnExit(e);
    }
}
```

---

## 移動先まとめ

| 元の場所 (NG) | 移動先 | クラス例 |
|---|---|---|
| ViewModel 内に `new AppDbContext()` | Infrastructure | `ProjectRepository` |
| ViewModel 内のクエリロジック | Application | `GetAllProjectsHandler` |
| ViewModel 内の DTO 生成 | Application | `ProjectDto` (マッピングも Handler 内) |
| ViewModel 内の `DbSet<>` 操作 | Infrastructure | `AppDbContext` |
| エンティティ定義 | Domain | `Project`, `ProjectTask` |
| リポジトリ interface | Domain | `IProjectRepository` |
| ViewModel 本体 | Presentation | `ProjectListViewModel` (IMediator のみ注入) |

---

## 依存方向の確認

```
Presentation  -->  Application (IMediator, Query/Command, DTO)
Application   -->  Domain      (IProjectRepository, Project entity)
Infrastructure --> Application (implements IProjectRepository)
Infrastructure --> Domain      (uses Project entity)

# 禁止されている方向
Presentation  -/-> Infrastructure  (DbContext, EF 型を直接参照してはいけない)
Application   -/-> Infrastructure  (EF Core の型を参照してはいけない)
Domain        -/-> any             (Domain は何にも依存しない)
```

この構成にすることで:
- ViewModel の単体テストで `IMediator` をモックするだけでよくなる
- EF Core を Dapper や別の ORM に差し替えても Application/Presentation に影響しない
- DbContext のライフサイクルは DI コンテナが管理するため、接続リークがなくなる
