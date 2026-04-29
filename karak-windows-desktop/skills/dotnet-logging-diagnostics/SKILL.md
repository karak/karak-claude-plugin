---
name: dotnet-logging-diagnostics
description: Use when setting up structured logging in a .NET 10 WPF application with Serilog, configuring sinks (File, EventLog, Seq), enrichers, or log rotation. Also use when diagnosing crashes via global exception handlers, writing custom ETW EventSource traces, or troubleshooting why logs aren't appearing. For CPU/memory profiling, use dotnet-performance instead.
---

# .NET 10 WPF — Logging & Diagnostics

## Overview

Serilog is the primary logging stack. ETW + Windows Event Log handle OS-level diagnostics and enterprise monitoring scenarios.

**Core rule:** Structured logging means message templates, not string interpolation. `Log.Information("User {UserId} logged in", id)` — not `"User " + id + " logged in"`.

---

## Serilog Setup (Generic Host)

```xml
<!-- MyApp.csproj -->
<PackageReference Include="Serilog.Extensions.Hosting" Version="8.*" />
<PackageReference Include="Serilog.Settings.Configuration" Version="8.*" />
<PackageReference Include="Serilog.Sinks.File" Version="5.*" />
<PackageReference Include="Serilog.Sinks.EventLog" Version="3.*" />
<PackageReference Include="Serilog.Enrichers.Thread" Version="3.*" />
<PackageReference Include="Serilog.Enrichers.Environment" Version="2.*" />
```

```csharp
// App.xaml.cs — bootstrap before Host
Log.Logger = new LoggerConfiguration()
    .ReadFrom.Configuration(configuration)
    .Enrich.FromLogContext()
    .Enrich.WithThreadId()
    .Enrich.WithMachineName()
    .CreateBootstrapLogger();

_host = Host.CreateDefaultBuilder()
    .UseSerilog((ctx, services, cfg) => cfg
        .ReadFrom.Configuration(ctx.Configuration)
        .ReadFrom.Services(services)
        .Enrich.FromLogContext())
    .ConfigureServices(services => { /* ... */ })
    .Build();
```

---

## appsettings.json Configuration

```json
{
  "Serilog": {
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
          "path": "%LOCALAPPDATA%/MyApp/logs/app-.log",
          "rollingInterval": "Day",
          "retainedFileCountLimit": 30,
          "outputTemplate": "{Timestamp:yyyy-MM-dd HH:mm:ss.fff zzz} [{Level:u3}] {Message:lj}{NewLine}{Exception}"
        }
      },
      {
        "Name": "EventLog",
        "Args": {
          "source": "MyApp",
          "logName": "Application",
          "restrictedToMinimumLevel": "Warning"
        }
      }
    ]
  }
}
```

**Log rotation:** `rollingInterval: Day` + `retainedFileCountLimit: 30` keeps 30 days of logs and auto-deletes older files. For size-based rotation, use `fileSizeLimitBytes` + `rollOnFileSizeLimit: true`.

---

## Log Level Strategy

| Level | Use for |
|-------|---------|
| `Verbose` | Hot-path tracing (disabled in production) — MEL equivalent: `Trace` |
| `Debug` | State snapshots useful during dev |
| `Information` | Business events (user logged in, order placed) |
| `Warning` | Recoverable issues (retry attempt, fallback used) |
| `Error` | Exceptions, failed operations — need attention |
| `Fatal` | App cannot continue — forces shutdown |

---

## Structured Logging Patterns

```csharp
// Good — named properties become searchable in Seq/ELK
_logger.LogInformation("Project {ProjectId} loaded in {ElapsedMs}ms", id, sw.ElapsedMilliseconds);

// Bad — concatenation loses structure
_logger.LogInformation("Project " + id + " loaded");

// Destructure complex objects with @
_logger.LogDebug("Saving {@Project}", project);

// Conditional trace (avoids allocation cost when trace is disabled)
if (_logger.IsEnabled(LogLevel.Trace))
    _logger.LogTrace("Raw payload: {Payload}", JsonSerializer.Serialize(data));
```

---

## Global Exception Handling

