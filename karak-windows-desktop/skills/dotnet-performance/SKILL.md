---
name: dotnet-performance
description: Use when a .NET 10 WPF application is slow, uses too much memory, or has a sluggish UI — profiling with dotnet-trace, dotnet-counters, PerfView, or Visual Studio Diagnostic Tools, diagnosing GC pressure, fixing UI thread blocking, or resolving unvirtualized large list rendering. Custom EventSource log tracing belongs to dotnet-logging-diagnostics.
---

# .NET 10 WPF — Performance Profiling

## Overview

Measure before optimizing. Most WPF performance issues fall into three buckets: UI thread blocking, GC pressure, and over-rendering. Tools tell you which one you have.

**Core rule:** Always profile a Release build. Debug builds have JIT suppressions and extra allocations that give false signals.

---

## Tool Selection

| Symptom | First tool to reach for |
|---------|------------------------|
| App feels sluggish / UI freezes | Visual Studio Diagnostic Tools (CPU + UI thread) |
| Memory grows over time | VS Memory Snapshot or dotnet-trace GC events |
| Need a flamegraph / deep callstack | PerfView |
| Production machine, no VS | `dotnet-trace` + `dotnet-counters` |
| Micro-benchmark a specific method | BenchmarkDotNet |

---

## dotnet-trace & dotnet-counters

```bash
# Install (once)
dotnet tool install --global dotnet-trace
dotnet tool install --global dotnet-counters

# Live counters — CPU, GC, threadpool, exception rate
dotnet-counters monitor --process-id <pid> \
  --counters System.Runtime,Microsoft.AspNetCore.Hosting

# Collect a CPU + GC trace (30s)
dotnet-trace collect --process-id <pid> \
  --duration 00:00:30 \
  --output myapp.nettrace

# Open myapp.nettrace in PerfView or VS
```

**Note:** `dotnet-trace` with `--providers MyApp-Diagnostics` collects custom EventSource events (log tracing). CPU/memory profiling uses the default `--profile cpu-sampling` — that's this skill's scope.

---

## PerfView Basics

PerfView is the deepest .NET profiler — free, no install.

1. **Collect:** Run > Collect (or `PerfView /GCCollectOnly collect` for GC-only)
2. **CPU flamegraph:** Open `.etl.zip` > CPU Stacks > Your process > Flame Graph
3. **GC view:** GC Stats — see Gen0/1/2 collection frequency, pause times, LOH size
4. **Memory:** Heap Snapshot > Diff two snapshots to find leak sources

**Key view: CPU Stacks**
- Sort by `Inc %` (inclusive %) — highest is where time is spent
- Filter by process name; exclude framework frames with `^System` in the filter box

---

## Visual Studio Diagnostic Tools

For development profiling (Debug menu > Performance Profiler):

- **CPU Usage** — sampling profiler, shows hot functions with call tree
- **Memory Usage** — take snapshots, diff them; find types accumulating across snapshots
- **XAML UI Responsiveness** — WPF-specific; shows UI thread vs render thread timeline

**Workflow:**
1. Start app in Release mode attached to VS
2. Reproduce the slow scenario
3. Stop collection, analyze

---

## WPF-Specific Performance Traps

### 1. Unvirtualized large lists
```xml
<!-- Bad: renders all 10,000 items immediately -->
<StackPanel>
  <ItemsControl ItemsSource="{Binding Items}" />
</StackPanel>

<!-- Good: VirtualizingStackPanel only renders visible items -->
<ListBox ItemsSource="{Binding Items}"
         VirtualizingStackPanel.IsVirtualizing="True"
         VirtualizingStackPanel.VirtualizationMode="Recycling" />
```

### 2. Frequent INotifyPropertyChanged on hot path
```csharp
// Bad: fires binding update on every frame
void OnTimer() => StatusText = DateTime.Now.ToString("HH:mm:ss.fff");

// Good: throttle with DispatcherTimer at 1Hz for display
_displayTimer = new DispatcherTimer { Interval = TimeSpan.FromSeconds(1) };
```

### 3. DataTemplate without x:Key causes repeated lookups
```xml
<!-- Add DataType to avoid visual tree traversal on every item -->
<DataTemplate DataType="{x:Type vm:ProjectViewModel}">
  ...
</DataTemplate>
```

### 4. UI thread blocking
```csharp
// Bad: blocks UI for synchronous I/O
void LoadButton_Click(object s, RoutedEventArgs e) =>
    Items = _repo.GetAll().ToObservableCollection(); // sync!

// Good: async + await returns to UI thread
async void LoadButton_Click(object s, RoutedEventArgs e) =>
    Items = (await _repo.GetAllAsync()).ToObservableCollection();
```

---

## GC Pressure

```csharp
// Bad: allocates new string every frame in hot loop
for (int i = 0; i < 100_000; i++)
    Process(new DataPoint { Label = $"Item {i}" });

// Good: reuse from pool for large, short-lived arrays
var buffer = ArrayPool<byte>.Shared.Rent(4096);
try { /* use buffer */ }
finally { ArrayPool<byte>.Shared.Return(buffer); }
```

**LOH (Large Object Heap):** Objects ≥ 85KB go to LOH and are collected infrequently. Watch for `byte[]` or `string` allocations above this threshold in loops.

---

## BenchmarkDotNet (Micro-benchmarking)

```csharp
[MemoryDiagnoser]
public class SerializationBenchmarks
{
    private readonly Project _project = new(Guid.NewGuid(), "Test");

    [Benchmark(Baseline = true)]
    public string JsonSerialize() => JsonSerializer.Serialize(_project);

    [Benchmark]
    public string NewtonsoftSerialize() => JsonConvert.SerializeObject(_project);
}

// Run: dotnet run -c Release
```

---

## Common Mistakes

| Mistake | Fix |
|---------|-----|
| Profiling in Debug mode | Always use Release build for profiling |
| Blocking UI thread with `.Result` | Use `async/await`; never `.Result` or `.Wait()` on Tasks in ViewModel |
| No virtualization on large `ItemsControl` | Switch to `ListBox`/`ListView` with `VirtualizingStackPanel` |
| LOH pressure from large buffers | Use `ArrayPool<T>` or `MemoryPool<T>` |
| Over-triggering `INotifyPropertyChanged` | Throttle display updates; batch property changes |
