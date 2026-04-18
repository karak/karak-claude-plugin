# iOS Color System

Complete color palette and guidelines following Apple Human Interface Guidelines.

## Semantic Colors

### Label Colors

Colors that automatically adapt to Light/Dark mode:

```swift
// Primary label - Most important text
Color.primary       // Light: #000000, Dark: #FFFFFF

// Secondary label - Subheadings, secondary info
Color.secondary     // Light: 60% opacity, Dark: 60% opacity

// Tertiary label - Disabled text, placeholders
Color(.tertiaryLabel)  // Light: 30% opacity, Dark: 30% opacity

// Quaternary label - Watermarks, separator lines
Color(.quaternaryLabel)  // Light: 18% opacity, Dark: 18% opacity
```

### Background Colors

```swift
// System backgrounds (adapts to mode and elevation)
Color(.systemBackground)            // Primary view background
Color(.secondarySystemBackground)   // Grouped content background
Color(.tertiarySystemBackground)    // Elevated content

// Grouped backgrounds (for grouped table views)
Color(.systemGroupedBackground)
Color(.secondarySystemGroupedBackground)
Color(.tertiarySystemGroupedBackground)
```

### Fill Colors

```swift
// System fills for UI elements
Color(.systemFill)           // Thin overlay
Color(.secondarySystemFill)  // Medium overlay
Color(.tertiarySystemFill)   // Thick overlay
Color(.quaternarySystemFill) // Thickest overlay
```

### Separator Colors

```swift
Color(.separator)         // Standard separator
Color(.opaqueSeparator)   // Opaque separator (no transparency)
```

## System Colors

Tint colors that work in both Light and Dark modes:

| Color | Light Mode | Dark Mode | Usage |
|-------|------------|-----------|-------|
| `.blue` | #007AFF | #0A84FF | Links, selection, interactive |
| `.green` | #34C759 | #30D158 | Success, positive actions |
| `.indigo` | #5856D6 | #5E5CE6 | Secondary accent |
| `.orange` | #FF9500 | #FF9F0A | Warnings, attention |
| `.pink` | #FF2D55 | #FF375F | Special, creative |
| `.purple` | #AF52DE | #BF5AF2 | Premium, special features |
| `.red` | #FF3B30 | #FF453A | Errors, destructive |
| `.teal` | #5AC8FA | #64D2FF | Info, alternate accent |
| `.yellow` | #FFCC00 | #FFD60A | Caution, highlights |
| `.gray` | #8E8E93 | #8E8E93 | Neutral, disabled |

### Accessible System Colors

Higher contrast versions for accessibility:

```swift
Color(.systemBlue)       // Standard blue
Color(.systemCyan)       // Cyan variant
Color(.systemMint)       // Mint green
Color(.systemBrown)      // Brown
```

## Custom Colors

### Defining Custom Colors

In Asset Catalog (recommended):
1. Add Color Set to Assets.xcassets
2. Define Light and Dark appearances
3. Set High Contrast variants

```swift
// Access from Asset Catalog
Color("BrandPrimary")
Color("BrandSecondary")
```

### Programmatic Custom Colors

```swift
extension Color {
    static let brandPrimary = Color(
        light: Color(red: 0.2, green: 0.4, blue: 0.8),
        dark: Color(red: 0.3, green: 0.5, blue: 0.9)
    )
}

// Helper extension
extension Color {
    init(light: Color, dark: Color) {
        self.init(UIColor { traits in
            traits.userInterfaceStyle == .dark
                ? UIColor(dark)
                : UIColor(light)
        })
    }
}
```

### High Contrast Support

```swift
extension Color {
    static let accessibleBlue = Color(UIColor { traits in
        if traits.accessibilityContrast == .high {
            return traits.userInterfaceStyle == .dark
                ? UIColor(red: 0.1, green: 0.6, blue: 1.0, alpha: 1)
                : UIColor(red: 0.0, green: 0.3, blue: 0.7, alpha: 1)
        } else {
            return traits.userInterfaceStyle == .dark
                ? UIColor.systemBlue
                : UIColor.systemBlue
        }
    })
}
```

## Accessibility Requirements

### Contrast Ratios

| Text Size | Minimum Ratio | Target Ratio |
|-----------|---------------|--------------|
| Normal text (<18pt) | 4.5:1 | 7:1 |
| Large text (≥18pt) | 3:1 | 4.5:1 |
| UI components | 3:1 | 4.5:1 |

### Checking Contrast

