# Layout and Navigation (iOS 26+)

## Layout fundamentals

**Extend content to fill the screen.** Backgrounds and full-screen artwork reach the edges;
scrollable layouts continue to the bottom and sides. Controls and navigation live on a
separate plane above content, so your layout must assume things pass beneath them.

**Differentiate controls from content.** That separation is the job of the Liquid Glass
material plus a scroll edge effect — not a solid bar background.

**Where content doesn't span the full window**, use `backgroundExtensionEffect()` (UIKit:
`UIBackgroundExtensionView`) to give the appearance of content continuing behind the
control layer, e.g. beneath a sidebar or inspector.

**Avoid full-width buttons.** Buttons feel at home in iOS when they respect system margins
and are inset from the screen edges. If a full-width button is unavoidable, make it
harmonize with the hardware curvature and align with adjacent safe areas.

**Keep the status bar** unless you're offering an in-depth experience like a game or media
playback.

**Support both orientations** where you can. If the app is landscape-only, it must work
rotated either direction.

### Safe areas

A safe area is the region not covered by toolbars, tab bars, or system features — Dynamic
Island, home indicator, camera housing. Respect it via `SafeAreaRegions` and layout guides
rather than hard-coded insets. Safe areas also reposition content when bar sizes change,
which now happens dynamically (e.g. a minimizing tab bar).

### Spacing

Use the system's standard spacing metrics rather than overriding them; overriding is what
causes crowding and overlapping glass. When you need explicit values, an 8-pt rhythm
(4 / 8 / 16 / 24 / 32) matches system margins, with 16 pt as the standard horizontal margin.

### iPad adaptivity

- Windows resize **continuously** down to a minimum size — not between presets. Support
  arbitrary sizes.
- Design for the full-screen layout first and **defer switching to a compact layout** as
  long as possible; for complex split views, hide tertiary columns (inspectors) first.
- Test at the system arrangement sizes: halves, thirds, quadrants.
- Use `NavigationSplitView` (UIKit: `UISplitViewController`) so columns reflow with fluid
  system animations.
- A toolbar and a tab bar can coexist in the same horizontal space at the top of the view.

## Tab bars

Tab bars are for **navigation between top-level sections** — never for actions. Actions go
in a toolbar.

On iPhone the tab bar floats above content at the bottom of the screen in a Liquid Glass
capsule, with content peeking through beneath. On iPad it sits near the top.

Rules:
- Keep it visible as people navigate; only a modal may cover it.
- Never disable or hide individual tabs. If a section is empty, explain why inside it.
- Include short labels — single words where possible.
- Prefer **filled** SF Symbols for consistency with the platform.
- Avoid overflow. If tabs don't fit, the trailing one becomes a More tab, which buries
  content. Reduce tabs or adopt `.sidebarAdaptable`.
- Badge only for genuinely critical information.
- If your content layer is bright and colorful, keep the tab bar monochromatic or pick an
  accent color with real differentiation.

```swift
TabView {
    Tab("Home", systemImage: "house.fill") { HomeView() }
    Tab("Library", systemImage: "books.vertical.fill") { LibraryView() }

    // Search gets a semantic role; the system separates it and pins it trailing
    Tab(role: .search) { SearchView() }
}
.tabBarMinimizeBehavior(.onScrollDown)
```

### Minimize on scroll

The tab bar can recede while scrolling to elevate content, then expand when the person
scrolls the other way. Tapping a tab or scrolling to the top exits the minimized state.

```swift
.tabBarMinimizeBehavior(.onScrollDown)   // or .onScrollUp, .never, .automatic
```

UIKit: `tabBarMinimizeBehavior = .onScrollDown`.

### Bottom accessory

Attach a persistent accessory — a now-playing bar, an active-session pill — that moves
inline with the tab bar when minimized.

```swift
TabView { /* ... */ }
    .tabViewBottomAccessory {
        NowPlayingBar()
    }
    .tabBarMinimizeBehavior(.onScrollDown)
```

Adjust the accessory's content for its context with the
`\.tabViewBottomAccessoryPlacement` environment value (`TabViewBottomAccessoryPlacement`),
which tells you whether it's expanded or inline.

### iPad: adaptable sidebar

```swift
TabView { /* tabs */ }
    .tabViewStyle(.sidebarAdaptable)
```

Presents as a tab bar or a sidebar with a button to switch, adapting to rotation and window
resizing. Prefer a tab bar first; offer the sidebar when the app has more sections than fit.
Let people customize which tabs appear (`TabViewCustomization`), aiming for a default of
five or fewer. To present a sidebar *without* the tab-bar option, use `NavigationSplitView`
instead.

### iOS 27 addition

`Tab(role: .prominent)` places a tab in a separate, trailing position of the tab bar.

## Toolbars

A toolbar holds the view title, navigation controls, search, and actions. Three placement
regions:

- **Leading edge** — back button, sidebar toggle, title, document menu. Not customizable.
- **Center** — common controls; on iPad/Mac these can be customized and collapse into a
  system overflow menu as the window narrows.
- **Trailing edge** — items that must stay available, inspector toggles, optional search,
  the More menu, and the single primary action. Always visible at all widths.

Rules:
- **Maximum ~3 logical groups.** Group by function and frequency.
- **Exactly one `.prominent` action**, on the trailing edge (Done, Submit). It gets tinted
  and separated to form a clear focal point.
