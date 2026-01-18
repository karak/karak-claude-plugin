# SF Symbols Reference

Complete guide to using SF Symbols in iOS applications.

## Overview

SF Symbols is Apple's iconography system with 5,000+ symbols that automatically align with San Francisco font. All symbols support:
- Multiple weights (ultralight to black)
- Multiple scales (small, medium, large)
- Four rendering modes
- Dynamic Type scaling
- Accessibility features

## Basic Usage

```swift
// Simple symbol
Image(systemName: "star")

// With size
Image(systemName: "star")
    .font(.system(size: 24))

// With weight
Image(systemName: "star")
    .font(.system(size: 24, weight: .medium))

// In a Label
Label("Favorites", systemImage: "star.fill")
```

## Rendering Modes

### Monochrome (Default)
Single color, respects foreground color:

```swift
Image(systemName: "cloud.sun")
    .foregroundStyle(.blue)
```

### Hierarchical
Single color with depth through opacity:

```swift
Image(systemName: "cloud.sun")
    .symbolRenderingMode(.hierarchical)
    .foregroundStyle(.blue)
```

### Palette
Two or three distinct colors:

```swift
Image(systemName: "cloud.sun")
    .symbolRenderingMode(.palette)
    .foregroundStyle(.blue, .yellow)
```

### Multicolor
SF Symbols' inherent colors (fixed):

```swift
Image(systemName: "cloud.sun")
    .symbolRenderingMode(.multicolor)
```

## Symbol Variants

Many symbols have variants:

| Variant | Example | Usage |
|---------|---------|-------|
| Outline | `heart` | Default, unselected |
| Fill | `heart.fill` | Selected state |
| Circle | `heart.circle` | Enclosed style |
| Square | `heart.square` | Boxed style |
| Slash | `heart.slash` | Disabled/unavailable |

```swift
// Toggle between states
Image(systemName: isFavorite ? "heart.fill" : "heart")
    .foregroundStyle(isFavorite ? .red : .gray)
```

## Symbol Effects (iOS 17+)

### Bounce

```swift
Image(systemName: "star.fill")
    .symbolEffect(.bounce, value: count)
```

### Pulse

```swift
Image(systemName: "antenna.radiowaves.left.and.right")
    .symbolEffect(.pulse)
```

### Variable Color

```swift
Image(systemName: "wifi")
    .symbolEffect(.variableColor.iterative)
```

### Scale

```swift
Image(systemName: "star.fill")
    .symbolEffect(.scale.up, isActive: isActive)
```

### Appear/Disappear

```swift
Image(systemName: "checkmark")
    .symbolEffect(.appear, isActive: showCheck)
```

### Replace

```swift
Image(systemName: currentSymbol)
    .contentTransition(.symbolEffect(.replace))
```

## Common Symbol Categories

### Navigation

| Symbol | Name | Usage |
|--------|------|-------|
| ← | `chevron.left` | Back navigation |
| → | `chevron.right` | Forward, disclosure |
| ↓ | `chevron.down` | Expand, dropdown |
| ↑ | `chevron.up` | Collapse |
| ✕ | `xmark` | Close, dismiss |
| ≡ | `line.3.horizontal` | Menu |

### Actions

| Symbol | Name | Usage |
|--------|------|-------|
| + | `plus` | Add, create |
| − | `minus` | Remove, decrease |
| ✓ | `checkmark` | Complete, done |
| ✎ | `pencil` | Edit |
| ⌫ | `trash` | Delete |
| ↗ | `square.and.arrow.up` | Share |
| ↻ | `arrow.clockwise` | Refresh |

### Media

| Symbol | Name | Usage |
|--------|------|-------|
| ▶ | `play.fill` | Play |
| ⏸ | `pause.fill` | Pause |
| ⏹ | `stop.fill` | Stop |
| ⏮ | `backward.fill` | Previous |
| ⏭ | `forward.fill` | Next |
| 🔊 | `speaker.wave.3.fill` | Volume |
| 🔇 | `speaker.slash.fill` | Mute |

### Communication

| Symbol | Name | Usage |
|--------|------|-------|
| ✉ | `envelope` | Email |
| 📱 | `phone` | Call |
| 💬 | `message` | Message |
| 🔔 | `bell` | Notifications |
| 👤 | `person` | Profile |
| 👥 | `person.2` | Contacts |

### Status

