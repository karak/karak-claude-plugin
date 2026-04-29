# WPF ItemsControl 5000件スクロール パフォーマンス改善

## 原因：UI仮想化の欠如

`ItemsControl` をそのまま使うと、デフォルトでは **5000件すべての要素が一度にレンダリング** されます。画面外の要素も含めて Visual Tree が全構築されるため、スクロールが重くなります。

---

## 解決策1：ListBox / ListView + VirtualizingStackPanel に切り替える（最優先）

```xml
<!-- Before: 全件レンダリングされて重い -->
<StackPanel>
  <ItemsControl ItemsSource="{Binding Items}" />
</StackPanel>

<!-- After: 表示中のアイテムだけレンダリングされる -->
<ListBox ItemsSource="{Binding Items}"
         VirtualizingStackPanel.IsVirtualizing="True"
         VirtualizingStackPanel.VirtualizationMode="Recycling" />
```

**ポイント：**
- `VirtualizingStackPanel.IsVirtualizing="True"` で画面外の要素を破棄
- `VirtualizationMode="Recycling"` でコンテナを再利用（Standard より高速）
- `ListBox` や `ListView` はデフォルトで `VirtualizingStackPanel` を使うため、`ItemsControl` より適している

どうしても `ItemsControl` を使いたい場合は、`ItemsPanel` を明示的に指定します：

```xml
<ItemsControl ItemsSource="{Binding Items}"
              VirtualizingStackPanel.IsVirtualizing="True"
              VirtualizingStackPanel.VirtualizationMode="Recycling">
  <ItemsControl.ItemsPanel>
    <ItemsPanelTemplate>
      <VirtualizingStackPanel />
    </ItemsPanelTemplate>
  </ItemsControl.ItemsPanel>
</ItemsControl>
```

---

## 解決策2：DataTemplate に DataType を指定する

```xml
<!-- Bad: DataType なしは Visual Tree の毎回探索が発生する -->
<DataTemplate>
  ...
</DataTemplate>

<!-- Good: DataType を指定してルックアップを最適化 -->
<DataTemplate DataType="{x:Type vm:ItemViewModel}">
  ...
</DataTemplate>
```

---

## 解決策3：INotifyPropertyChanged の過剰発火を抑える

スクロール中に頻繁にプロパティ更新が走っている場合は、更新頻度を下げます。

```csharp
// Bad: 毎フレーム UI バインディングを更新してしまう
void OnTimer() => StatusText = DateTime.Now.ToString("HH:mm:ss.fff");

// Good: DispatcherTimer で表示更新を 1Hz に制限
_displayTimer = new DispatcherTimer { Interval = TimeSpan.FromSeconds(1) };
_displayTimer.Tick += (_, _) => StatusText = DateTime.Now.ToString("HH:mm:ss");
_displayTimer.Start();
```

---

## 解決策4：データ読み込みを非同期にする

UI スレッドをブロックするとスクロールが止まります。

```csharp
// Bad: 同期 I/O で UI スレッドをブロック
void LoadButton_Click(object s, RoutedEventArgs e) =>
    Items = _repo.GetAll().ToObservableCollection();

// Good: async/await で UI スレッドを解放
async void LoadButton_Click(object s, RoutedEventArgs e) =>
    Items = (await _repo.GetAllAsync()).ToObservableCollection();
```

---

## プロファイリングで根本原因を確認する

まず **Release ビルド** でプロファイルを取ります（Debug ビルドは余分なアロケーションがあり正確な計測ができません）。

```bash
# プロセス ID を確認
dotnet-counters monitor --process-id <pid> \
  --counters System.Runtime

# 30秒間トレースを収集して PerfView / VS で分析
dotnet-trace collect --process-id <pid> \
  --duration 00:00:30 \
  --output wpfapp.nettrace
```

Visual Studio では **Debug > Performance Profiler > XAML UI Responsiveness** で UI スレッドのボトルネックを可視化できます。

---

## まとめ：優先度順チェックリスト

| 優先度 | 対処 |
|--------|------|
| 1 | `ListBox` + `VirtualizingStackPanel.VirtualizationMode="Recycling"` に切り替え |
| 2 | `DataTemplate` に `DataType` を追加 |
| 3 | データ読み込みを `async/await` 化 |
| 4 | `INotifyPropertyChanged` の更新頻度を `DispatcherTimer` で制限 |
| 5 | Release ビルドで dotnet-trace / VS Diagnostic Tools によるプロファイリング |

ほとんどのケースでは **仮想化の有効化（解決策1）だけで劇的に改善** されます。