- **Prefer symbols over text**, except for actions symbols represent badly (e.g. "Edit").
  Don't mix text and symbols among items that share a background.
- **Separate text-labeled buttons** with `ToolbarSpacer` — adjacent text buttons visually
  run together, and a text button next to a symbol button reads as one combined item.
- **No borders on symbols.** The section provides the container; the system supplies hover
  and selection appearance.
- **Never add an overflow menu manually** — the system adds one on iPad/Mac when needed.
  Add a *More* menu only for genuinely lower-priority actions.
- **Always supply an accessibility label** for every icon, even when text is visible.
- Keep titles under ~15 characters. Never title a window with the app name.

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
    .sharedBackgroundVisibility(.hidden)
}
```

Large titles still work: they transition to a standard title as content scrolls and back
when it returns to top, which helps orientation.

**iOS 27 additions:** `visibilityPriority(_:)` to control which items survive as space
shrinks, `ToolbarOverflowMenu` to send secondary actions (archive, delete) straight to
overflow, and `topBarPinnedTrailing` placement to anchor an item to the trailing edge.

## Sidebars

Sidebars float in the Liquid Glass layer like other controls.

- **Extend visually rich content beneath the sidebar** — either let it scroll horizontally
  or apply `backgroundExtensionEffect()`.
- Show at most **two levels of hierarchy**; deeper structures want a split view with a
  content list column.
- Let people customize contents and hide/show the sidebar using platform-native
  interactions. Don't hide it by default.
- Sidebar icons use the app accent color by default. Fixed colors are legitimate only when
  the color carries meaning (Mail's yellow VIP icon).
- Use `Disclosure` controls to group deep hierarchies and keep vertical space manageable.

## Search

Three entry points on iPhone; pick by how central search is.

### Search as a tab

Use `Tab(role: .search)`. Two styles:

- **Standard tab** — navigates to a search landing page with the field at the top. Choose
  this to surface suggestions, categories, and browsable content before the person types.
  (Apple TV works this way.)
- **Button appearance** — displays as a separate button and focuses the field immediately
  with the keyboard up, returning people to their previous tab on exit. Choose this when
  search should resolve quickly and transiently.

### Search in a toolbar

```swift
NavigationStack {
    List { /* ... */ }
        .searchable(text: $query, prompt: "Search items")
        .searchToolbarBehavior(.minimize)
}
```

- **Prefer the bottom** when there's room — either alongside other controls or as the sole
  item in its own toolbar. Tapping animates it into a field above the keyboard. (Settings
  uses search as the only bottom-toolbar item; Mail and Notes fit it alongside others.)
- **Use the top** only when bottom content must stay visible — e.g. Wallet keeps passes
  reachable at the bottom — or when there's no bottom toolbar.
- Check that the field slides up correctly with the keyboard.

### Inline search field

Place it directly above the list it filters when the relationship to *that* content matters
— e.g. a second, scoped search inside a library view. Consider pinning it to the top
toolbar as the person scrolls.

### Behavior

- Start searching as the person types.
- Show recent searches before, and suggestions during, typing.
- Offer scope bars for clearly defined categories, defaulting to the broader scope.
- Offer tokens for common filters, and pair them with suggestions so people discover them.

On iPad and Mac, put search at the trailing side of the toolbar for most apps, at the top of
the sidebar when it filters navigation, or as a dedicated sidebar/tab item when search is a
discovery surface.

## Sheets

Sheets adopt Liquid Glass, have an increased corner radius, and half sheets are inset from
the display edge so content peeks through. Expanding to full height transitions to a more
opaque appearance.

```swift
.sheet(isPresented: $showSheet) {
    SheetContent()
        .presentationDetents([.medium, .large])
        .presentationDragIndicator(.visible)
}
```

- **Cancel goes leading, Done goes trailing** in the sheet's top toolbar.
- **Never ship Done without Cancel** (or Back). Done alone implies completing the task is
  the only exit.
- **Never show Cancel, Done, and Back together.**
- One sheet at a time. If a sheet triggers another, dismiss the first.
- Include a grabber on a resizable sheet — it signals resizability and works with VoiceOver.
- Support swipe-to-dismiss; confirm with a confirmation dialog if there are unsaved changes.
- Check content near the larger corner radius, and check what shows through between an inset
  sheet and the display edge.
- Use a **nonmodal** sheet when the person needs to keep affecting the parent view (Notes
  formatting).
- For long or complex flows, prefer full-screen presentation over a sheet.
- On iPad, prefer the page or form sheet presentation styles.

## Action sheets / confirmation dialogs

An action sheet now originates from the element that triggered it rather than the bottom
edge, and lets people interact with the rest of the interface while it's up. Set the source
so it anchors correctly.

```swift
.confirmationDialog("Delete this item?", isPresented: $confirming, titleVisibility: .visible) {
    Button("Delete", role: .destructive) { delete() }
    Button("Cancel", role: .cancel) { }
}
```

UIKit: set `sourceView` / `sourceItem`.

## Lists, tables, and forms

Rows have larger height and padding, sections have an increased corner radius, and
**section headers render in title case** — the system no longer uppercases them, so update
your strings.

```swift
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

Adopt `Form` with `.grouped` to pick up the updated layout metrics automatically. Tune
section insets with `listSectionMargins(_:_:)` when needed.