```swift
// Use Accessibility Inspector in Xcode
// Or online tools like WebAIM Contrast Checker

// Common passing combinations:
// - Black text on white: 21:1 ✓
// - White text on blue (#007AFF): 4.52:1 ✓
// - White text on red (#FF3B30): 4.01:1 ⚠️ (use darker red)
```

### Color Blindness

Never convey information by color alone:

```swift
// Bad - relies only on color
Circle()
    .fill(isSuccess ? .green : .red)

// Good - uses icon as well
HStack {
    Image(systemName: isSuccess ? "checkmark.circle" : "xmark.circle")
    Circle()
        .fill(isSuccess ? .green : .red)
}
```

## Common Patterns

### Status Indicators

```swift
struct StatusBadge: View {
    enum Status {
        case success, warning, error, info

        var color: Color {
            switch self {
            case .success: return .green
            case .warning: return .orange
            case .error: return .red
            case .info: return .blue
            }
        }

        var icon: String {
            switch self {
            case .success: return "checkmark.circle.fill"
            case .warning: return "exclamationmark.triangle.fill"
            case .error: return "xmark.circle.fill"
            case .info: return "info.circle.fill"
            }
        }
    }

    let status: Status
    let message: String

    var body: some View {
        Label(message, systemImage: status.icon)
            .foregroundStyle(status.color)
    }
}
```

### Card with Background

```swift
VStack {
    content
}
.padding()
.background(Color(.secondarySystemBackground))
.clipShape(RoundedRectangle(cornerRadius: 12))
```

### Gradient Background

```swift
LinearGradient(
    colors: [.blue, .purple],
    startPoint: .topLeading,
    endPoint: .bottomTrailing
)

// Accessible gradient
LinearGradient(
    colors: [
        Color.blue.opacity(0.8),
        Color.purple.opacity(0.8)
    ],
    startPoint: .top,
    endPoint: .bottom
)
.overlay {
    // Ensure text contrast
    Color.black.opacity(0.3)
}
```

### Button States

```swift
struct StyledButton: View {
    @Environment(\.isEnabled) var isEnabled
    let title: String
    let action: () -> Void

    var body: some View {
        Button(action: action) {
            Text(title)
                .foregroundStyle(isEnabled ? .white : .secondary)
        }
        .buttonStyle(.borderedProminent)
        .tint(isEnabled ? .blue : .gray)
    }
}
```

## Dark Mode Considerations

### Material Backgrounds

Use materials for translucent backgrounds:

```swift
.background(.ultraThinMaterial)
.background(.thinMaterial)
.background(.regularMaterial)
.background(.thickMaterial)
.background(.ultraThickMaterial)
```

### Elevation and Shadows

Dark mode uses elevated backgrounds instead of shadows:

```swift
// Light mode: uses shadow
// Dark mode: uses lighter background
.background(Color(.systemBackground))
.shadow(color: .black.opacity(0.1), radius: 8, y: 4)

// Better approach - works in both modes
.background(Color(.secondarySystemBackground))
```

### Vibrancy

```swift
.foregroundStyle(.primary)
.background(.ultraThinMaterial)
```

## Color Usage Guidelines

### Do:
- Use semantic colors (`.primary`, `.secondary`)
- Support both Light and Dark modes
- Test with Increase Contrast enabled
- Provide non-color cues for status
- Use system colors for consistency
- Define custom colors in Asset Catalog

### Don't:
- Hard-code hex colors without dark mode support
- Use pure black (#000000) on pure white (too harsh)
- Rely solely on color for meaning
- Use too many accent colors
- Override system colors unnecessarily
- Use low-contrast color combinations

## Testing Colors

### In Xcode

1. **Environment overrides**: Change appearance to test Light/Dark
2. **Accessibility Inspector**: Check contrast ratios
3. **Color blindness filters**: Test deuteranopia, protanopia, tritanopia

### Programmatically

```swift
#Preview {
    ContentView()
        .preferredColorScheme(.dark)
        .environment(\.accessibilityContrast, .high)
}
```

## Brand Color Integration

When integrating brand colors:

1. **Define in Asset Catalog** with Light/Dark variants
2. **Ensure accessibility** - test contrast ratios
3. **Use sparingly** - accent only, not backgrounds
4. **Complement system colors** - don't replace them

```swift
// Brand accent color
extension Color {
    static let brandAccent = Color("BrandAccent")
}

// Usage
Button("Brand Action") { }
    .tint(.brandAccent)
```
