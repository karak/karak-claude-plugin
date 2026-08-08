# SwiftUI Component Recipes (iOS 26+)

Concrete patterns for standard components. Prefer these over custom builds — standard
components inherit Liquid Glass, scroll edge effects, concentric corners, adaptive
appearance, and accessibility for free.

## Buttons

### Styles

```swift
// Liquid Glass styles — the iOS 26 defaults for floating/chrome buttons
Button("Continue") { }.buttonStyle(.glass)
Button("Done") { }.buttonStyle(.glassProminent)

// In-content styles
Button("Save") { }.buttonStyle(.borderedProminent)
Button("Skip") { }.buttonStyle(.bordered)
Button("Learn more") { }.buttonStyle(.plain)

// Roles carry semantics and change appearance
Button("Delete", role: .destructive) { }    // system red
Button("Cancel", role: .cancel) { }
```

Assign the primary role to the button people are most likely to choose — it responds to
Return and lets a sheet/alert dismiss itself. **Never** give the primary role to a
destructive action.

### Sizing

```swift
Button("Get started") { }
    .buttonStyle(.glassProminent)
    .controlSize(.extraLarge)      // extra-large sizing for headline actions
    .buttonSizing(.flexible)       // iOS 26: control how the button sizes to its container
```

Rules:
- Hit region **≥ 44×44 pt** (absolute floor 28×28 pt).
- One or two prominent buttons per view, no more.
- Distinguish the preferred option by *style*, not size — sibling options should be the
  same size.
- Always give custom buttons a press state.
- Avoid full-width buttons; inset from screen edges.

### With an activity indicator

Configure the button to show progress in place rather than blocking the screen, optionally
swapping the label ("Checkout" → "Checking out…").

## Navigation

```swift
NavigationStack(path: $path) {
    List(items) { item in
        NavigationLink(value: item) { ItemRow(item: item) }
    }
    .navigationTitle("Items")
    .navigationDestination(for: Item.self) { ItemDetail(item: $0) }
}
```

Never build a custom back button — it breaks the system swipe gesture. If you must, keep
the standard appearance and behavior.

## Tab view

```swift
TabView {
    Tab("Home", systemImage: "house.fill") { HomeView() }
    Tab("Library", systemImage: "books.vertical.fill") { LibraryView() }
    Tab(role: .search) { SearchView() }
}
.tabBarMinimizeBehavior(.onScrollDown)
.tabViewBottomAccessory { NowPlayingBar() }
```

On iPad add `.tabViewStyle(.sidebarAdaptable)`.

## Toolbar

```swift
.toolbar {
    ToolbarItem(placement: .topBarLeading) {
        Button("Close", systemImage: "xmark") { dismiss() }
    }
    ToolbarItemGroup(placement: .topBarTrailing) {
        Button("Filter", systemImage: "line.3.horizontal.decrease") { }
        Button("Sort", systemImage: "arrow.up.arrow.down") { }
    }
    ToolbarSpacer(.fixed, placement: .topBarTrailing)
    ToolbarItem(placement: .topBarTrailing) {
        Button("Done") { save() }
    }
}
```

Hide the **item**, not its content, when an action is unavailable — otherwise you get an
empty glass pill.

## Search

```swift
NavigationStack {
    List(results) { ResultRow(item: $0) }
        .searchable(text: $query, prompt: "Search items")
        .searchToolbarBehavior(.minimize)
        .searchScopes($scope) {
            Text("All").tag(Scope.all)
            Text("Mailbox").tag(Scope.mailbox)
        }
}
```

## Lists and forms

```swift
List {
    Section("Account") {                  // title case — the system no longer uppercases
        NavigationLink("Profile") { ProfileView() }
        NavigationLink("Settings") { SettingsView() }
    }
}
.listStyle(.insetGrouped)
.listSectionMargins(.horizontal, 20)      // iOS 26

Form {
    Section("Personal info") {
        TextField("Name", text: $name)
        DatePicker("Birthday", selection: $birthday, displayedComponents: .date)
    }
    Section {
        Toggle("Notifications", isOn: $notifications)
    }
}
.formStyle(.grouped)
```

Rows and sections have larger padding and corner radii than in iOS 18 — don't fight it with
hard-coded insets.

## Sheets

