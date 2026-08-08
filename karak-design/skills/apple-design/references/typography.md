# Typography (iOS 26+)

## System fonts

**SF Pro** is the system font on iOS and iPadOS. **New York (NY)** is available as a serif
alternative. Both ship as **variable fonts**.

Because they're variable fonts with **dynamic optical sizes**, the old discrete "SF Pro
Text" / "SF Pro Display" split no longer applies — the system interpolates each glyph to
the exact point size. You only need discrete optical sizes when working in a design tool
that doesn't support variable fonts.

Never embed the system fonts in your app. Reach them through `Font.Design`:

```swift
.font(.system(.body, design: .default))   // SF Pro
.font(.system(.body, design: .serif))     // New York
.font(.system(.body, design: .rounded))   // SF Pro Rounded
.font(.system(.body, design: .monospaced))// SF Mono
```

SF Symbols use equivalent weights, so symbols and adjacent text weight-match precisely at
any size.

## Text styles

Always use semantic text styles. They give you Dynamic Type support, correct leading, and
correct tracking for free.

```swift
Text("Screen title").font(.largeTitle)
Text("Section").font(.title2)
Text("Row label").font(.headline)
Text("Body copy").font(.body)
Text("Metadata").font(.footnote).foregroundStyle(.secondary)
```

Emphasize with symbolic traits rather than switching to a hard-coded weight:

```swift
Text("Important").font(.body).bold()     // SwiftUI
// UIKit: UIFontDescriptor traitBold
```

Adjust leading only when you have a reason:

```swift
Text(longPassage).font(.body).leading(.loose)  // wide columns, long passages
Text(compactRow).font(.body).leading(.tight)   // height-constrained rows, ≤2 lines
```

Never use tight leading for three or more lines.

## iOS / iPadOS Dynamic Type — Large (default)

| Style | Weight | Size (pt) | Leading (pt) | Emphasized weight |
|---|---|---|---|---|
| Large Title | Regular | 34 | 41 | Bold |
| Title 1 | Regular | 28 | 34 | Bold |
| Title 2 | Regular | 22 | 28 | Bold |
| Title 3 | Regular | 20 | 25 | Semibold |
| Headline | Semibold | 17 | 22 | Semibold |
| Body | Regular | 17 | 22 | Semibold |
| Callout | Regular | 16 | 21 | Semibold |
| Subhead | Regular | 15 | 20 | Semibold |
| Footnote | Regular | 13 | 18 | Semibold |
| Caption 1 | Regular | 12 | 16 | Semibold |
| Caption 2 | Regular | 11 | 13 | Semibold |

For reference, the smallest non-accessibility size (xSmall) compresses this to Large Title 31/38
down to Caption 11/13; the accessibility sizes (AX1–AX5) scale Body from 17 pt up past 50 pt.
Download the full Dynamic Type tables for every size from Apple Design Resources rather than
transcribing them.

## Size limits

| Platform | Default | Minimum |
|---|---|---|
| iOS, iPadOS | 17 pt | 11 pt |
| macOS | 13 pt | 10 pt |
| tvOS | 29 pt | 23 pt |
| visionOS | 17 pt | 12 pt |
| watchOS | 16 pt | 12 pt |

## Weight

**Avoid light weights.** Prefer Regular, Medium, Semibold, or Bold. Ultralight, Thin, and
Light are hard to read, especially at small sizes and especially over Liquid Glass.

If you use a custom font with a thin weight, go larger than the recommended minimums.

## Tracking

In a running app the system font adjusts tracking automatically at every point size. You
only need to set tracking manually when producing mockups in a design tool. Representative
SF Pro values (1/1000 em → pt):

| Size (pt) | Tracking (1/1000 em) | Tracking (pt) |
|---|---|---|
| 6 | +41 | +0.24 |
| 8 | +26 | +0.21 |
| 10 | +12 | +0.12 |
| 11 | +6 | +0.06 |

Larger sizes trend toward zero and then slightly negative. Pull the full table from the HIG
Typography specifications when doing precise mockup work.

## Supporting Dynamic Type

Dynamic Type is a system setting; supporting it is not optional.

```swift
@Environment(\.dynamicTypeSize) private var dynamicTypeSize

var body: some View {
    if dynamicTypeSize.isAccessibilitySize {
        VStack(alignment: .leading) { label; value }   // stack when text is huge
    } else {
        HStack { label; Spacer(); value }
    }
}
```

Rules:
- **Verify at every size**, including Larger Accessibility Text Sizes.
- **Minimize truncation.** Aim to show as much useful text at the largest accessibility size
  as at the largest standard size. Let labels use as many lines as needed.
- **Scale meaningful icons with the text.** SF Symbols do this automatically.
- **Reduce columns** as text grows; multicolumn text becomes unreadable at large sizes.
- **Stack instead of inline** when inline items (glyphs, timestamps) start crowding text.
- **Keep the information hierarchy stable** — primary elements stay near the top regardless
  of size.
- Not all content deserves to grow. Tab titles, for instance, don't need to scale with the
  reader's choice for body copy.

## Custom fonts

If you ship a custom font you must implement the behaviors the system fonts give you for
free: Dynamic Type scaling and response to Bold Text.

```swift
Text("Custom")
    .font(.custom("YourFont-Regular", size: 17, relativeTo: .body))
```

Follow the recommended minimum sizes for the style and weight you're using, and test
legibility at the sizes and conditions your users will actually see.

## Legibility over Liquid Glass

- Keep chrome text monochromatic by default; it flips light/dark against what's beneath.
- Text on `.clear` glass needs a dimming layer when the underlying media is bright.
- Use system-defined vibrant colors on standard materials — they stay legible where a
  hand-picked color won't.
- Minimize the number of typefaces. Mixing families obscures hierarchy.