```csharp
// App.xaml.cs — catch everything before the process dies
public partial class App : Application
{
    protected override void OnStartup(StartupEventArgs e)
    {
        DispatcherUnhandledException += (_, args) =>
        {
            Log.Fatal(args.Exception, "Unhandled UI thread exception");
            Log.CloseAndFlush();
            args.Handled = false; // let Windows show crash dialog
        };

        TaskScheduler.UnobservedTaskException += (_, args) =>
        {
            // .NET Core+ does NOT terminate the process on unobserved Task exceptions by default.
            // Log at Fatal to keep visibility; fix the root cause (unobserved Task in calling code).
            Log.Fatal(args.Exception, "Unobserved Task exception — fix calling code to observe this Task");
            args.SetObserved();
        };

        AppDomain.CurrentDomain.UnhandledException += (_, args) =>
        {
            var ex = args.ExceptionObject as Exception;
            if (ex is not null)
                Log.Fatal(ex, "AppDomain unhandled exception");
            else
                Log.Fatal("AppDomain unhandled exception (non-Exception): {ExceptionObject}", args.ExceptionObject);
            Log.CloseAndFlush();
        };

        base.OnStartup(e);
    }
}
```

**Why `CloseAndFlush` before shutdown:** Async Serilog sinks (File with buffering) may not flush on process exit without this call. Loss of the last log entries is a common post-crash debugging failure.

---

## ETW / Custom EventSource

Use for high-frequency, low-overhead tracing (game loops, parsing hot paths). Collected via `dotnet-trace` with `--providers` flag.

```csharp
[EventSource(Name = "MyApp-Diagnostics")]
public sealed class AppEventSource : EventSource
{
    public static readonly AppEventSource Log = new();

    [Event(1, Level = EventLevel.Informational)]
    public void ProjectLoaded(string projectId, long elapsedMs) =>
        WriteEvent(1, projectId, elapsedMs);

    [Event(2, Level = EventLevel.Warning)]
    public void SlowQuery(string sql, long elapsedMs) =>
        WriteEvent(2, sql, elapsedMs);
}

// Usage — zero allocation when no listener is attached
AppEventSource.Log.ProjectLoaded(project.Id.ToString(), sw.ElapsedMilliseconds);
```

```bash
# Collect custom EventSource traces (log events only — CPU/mem profiling → dotnet-performance)
dotnet-trace collect --process-id <pid> \
  --providers "MyApp-Diagnostics:0xFFFFFFFF:5"
```

---

## Windows Event Log — Source Registration

The Event Log source must be registered before first write (requires elevation, typically done at install time):

```powershell
# Run once during install (elevated)
New-EventLog -LogName Application -Source "MyApp"
```

```csharp
// Check at startup and warn if missing
if (!EventLog.SourceExists("MyApp"))
    _logger.LogWarning("EventLog source 'MyApp' not registered. Run installer as admin.");
```

---

## Common Mistakes

| Mistake | Fix |
|---------|-----|
| No logs on crash | Add `Log.CloseAndFlush()` in all unhandled exception handlers |
| PII in logs | Destructure only safe fields; use `[LogMasked]` attribute or custom destructuring policies |
| Async sink not flushing | Always call `Log.CloseAndFlush()` before process exit |
| Log file locked | Use `shared: true` in File sink args for multi-process scenarios |
| EventLog source registration fails silently | Check `EventLog.SourceExists` at startup; log a warning if missing |
| `Information` level floods log in production | Set `Override` in config to `Warning` for `Microsoft.*` and `System.*` namespaces |

---

## Quick Reference

| Task | How |
|------|-----|
| Add Serilog to Generic Host | `UseSerilog(...)` in Host builder |
| Configure via `appsettings.json` | `ReadFrom.Configuration(ctx.Configuration)` |
| Capture crash | `DispatcherUnhandledException` + `Log.Fatal` + `CloseAndFlush` |
| Rotate logs daily | `rollingInterval: "Day"` in File sink |
| Write to Windows Event Log | `Serilog.Sinks.EventLog` sink, Warning+ |
| High-frequency tracing | Custom `EventSource` + `dotnet-trace --providers` |
