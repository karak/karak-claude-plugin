# WPF ItemsControl 5000件のスクロール最適化

## 根本原因

`ItemsControl` はデフォルトで **全アイテムのビジュアルを一度に生成・保持**します。5000件では5000個のUIオブジェクトがメモリ上に存在し、レイアウト計算・レンダリングのコストが爆発します。

---

## 解決策 1（最重要）: UI 仮想化を有効にする

### ListBox / ListView に切り替える（推奨）

`ListBox` と `ListView` は `VirtualizingStackPanel` をデフォルトで使うため、**画面内に見えているアイテムのみ**UI要素を生成します。

```xml
<ListBox ItemsSource="{Binding Items}"
         VirtualizingPanel.IsVirtualizing="True"
         VirtualizingPanel.VirtualizationMode="Recycling">
    <ListBox.ItemTemplate>
        <DataTemplate>
            <TextBlock Text="{Binding Name}" />
        </DataTemplate>
    </ListBox.ItemTemplate>
</ListBox>
```

### ItemsControl のまま使う場合

`ItemsPanel` を明示的に `VirtualizingStackPanel` に設定し、`ScrollViewer` でラップします。

```xml
<ScrollViewer>
    <ItemsControl ItemsSource="{Binding Items}"
                  VirtualizingPanel.IsVirtualizing="True"
                  VirtualizingPanel.VirtualizationMode="Recycling">
        <ItemsControl.ItemsPanel>
            <ItemsPanelTemplate>
                <VirtualizingStackPanel />
            </ItemsPanelTemplate>
        </ItemsControl.ItemsPanel>
        <ItemsControl.Template>
            <ControlTemplate TargetType="ItemsControl">
                <ScrollViewer CanContentScroll="True">
                    <ItemsPresenter />
                </ScrollViewer>
            </ControlTemplate>
        </ItemsControl.Template>
    </ItemsControl>
</ScrollViewer>
```

**重要:** `CanContentScroll="True"` が必須です。`False`（ピクセルスクロール）だと仮想化が無効になります。

---

## 解決策 2: VirtualizationMode を Recycling にする

デフォルトの `Standard` モードはスクロールのたびに古いコンテナを破棄して新しいものを作ります。`Recycling` にするとコンテナを再利用するため GC 圧力が下がりさらに高速になります。

```xml
VirtualizingPanel.VirtualizationMode="Recycling"
```

---

## 解決策 3: ScrollUnit を Item にする

ピクセル単位のスクロールでは仮想化が機能しません。

```xml
VirtualizingPanel.ScrollUnit="Item"
```

アイテムの高さが不均一な場合は後述の「異なる高さ」セクションを参照してください。

---

## 解決策 4: データバインディングの最適化

### INotifyPropertyChanged の最適化

変更のないプロパティで `PropertyChanged` を発火させないようにします。

```csharp
private string _name;
public string Name
{
    get => _name;
    set
    {
        if (_name == value) return; // 変更なければ通知しない
        _name = value;
        OnPropertyChanged(nameof(Name));
    }
}
```

### コレクションに ObservableCollection を使う

`List<T>` を直接バインドすると差分通知ができず全再描画になります。

```csharp
public ObservableCollection<ItemViewModel> Items { get; } = new();
```

---

## 解決策 5: アイテムテンプレートの軽量化

複雑なテンプレートは仮想化しても重くなります。

```xml
<!-- 重い例（避ける） -->
<DataTemplate>
    <Border>
        <Grid>
            <Grid.ColumnDefinitions>...</Grid.ColumnDefinitions>
            <StackPanel>
                <Image Source="{Binding LargeImage}" /> <!-- 重い -->
                ...
            </StackPanel>
        </Grid>
    </Border>
</DataTemplate>

<!-- 軽い例 -->
<DataTemplate>
    <StackPanel Orientation="Horizontal">
        <TextBlock Text="{Binding Id}" Width="60" />
        <TextBlock Text="{Binding Name}" />
    </StackPanel>
</DataTemplate>
```

画像がある場合は `DecodePixelWidth` / `DecodePixelHeight` でデコードサイズを制限します。

```xml
<Image>
    <Image.Source>
        <BitmapImage UriSource="{Binding ImagePath}"
                     DecodePixelWidth="48" />
    </Image.Source>
</Image>
```

---

## 解決策 6: アイテム高さが不均一な場合

`VirtualizingPanel.IsVirtualizingWhenGrouping="True"` と合わせて、`ScrollUnit="Pixel"` でも仮想化を効かせるには `.NET 4.5+` の機能を使います。

```xml
VirtualizingPanel.ScrollUnit="Pixel"
VirtualizingPanel.CacheLength="3"
VirtualizingPanel.CacheLengthUnit="Page"
```

`CacheLength` はスクロール方向の前後にキャッシュするページ数です。増やすと先読みが増えてスクロールが滑らかになりますが、メモリ使用量が増えます。

---

## 解決策 7: 非同期データ読み込み

5000件を同期でロードしているなら UI スレッドをブロックします。`async/await` + `Dispatcher` で非同期にします。

```csharp
public async Task LoadItemsAsync()
{
    var data = await Task.Run(() => FetchDataFromDatabase());
    foreach (var item in data)
    {
        Items.Add(item); // UI スレッドで追加
    }
}
```

大量追加の場合は `ObservableCollection` への `Add` をまとめて `AddRange` 相当にするか、一時的に通知を抑制します。

```csharp
// 大量追加時のパターン
var list = new List<ItemViewModel>(data.Select(d => new ItemViewModel(d)));
Items = new ObservableCollection<ItemViewModel>(list); // 一括置き換え
OnPropertyChanged(nameof(Items));
```

---

## チェックリスト（優先度順）

| 優先度 | 対策 | 効果 |
|--------|------|------|
| 高 | `VirtualizingStackPanel` + `CanContentScroll="True"` | 劇的改善 |
| 高 | `VirtualizationMode="Recycling"` | GC 圧力削減 |
| 中 | `ScrollUnit="Item"` | スクロール安定化 |
| 中 | アイテムテンプレートの軽量化 | レンダリング負荷削減 |
| 中 | `INotifyPropertyChanged` の無駄通知削減 | バインディング負荷削減 |
| 低 | `CacheLength` チューニング | スクロール滑らかさ調整 |
| 低 | 非同期読み込み | 初期表示の改善 |

---

## 最小限の修正例（既存 ItemsControl を維持する場合）

```xml
<ItemsControl ItemsSource="{Binding Items}"
              VirtualizingPanel.IsVirtualizing="True"
              VirtualizingPanel.VirtualizationMode="Recycling"
              VirtualizingPanel.ScrollUnit="Item">
    <ItemsControl.ItemsPanel>
        <ItemsPanelTemplate>
            <VirtualizingStackPanel />
        </ItemsPanelTemplate>
    </ItemsControl.ItemsPanel>
    <ItemsControl.Template>
        <ControlTemplate TargetType="ItemsControl">
            <ScrollViewer CanContentScroll="True"
                          HorizontalScrollBarVisibility="Auto"
                          VerticalScrollBarVisibility="Auto">
                <ItemsPresenter />
            </ScrollViewer>
        </ControlTemplate>
    </ItemsControl.Template>
    <ItemsControl.ItemTemplate>
        <DataTemplate>
            <!-- 軽量なテンプレートを記述 -->
            <TextBlock Text="{Binding Name}" />
        </DataTemplate>
    </ItemsControl.ItemTemplate>
</ItemsControl>
```

これだけで 5000件でも実用的なスクロール速度になるはずです。それでも重い場合はアイテムテンプレートの内容を見直してください。