```swift
.sheet(isPresented: $showSheet) {
    NavigationStack {
        SheetContent()
            .toolbar {
                ToolbarItem(placement: .cancellationAction) {
                    Button("Cancel") { showSheet = false }
                }
                ToolbarItem(placement: .confirmationAction) {
                    Button("Done") { save() }
                }
            }
    }
    .presentationDetents([.medium, .large])
    .presentationDragIndicator(.visible)
}
```

## Alerts and confirmation dialogs

```swift
.alert("Delete item?", isPresented: $showAlert) {
    Button("Cancel", role: .cancel) { }
    Button("Delete", role: .destructive) { delete() }
} message: {
    Text("This action cannot be undone.")
}

.confirmationDialog("Delete this item?", isPresented: $confirming, titleVisibility: .visible) {
    Button("Delete", role: .destructive) { delete() }
    Button("Cancel", role: .cancel) { }
}
```

Confirmation dialogs now originate from the element that triggered them, so anchor them
correctly (UIKit: `sourceView` / `sourceItem`).

**iOS 27:** `alert(_:item:actions:)` and `alert(error:actions:)` let you drive an alert
from an optional data item or an error.

## Empty and loading states

```swift
ContentUnavailableView {
    Label("No results", systemImage: "magnifyingglass")
} description: {
    Text("Try a different search term.")
} actions: {
    Button("Clear filters") { clearFilters() }
        .buttonStyle(.glass)
}

ContentUnavailableView.search(text: query)   // built-in search variant

ProgressView()                                // indeterminate
ProgressView(value: fraction)                 // determinate
```

Never leave a tab empty without explaining why.

## Pull to refresh

```swift
List(items) { ItemRow(item: $0) }
    .refreshable { await loadData() }
```

## Menus

```swift
Menu {
    Button("Duplicate", systemImage: "plus.square.on.square") { }
    Button("Rename", systemImage: "pencil") { }
    Divider()
    Button("Delete", systemImage: "trash", role: .destructive) { }
} label: {
    Label("More", systemImage: "ellipsis")
}
```

Menus adopt Liquid Glass and now show icons for common actions. Use standard selectors for
standard actions so the system supplies the right icon automatically. **Match the actions at
the top of a context menu to the swipe actions you offer for the same item.**

## Custom glass control

Only when a standard component genuinely can't do the job.

```swift
@Namespace private var glassNamespace

GlassEffectContainer(spacing: 24) {
    HStack(spacing: 24) {
        Button { record() } label: {
            Image(systemName: "record.circle")
                .font(.system(size: 28))
                .frame(width: 64, height: 64)
        }
        .glassEffect(.regular.interactive())
        .glassEffectID("record", in: glassNamespace)

        if isRecording {
            Button { stop() } label: {
                Image(systemName: "stop.fill")
                    .font(.system(size: 28))
                    .frame(width: 64, height: 64)
            }
            .glassEffect(.regular.tint(.red).interactive())
            .glassEffectID("stop", in: glassNamespace)
        }
    }
}
```

## Concentric corners

```swift
CardContent()
    .background {
        ConcentricRectangle()
            .fill(.background.secondary)
    }
    .padding(12)

// Guarantee a rounded corner even where the computed radius would be 0
ConcentricRectangle(corners: .concentric(minimum: 12))
```

Declare `containerShape(_:)` on a custom container so the shape has something to be
concentric with.

## Scroll edge effect on a custom bar

```swift
ScrollView { content }
    .safeAreaBar(edge: .bottom) {
        CustomBar()
    }
    .scrollEdgeEffectStyle(.automatic, for: .bottom)
```

## Reorder and swipe (iOS 27)

```swift
// Drag-to-reorder in lists, stacks, grids, custom layouts
.reorderable()
.reorderContainer(for: Item.self) { from, to in move(from, to) }

// Swipe actions beyond List
.swipeActions(edge: .trailing) {
    Button("Delete", role: .destructive) { delete() }
}
```

## Anti-patterns

- Custom back buttons
- Hard-coded font sizes or system color values
- Custom backgrounds on bars, sheets, popovers
- Glass on content-layer cards and rows
- Fixed corner radii near screen or container edges
- Hiding a toolbar item's content instead of the item
- ALL CAPS section headers
- Full-width, edge-to-edge buttons
- Touch targets under 44 pt
- Gestures with no visual affordance
- Ignoring safe areas
