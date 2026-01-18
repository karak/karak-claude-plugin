---
name: apple-design
description: "Design beautiful iOS/iPadOS user interfaces following Apple Human Interface Guidelines (HIG). This skill should be used when creating SwiftUI views, designing app screens, implementing navigation patterns, choosing colors/typography, or ensuring accessibility compliance. Provides comprehensive design system including SF Symbols usage, semantic colors, Dynamic Type, and platform-specific UI patterns."
---

# Apple Design Skill

Design iOS/iPadOS user interfaces that follow Apple Human Interface Guidelines (HIG) for a native, intuitive user experience.

## When to Use

- Creating new SwiftUI views or screens
- Designing navigation and information architecture
- Implementing color schemes and typography
- Ensuring accessibility compliance
- Reviewing UI for HIG conformance
- Choosing appropriate UI patterns for iOS

## Core Design Principles

### 1. Clarity
- Use negative space generously
- Ensure text is legible at every size
- Use precise, clear language
- Icons should be accurate and obvious

### 2. Deference
- Content should be the focus
- Use translucency and blurs appropriately
- Minimize borders, gradients, and shadows
- Let the content speak for itself

### 3. Depth
- Use distinct visual layers
- Provide realistic motion
- Create hierarchy through depth
- Use transitions that convey relationships

## Implementation Guidelines

### Typography

Always use Dynamic Type with semantic text styles:

```swift
// Correct - Using semantic styles
Text("Title")
    .font(.largeTitle)    // 34pt, Bold

Text("Headline")
    .font(.headline)      // 17pt, Semibold

Text("Body")
    .font(.body)          // 17pt, Regular

Text("Caption")
    .font(.caption)       // 12pt, Regular

// For custom fonts, maintain Dynamic Type support
Text("Custom")
    .font(.custom("SF Pro Display", size: 17, relativeTo: .body))
```

See `references/typography.md` for complete text style specifications.

### Colors

Use semantic colors that adapt to Light/Dark mode:

```swift
// Primary semantic colors
Color.primary      // Labels, text (adapts to mode)
Color.secondary    // Secondary labels
Color.accentColor  // App tint, interactive elements

// Background colors
Color(.systemBackground)           // Primary background
Color(.secondarySystemBackground)  // Grouped content
Color(.tertiarySystemBackground)   // Elevated elements

// System colors (adapt automatically)
Color.blue    // Links, selection
Color.green   // Success, positive
Color.red     // Errors, destructive
Color.orange  // Warnings
```

See `references/colors.md` for complete palette and accessibility guidelines.

### Spacing and Layout

Use consistent 8pt grid system:

```swift
// Standard spacing values
let spacingXS: CGFloat = 4
let spacingSM: CGFloat = 8
let spacingMD: CGFloat = 16
let spacingLG: CGFloat = 24
let spacingXL: CGFloat = 32

// Safe area and margins
VStack {
    content
}
.padding(.horizontal, 16)  // Standard horizontal margin
```

### Touch Targets

Minimum touch target: **44x44 points**

```swift
Button(action: action) {
    Image(systemName: "plus")
        .font(.system(size: 20))
}
.frame(minWidth: 44, minHeight: 44)
```

### SF Symbols

Always use SF Symbols for iconography:

```swift
// Basic usage
Image(systemName: "star.fill")

// With rendering mode
Image(systemName: "gear")
    .symbolRenderingMode(.hierarchical)
    .font(.system(size: 24, weight: .medium))

// Animated (iOS 17+)
Image(systemName: "checkmark.circle")
    .symbolEffect(.bounce, value: isComplete)
```

See `references/sf-symbols.md` for symbol categories.

### Navigation Patterns

#### Tab Bar
```swift
TabView {
    HomeView()
        .tabItem {
            Label("Home", systemImage: "house")
        }
    SearchView()
        .tabItem {
            Label("Search", systemImage: "magnifyingglass")
        }
}
```
- Maximum 5 tabs
- Use filled icons for selected state

