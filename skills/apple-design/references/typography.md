# iOS Typography System

Complete typography specifications following Apple Human Interface Guidelines.

## San Francisco Font Family

### SF Pro
Primary system font for iOS, iPadOS, macOS, and tvOS.
- **SF Pro Display**: Optimized for larger sizes (20pt+)
- **SF Pro Text**: Optimized for smaller sizes (<20pt)
- **SF Pro Rounded**: Rounded variant for friendly UI

### SF Compact
Compact width for watchOS and space-constrained UI.
- **SF Compact Display**: Larger sizes
- **SF Compact Text**: Smaller sizes
- **SF Compact Rounded**: Rounded variant

### SF Mono
Monospaced font for code and technical content.

## Dynamic Type Text Styles

| Style | Default Size | Weight | Usage |
|-------|-------------|--------|-------|
| `.largeTitle` | 34pt | Bold | Major screen titles, hero text |
| `.title` | 28pt | Regular | Primary section headers |
| `.title2` | 22pt | Regular | Secondary section headers |
| `.title3` | 20pt | Regular | Tertiary headers, card titles |
| `.headline` | 17pt | Semibold | Important labels, list headers |
| `.body` | 17pt | Regular | Main content text |
| `.callout` | 16pt | Regular | Supplementary information |
| `.subheadline` | 15pt | Regular | Descriptions below headlines |
| `.footnote` | 13pt | Regular | Secondary text, metadata |
| `.caption` | 12pt | Regular | Annotations, timestamps |
| `.caption2` | 11pt | Regular | Smallest readable text |

## Dynamic Type Size Categories

Users can adjust text size in Settings. Support all categories:

| Category | Multiplier | Notes |
|----------|------------|-------|
| `xSmall` | 0.82x | Smallest standard |
| `small` | 0.88x | |
| `medium` | 0.94x | |
| `large` | 1.0x | Default |
| `xLarge` | 1.12x | |
| `xxLarge` | 1.24x | |
| `xxxLarge` | 1.35x | Largest standard |
| `accessibility1` | 1.65x | Accessibility sizes |
| `accessibility2` | 1.94x | |
| `accessibility3` | 2.35x | |
| `accessibility4` | 2.76x | |
| `accessibility5` | 3.12x | Largest |

## Implementation

### Basic Usage

```swift
Text("Welcome")
    .font(.largeTitle)

Text("Section Header")
    .font(.title2)

Text("Body content goes here...")
    .font(.body)
```

### Custom Fonts with Dynamic Type

```swift
// Maintains Dynamic Type scaling
Text("Custom")
    .font(.custom("Avenir-Medium", size: 17, relativeTo: .body))

// Fixed size (avoid in most cases)
Text("Fixed")
    .font(.custom("Avenir-Medium", fixedSize: 17))
```

### Font Weight Modifiers

```swift
Text("Light")
    .fontWeight(.light)

Text("Regular")
    .fontWeight(.regular)

Text("Medium")
    .fontWeight(.medium)

Text("Semibold")
    .fontWeight(.semibold)

Text("Bold")
    .fontWeight(.bold)

Text("Heavy")
    .fontWeight(.heavy)

Text("Black")
    .fontWeight(.black)
```

### Text Styling

```swift
Text("Important")
    .font(.headline)
    .foregroundStyle(.primary)

Text("Secondary info")
    .font(.subheadline)
    .foregroundStyle(.secondary)

Text("Tertiary")
    .font(.caption)
    .foregroundStyle(.tertiary)
```

### Multiline Text

```swift
Text("Long content that may wrap to multiple lines")
    .font(.body)
    .lineSpacing(4)
    .lineLimit(3)
    .truncationMode(.tail)
```

### Text Alignment

```swift
Text("Centered text")
    .multilineTextAlignment(.center)

Text("Leading aligned")
    .multilineTextAlignment(.leading)

Text("Trailing aligned")
    .multilineTextAlignment(.trailing)
```

## Accessibility Considerations

### Check for Large Text

```swift
@Environment(\.dynamicTypeSize) var dynamicTypeSize

var body: some View {
    if dynamicTypeSize >= .accessibility1 {
        // Adjust layout for large text
        VStack(alignment: .leading) {
            label
            value
        }
    } else {
        // Standard horizontal layout
        HStack {
            label
            Spacer()
            value
        }
    }
}
```

### Allow Text Scaling

```swift
// Allow scaling (default)
Text("Scales with system")
    .font(.body)

// Limit scaling for specific UI
Text("Limited scaling")
    .font(.body)
    .dynamicTypeSize(...DynamicTypeSize.xxxLarge)
```

### Minimum Font Size

```swift
Text("Scalable with minimum")
    .font(.body)
    .minimumScaleFactor(0.5)
```

## Typography Best Practices

### Do:
- Use semantic text styles (`.body`, `.headline`, etc.)
- Test with all Dynamic Type sizes
- Provide adequate line spacing for readability
- Use appropriate contrast ratios
- Support Bold Text accessibility setting

### Don't:
- Use fixed font sizes without good reason
- Mix too many font styles in one view
- Make text too small (minimum 11pt)
- Use light gray text on white backgrounds
- Truncate important information

## Common Patterns

### Page Title with Subtitle

```swift
VStack(alignment: .leading, spacing: 4) {
    Text("Page Title")
        .font(.largeTitle)
        .fontWeight(.bold)

    Text("Supporting description")
        .font(.subheadline)
        .foregroundStyle(.secondary)
}
```

### List Row

```swift
HStack {
    VStack(alignment: .leading, spacing: 2) {
        Text("Primary Label")
            .font(.body)

        Text("Secondary info")
            .font(.caption)
            .foregroundStyle(.secondary)
    }

    Spacer()

    Text("Value")
        .font(.body)
        .foregroundStyle(.secondary)
}
```

### Card Header

```swift
VStack(alignment: .leading, spacing: 8) {
    Text("CATEGORY")
        .font(.caption)
        .fontWeight(.semibold)
        .foregroundStyle(.secondary)
        .tracking(0.5)

    Text("Card Title")
        .font(.title3)
        .fontWeight(.semibold)
}
```

### Button Label

```swift
Button {
    action()
} label: {
    Text("Continue")
        .font(.headline)
}
.buttonStyle(.borderedProminent)
```

## SF Symbols with Typography

Match symbol weight to text weight:

```swift
Label {
    Text("Settings")
        .font(.body)
} icon: {
    Image(systemName: "gear")
        .font(.body)  // Matches text size
}

// With explicit weight
HStack(spacing: 8) {
    Image(systemName: "star.fill")
        .font(.system(size: 17, weight: .semibold))

    Text("Favorites")
        .font(.headline)  // 17pt semibold
}
```

## Localization Considerations

### Right-to-Left Languages

```swift
Text("Arabic text")
    .environment(\.layoutDirection, .rightToLeft)
```

### Variable Text Length

Always design for text expansion (German can be 30% longer than English):

```swift
// Allow wrapping
Text(LocalizedStringKey("action_button"))
    .lineLimit(2)
    .minimumScaleFactor(0.8)
```

### Date and Number Formatting

```swift
// Localized date
Text(date, style: .date)
    .font(.subheadline)

// Localized number
Text(value, format: .number)
    .font(.body)

// Localized currency
Text(price, format: .currency(code: "USD"))
    .font(.headline)
```
