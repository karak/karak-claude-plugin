# SF Symbols (SF Symbols 7, iOS 26+)

Thousands of configurable symbols that integrate with San Francisco, matching text weight
and size automatically. Use them wherever interface icons appear.

Availability tracks OS version — symbols and features introduced in a given year aren't
available earlier. Since this skill targets iOS 26+, SF Symbols 7 features are fair game.

**Licensing:** SF Symbols may not be used — nor may confusingly similar images — in app
icons, logos, or any trademarked use.

## Basic usage

```swift
Image(systemName: "star.fill")

Label("Favorites", systemImage: "star.fill")

Image(systemName: "gear")
    .font(.system(size: 24, weight: .medium))
    .imageScale(.large)          // .small | .medium (default) | .large
```

Weights map 1:1 to San Francisco weights (ultralight → black), so symbols and adjacent text
weight-match precisely. Scales are defined relative to SF's cap height, letting you adjust a
symbol's emphasis without breaking weight matching.

## Rendering modes

Symbols organize their paths into layers; the rendering mode decides how color maps onto
them.

```swift
Image(systemName: "cloud.sun.rain.fill")
    .symbolRenderingMode(.monochrome)    // one color, all layers
    .symbolRenderingMode(.hierarchical)  // one color, varying opacity per layer
    .symbolRenderingMode(.palette)       // one color per layer
    .symbolRenderingMode(.multicolor)    // intrinsic meaningful colors
    .symbolRenderingMode(nil)            // automatic — the symbol's preferred mode
```

```swift
// Palette needs one color per hierarchy level
Image(systemName: "cloud.sun.rain.fill")
    .symbolRenderingMode(.palette)
    .foregroundStyle(.white, .yellow, .blue)
```

- **Hierarchical** is the go-to for conveying depth and hierarchy inside a symbol.
- **Multicolor** carries semantics — `leaf` is green, `trash.slash` is red.
- Use **system-provided colors** whatever the mode, so symbols adapt to vibrancy, Dark Mode,
  and accessibility settings automatically.
- Verify the chosen mode at the sizes and contrasts you actually ship — legibility varies.

## Gradients (SF Symbols 7)

Generates a smooth linear gradient from a single source color. Works across all rendering
modes, for system and custom colors, and for custom symbols. Renders at any size but looks
best large.

```swift
Image(systemName: "heart.fill")
    .foregroundStyle(.pink)
    .symbolColorRenderingMode(.gradient)   // or .flat
```

## Variable color

Represents a quantity that changes over time — capacity, signal strength, volume — by
coloring layers as a value crosses thresholds between 0 and 1.

```swift
Image(systemName: "speaker.wave.3", variableValue: volume)
```

Use variable color for **change**, never for depth — that's hierarchical rendering's job.
Layers that don't change (the speaker body) opt out.

**SF Symbols 7** adds a draw-based variable value mode:

```swift
Image(systemName: "chart.line.uptrend.xyaxis", variableValue: progress)
    .symbolVariableValueMode(.draw)   // or .color
```

## Design variants

- **Outline** — the most common; matches text. Best in toolbars, lists, and beside text.
- **Fill** — solid interiors. Use for selection and for tab bars.
- **Slash** — unavailable or disabled state.
- **Enclosed** (circle, square, rectangle) — improves legibility at small sizes; combines
  with outline/fill.

```swift
Image(systemName: "heart")
    .symbolVariant(isFavorite ? .fill : .none)
```

Language- and script-specific variants (Latin, Arabic, Hebrew, Hindi, Thai, Chinese,
Japanese, Korean, Cyrillic, Devanagari, and several Indic numeral systems) swap
automatically with the device language.

## Animation

```swift
// State-change effects
Image(systemName: "bell").symbolEffect(.bounce, value: notificationCount)
Image(systemName: "wifi").symbolEffect(.variableColor.iterative)
Image(systemName: "arrow.clockwise").symbolEffect(.rotate, isActive: isRefreshing)

// Content transitions between symbols
Image(systemName: isPlaying ? "pause.fill" : "play.fill")
    .contentTransition(.symbolEffect(.replace))

// SF Symbols 7: Draw animations — the symbol draws itself on/off along its paths
Image(systemName: "checkmark.circle")
    .symbolEffect(.drawOn, isActive: isComplete)
```

`DrawOnSymbolEffect` / `DrawOffSymbolEffect` are iOS 26+.

Use symbol animations to communicate state changes — especially for Control Center controls,
where the symbol may be the only visible element. For a toggle, animate both directions. For
an action with duration, animate indefinitely while it runs and stop on completion.

## Custom symbols

When SF Symbols doesn't have what you need, create a **custom symbol** rather than shipping
a bitmap. Export a template from the SF Symbols app, edit the paths, and keep the layer
structure so rendering modes work.

## Standard action symbols

Use these for common actions so people recognize them instantly.

### Editing
| Action | Symbol |
|---|---|
| Cut | `scissors` |
| Copy | `document.on.document` |
| Paste | `document.on.clipboard` |
| Done | `checkmark` |
| Cancel / Close | `xmark` |
| Delete | `trash` |
| Undo | `arrow.uturn.backward` |
| Redo | `arrow.uturn.forward` |
| Compose | `square.and.pencil` |
| Duplicate | `plus.square.on.square` |
| Rename | `pencil` |
| Move to / Folder | `folder` |
| Attach | `paperclip` |
| Add | `plus` |
| More | `ellipsis` |

### Selection
| Action | Symbol |
|---|---|
| Select | `checkmark.circle` |
| Deselect | `xmark` |

### Text formatting
| Action | Symbol |
|---|---|
| Bold | `bold` |
| Italic | `italic` |
| Underline | `underline` |
| Superscript | `textformat.superscript` |
| Subscript | `textformat.subscript` |
| Align left | `text.alignleft` |
| Center | `text.aligncenter` |
| Justified | `text.justify` |
| Align right | `text.alignright` |

### Search
| Action | Symbol |
|---|---|
| Search | `magnifyingglass` |
| Find | `text.page.badge.magnifyingglass` |
| Filter | `line.3.horizontal.decrease` |

### Sharing
| Action | Symbol |
|---|---|
| Share | `square.and.arrow.up` |
| Print | `printer` |

### Accounts
| Action | Symbol |
|---|---|
| Account | `person.crop.circle` |

For menu items performing standard actions (Cut, Copy, Paste), use the **standard selector**
— the system picks the icon from it, so you get the right symbol with no extra code.

## Rules

- **Always supply an accessibility label**, even when a text label is visible — people using
  VoiceOver or Voice Control need it.
- **Prefer filled variants in tab bars** for platform consistency.
- **No borders in toolbars.** Outlined-circle-style symbols are redundant; the section
  already provides a container.
- **Don't mix text and symbols** across toolbar items that share a background.
- Symbols scale with Dynamic Type automatically — let them.