| Symbol | Name | Usage |
|--------|------|-------|
| ✓○ | `checkmark.circle` | Success |
| !△ | `exclamationmark.triangle` | Warning |
| ✕○ | `xmark.circle` | Error |
| ⓘ | `info.circle` | Information |
| ? | `questionmark.circle` | Help |

### Objects

| Symbol | Name | Usage |
|--------|------|-------|
| ⚙ | `gear` | Settings |
| 🏠 | `house` | Home |
| 🔍 | `magnifyingglass` | Search |
| ⭐ | `star` | Favorite |
| ❤ | `heart` | Like |
| 📁 | `folder` | Files |
| 📄 | `doc` | Document |

### Device

| Symbol | Name | Usage |
|--------|------|-------|
| 📱 | `iphone` | iPhone |
| 💻 | `laptopcomputer` | Mac |
| ⌚ | `applewatch` | Watch |
| 🎧 | `airpodspro` | AirPods |
| 📷 | `camera` | Camera |

## Sizing and Alignment

### Match Text Size

```swift
HStack {
    Image(systemName: "star.fill")
        .font(.body)  // Matches body text size

    Text("Favorite")
        .font(.body)
}
```

### Image Scale

```swift
Image(systemName: "star.fill")
    .imageScale(.small)   // Smaller
    .imageScale(.medium)  // Default
    .imageScale(.large)   // Larger
```

### Baseline Alignment

SF Symbols automatically align to text baseline:

```swift
HStack(alignment: .firstTextBaseline) {
    Image(systemName: "star.fill")
    Text("Rating")
}
```

## Accessibility

### Labels

Always provide accessibility labels for meaning:

```swift
Image(systemName: "star.fill")
    .accessibilityLabel("Favorite")

// Hide decorative symbols
Image(systemName: "chevron.right")
    .accessibilityHidden(true)
```

### Bold Text Support

SF Symbols automatically bold when Bold Text is enabled.

### VoiceOver

Symbols in Labels are automatically described:

```swift
// VoiceOver: "Favorites"
Label("Favorites", systemImage: "star.fill")

// For custom behavior:
Button {
    action()
} label: {
    Image(systemName: "plus")
}
.accessibilityLabel("Add item")
```

## Custom Symbols

Create custom symbols compatible with SF Symbols:

1. Design in SF Symbols app or Sketch
2. Export as SVG
3. Import to Asset Catalog as Symbol Image Set
4. Use like system symbols

```swift
Image("custom.symbol.name")
    .font(.system(size: 24))
```

## Best Practices

### Do:
- Use filled variants for selected states
- Match symbol weight to text weight
- Use rendering modes consistently
- Provide accessibility labels
- Test with Bold Text enabled
- Use symbol effects for feedback

### Don't:
- Mix too many rendering modes
- Use symbols without context
- Forget accessibility labels
- Use symbols that don't scale well
- Override symbol colors unnecessarily

## Common Patterns

### Tab Bar Icons

```swift
TabView {
    HomeView()
        .tabItem {
            Label("Home", systemImage: "house.fill")
        }

    SearchView()
        .tabItem {
            Label("Search", systemImage: "magnifyingglass")
        }
}
```

### Toolbar Buttons

```swift
.toolbar {
    ToolbarItem(placement: .navigationBarTrailing) {
        Button {
            add()
        } label: {
            Image(systemName: "plus")
        }
    }
}
```

### Toggle with Symbol

```swift
Button {
    isFavorite.toggle()
} label: {
    Image(systemName: isFavorite ? "heart.fill" : "heart")
        .foregroundStyle(isFavorite ? .red : .secondary)
        .symbolEffect(.bounce, value: isFavorite)
}
```

### Loading Indicator

```swift
Image(systemName: "arrow.triangle.2.circlepath")
    .symbolEffect(.rotate, isActive: isLoading)
```

### Badge with Symbol

```swift
Image(systemName: "bell.fill")
    .overlay(alignment: .topTrailing) {
        if badgeCount > 0 {
            Circle()
                .fill(.red)
                .frame(width: 8, height: 8)
        }
    }
```

## Finding Symbols

### SF Symbols App
Download from Apple Developer for browsing all symbols.

### Xcode Library
Use the Library panel (⌘⇧L) to browse and insert symbols.

### Search Patterns
- Object: `house`, `car`, `building`
- Action: `plus`, `minus`, `xmark`
- State: `checkmark`, `exclamationmark`
- Arrow: `arrow.up`, `chevron.down`
- Shape: `circle`, `square`, `rectangle`