#### Navigation Stack
```swift
NavigationStack {
    List(items) { item in
        NavigationLink(value: item) {
            ItemRow(item: item)
        }
    }
    .navigationTitle("Items")
    .navigationDestination(for: Item.self) { item in
        ItemDetail(item: item)
    }
}
```

#### Sheets
```swift
.sheet(isPresented: $showSheet) {
    SheetContent()
        .presentationDetents([.medium, .large])
        .presentationDragIndicator(.visible)
}
```

### Lists and Forms

```swift
// Grouped list
List {
    Section("Account") {
        NavigationLink("Profile", destination: ProfileView())
        NavigationLink("Settings", destination: SettingsView())
    }
}
.listStyle(.insetGrouped)

// Form
Form {
    Section("Personal Info") {
        TextField("Name", text: $name)
        DatePicker("Birthday", selection: $birthday)
    }
    Section {
        Toggle("Notifications", isOn: $notifications)
    }
}
```

### Buttons

```swift
// Primary action
Button("Continue") { action() }
    .buttonStyle(.borderedProminent)

// Secondary action
Button("Skip") { skip() }
    .buttonStyle(.bordered)

// Destructive action
Button("Delete", role: .destructive) { delete() }
```

### Alerts

```swift
.alert("Delete Item?", isPresented: $showAlert) {
    Button("Cancel", role: .cancel) { }
    Button("Delete", role: .destructive) { delete() }
} message: {
    Text("This action cannot be undone.")
}
```

## Accessibility

### VoiceOver

```swift
Image(systemName: "star.fill")
    .accessibilityLabel("Favorite")

Button(action: toggleFavorite) {
    Image(systemName: isFavorite ? "heart.fill" : "heart")
}
.accessibilityLabel(isFavorite ? "Remove from favorites" : "Add to favorites")
```

### Dynamic Type

```swift
@Environment(\.dynamicTypeSize) var dynamicTypeSize

var body: some View {
    if dynamicTypeSize.isAccessibilitySize {
        VStack { content }  // Stack vertically for large text
    } else {
        HStack { content }  // Normal horizontal layout
    }
}
```

### Reduce Motion

```swift
@Environment(\.accessibilityReduceMotion) var reduceMotion

withAnimation(reduceMotion ? nil : .spring()) {
    // Animation
}
```

### Color Contrast
- Minimum 4.5:1 for normal text
- Minimum 3:1 for large text (18pt+)
- Never convey information by color alone

## Common Patterns

### Loading States
```swift
ProgressView()
    .progressViewStyle(.circular)
```

### Empty States
```swift
ContentUnavailableView {
    Label("No Results", systemImage: "magnifyingglass")
} description: {
    Text("Try searching for something else.")
}
```

### Pull to Refresh
```swift
List {
    ForEach(items) { item in
        ItemRow(item: item)
    }
}
.refreshable {
    await loadData()
}
```

### Search
```swift
NavigationStack {
    List { /* content */ }
        .searchable(text: $searchText, prompt: "Search items")
}
```

## Anti-Patterns to Avoid

### Do NOT:
- Use custom back buttons (breaks system gestures)
- Override system colors without semantic alternatives
- Use fixed font sizes (breaks Dynamic Type)
- Place destructive actions where users might tap accidentally
- Use gestures without visual affordances
- Ignore safe areas
- Use small touch targets (<44pt)

### Do:
- Follow platform conventions
- Use system controls when possible
- Test on real devices
- Support both orientations
- Test with accessibility features enabled
- Use semantic colors and fonts

## Resources

- `references/typography.md` - Complete typography specifications
- `references/colors.md` - Full color palette with semantic meanings
- `references/sf-symbols.md` - SF Symbols categories and usage
- `references/components.md` - Standard component patterns
- `references/animations.md` - Motion design guidelines

## Quick Reference

| Element | Minimum Size | Typical Size |
|---------|--------------|--------------|
| Touch target | 44x44pt | 44x44pt |
| Icon in button | 20pt | 24pt |
| Tab bar icon | 24pt | 28pt |
| Body text | 17pt | 17pt |
| Horizontal margin | 16pt | 20pt |
