---
name: dotnet-clean-architecture
description: Use when designing layer boundaries for a .NET 10 WPF application — deciding which layer owns a class, how to wire up dependency inversion, whether to use Clean Architecture vs Vertical Slice, or how to introduce MediatR/CQRS. Also use when an existing codebase needs layer refactoring (ViewModel directly referencing EF DbContext, services mixed into Presentation, etc.). Distinct from dotnet-wpf-expert which handles component-level wiring; this skill handles structural design decisions.
---

# .NET 10 WPF Clean Architecture

## Overview

Two main structural patterns for WPF desktop apps. Choose based on team size and domain complexity — both are valid, and the wrong choice just means a light refactor later.

**Core rule:** The Domain layer must never reference any other layer. Dependencies always point inward.

---

## Pattern Selection

| Signal | Choose |
|--------|--------|
| Rich domain logic, multiple aggregates, DDD concepts | Clean Architecture |
| Feature-oriented team, CRUD-heavy, small-medium domain | Vertical Slice |
| Unsure / prototype | Clean Architecture (easier to migrate from) |

---

## Clean Architecture — Layer Map

```
Domain          (zero dependencies)
  └─ Application (depends on Domain only)
       └─ Infrastructure (depends on Application interfaces)
       └─ Presentation   (depends on Application + Domain)
```

### Domain layer
Pure C# — entities, value objects, domain events, repository interfaces, no framework references.

```csharp
// Domain/Entities/Project.cs
public class Project
{
    public Guid Id { get; private set; }
    public string Name { get; private set; }
    private readonly List<Task> _tasks = new();
    public IReadOnlyList<Task> Tasks => _tasks.AsReadOnly();

    public void AddTask(string title)
    {
        if (string.IsNullOrWhiteSpace(title)) throw new DomainException("Title required");
        _tasks.Add(new Task(title));
    }
}
```

### Application layer
Use cases (Commands + Queries), DTOs, service interfaces. Use MediatR for CQRS lite.

```csharp
// Application/Projects/GetProjectQuery.cs
public record GetProjectQuery(Guid Id) : IRequest<ProjectDto>;

public class GetProjectHandler(IProjectRepository repo)
    : IRequestHandler<GetProjectQuery, ProjectDto>
{
    public async Task<ProjectDto> Handle(GetProjectQuery req, CancellationToken ct)
    {
        var project = await repo.GetByIdAsync(req.Id, ct)
            ?? throw new NotFoundException(nameof(Project), req.Id);
        return new ProjectDto(project.Id, project.Name, project.Tasks.Count);
    }
}
```

### Infrastructure layer
EF Core DbContext, Dapper repos, file system, external APIs — all behind Application interfaces.

```csharp
// Infrastructure/Repositories/ProjectRepository.cs
public class ProjectRepository(AppDbContext db) : IProjectRepository
{
    public async Task<Project?> GetByIdAsync(Guid id, CancellationToken ct) =>
        await db.Projects.Include(p => p.Tasks).FirstOrDefaultAsync(p => p.Id == id, ct);
}
```

### Presentation layer (WPF)
ViewModels belong here (or in Application for thin VMs). Never reference `DbContext` or EF types directly.

```csharp
// Presentation/ViewModels/ProjectViewModel.cs
public partial class ProjectViewModel(IMediator mediator) : ObservableObject
{
    [ObservableProperty] private ProjectDto? _project;

    [RelayCommand]
    private async Task LoadAsync(Guid id) =>
        Project = await mediator.Send(new GetProjectQuery(id));
}
```

---

## Vertical Slice Architecture

Organize by **feature** rather than layer. Each feature owns its Command/Query, Handler, ViewModel slice, and Infrastructure access.

```
Features/
  Projects/
    List/
      ListProjectsQuery.cs
      ListProjectsHandler.cs
      ProjectsViewModel.cs   ← this slice's ViewModel
    Create/
      CreateProjectCommand.cs
      CreateProjectHandler.cs
      CreateProjectViewModel.cs
  Tasks/
    Complete/
      ...
```

**When to pick Vertical Slice:** When you find yourself jumping through 4 folders to trace a single feature — VSA removes that friction at the cost of some cross-feature duplication.

---

## Dependency Injection Wiring (Generic Host)

```csharp
// App.xaml.cs
_host = Host.CreateDefaultBuilder()
    .ConfigureServices((ctx, services) =>
    {
        // MediatR — scans Application assembly
        services.AddMediatR(cfg =>
            cfg.RegisterServicesFromAssembly(typeof(GetProjectQuery).Assembly));

        // Infrastructure
        services.AddDbContext<AppDbContext>(o =>
            o.UseSqlite(ctx.Configuration.GetConnectionString("Default")));
        services.AddScoped<IProjectRepository, ProjectRepository>();

        // Presentation
        services.AddTransient<MainViewModel>();
        services.AddSingleton<MainWindow>();
    })
    .Build();
```

---

## Common Mistakes

| Mistake | Fix |
|---------|-----|
| ViewModel holds `DbContext` directly | Inject `IMediator` or a dedicated service interface |
| Domain entity references EF navigation properties with setters | Use `private set` + factory methods; configure EF via Fluent API |
| Application layer references `Microsoft.EntityFrameworkCore` | Move EF code to Infrastructure; Application only references interfaces |
| One giant `Services/` folder mixing domain + infra | Split by layer or by feature slice |
| Returning Domain entities from Application handlers | Map to DTOs at the Application boundary |

---

## Quick Reference

| Concept | Location |
|---------|----------|
| Entity / Value Object | Domain |
| Repository interface | Domain |
| Command / Query / DTO | Application |
| MediatR handler | Application |
| EF DbContext / Dapper | Infrastructure |
| Repository implementation | Infrastructure |
| ViewModel | Presentation (or Application for thin VMs) |
| XAML / code-behind | Presentation |
