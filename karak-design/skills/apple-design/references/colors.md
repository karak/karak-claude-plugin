# Color (iOS 26+)

## Never hard-code system colors

Documented system color values are for design-time reference only. Actual values shift
between releases and with environmental variables. Always reach them through the API.

```swift
Color.blue          // not #007AFF
Color(.systemGray3)
Color.accentColor
```

## Semantic foreground colors

| Purpose | SwiftUI | UIKit |
|---|---|---|
| Primary text | `Color.primary` | `label` |
| Secondary text | `Color.secondary` | `secondaryLabel` |
| Tertiary text | `Color(.tertiaryLabel)` | `tertiaryLabel` |
| Quaternary text | `Color(.quaternaryLabel)` | `quaternaryLabel` |
| Placeholder | `Color(.placeholderText)` | `placeholderText` |
| Separator (translucent) | `Color(.separator)` | `separator` |
| Separator (opaque) | `Color(.opaqueSeparator)` | `opaqueSeparator` |
| Link | `Color(.link)` | `link` |

Don't repurpose these. Separator color is not a text color; secondary label is not a
background.

## Background colors

Two sets, each with primary / secondary / tertiary variants:

```swift
// Use the plain set for ungrouped views
Color(.systemBackground)
Color(.secondarySystemBackground)
Color(.tertiarySystemBackground)

// Use the grouped set with grouped table views / forms
Color(.systemGroupedBackground)
Color(.secondarySystemGroupedBackground)
Color(.tertiarySystemGroupedBackground)
```

Hierarchy convention:
- **Primary** — the overall view
- **Secondary** — grouping content within the overall view
- **Tertiary** — grouping content within secondary elements

## System colors

`red`, `orange`, `yellow`, `green`, `mint`, `teal`, `cyan`, `blue`, `indigo`, `purple`,
`pink`, `brown` — each defines light, dark, and increased-contrast variants.

Grays are UIKit-side: `systemGray` through `systemGray6`. In SwiftUI, `Color.gray` is the
equivalent of `systemGray`.

## Liquid Glass color

By default **Liquid Glass has no inherent color** — it takes color from whatever is directly
behind it. You can tint some glass elements to get the look of stained glass.

The rules:

**Apply color sparingly.** Reserve it for elements that genuinely benefit from emphasis:
status indicators and the primary action.

**Emphasize by tinting the background, not the label.** The system does exactly this for
prominent buttons — the app accent color goes on the button's background, not on its title.
Don't tint the background of multiple controls in the same view.

**Small elements go monochromatic.** Tab bars and toolbars adapt between light and dark
appearance based on the content beneath; their symbols and text follow a monochromatic
scheme — darker over light content, lighter over dark. Larger elements like sidebars render
more opaque to preserve legibility over complex backgrounds.

**Colorful content ⇒ monochromatic chrome.** If your content layer is bright and colorful,
keep toolbars and tab bars monochromatic, or pick an accent color with real visual
separation. Conversely, if your content is largely monochromatic, your brand color makes a
strong accent color.

**Mind the overlap.** Check the *resting* state — the top of a scroll — for similar colors
colliding between the content layer and controls above it. Transient overlap while scrolling
is acceptable; a bad default state is not.

## Accent color

Set an app accent color in the asset catalog. It drives prominent buttons, selection, and
sidebar icons. Choose a color that reads against both light and dark content and that
doesn't collide with your content layer.

## Custom colors

Every custom color must define:
1. A light variant
2. A dark variant
3. An increased-contrast option for **each** of those

This holds even if the app ships in a single appearance mode — Liquid Glass adapts in both
directions and needs both definitions.

Define them in the asset catalog, not in code, so the system resolves them per context.

## Inclusive color

- **Never convey information by color alone.** Pair it with text, shape, or a symbol.
  Red-green and blue-orange pairings are the common failures.
- Check contrast: **4.5:1** for text up to 17 pt, **3:1** for 18 pt+ or bold at any size.
- If the default palette can't hit those numbers, at minimum ship a higher-contrast scheme
  that activates with Increase Contrast.
- Check contrast in **both** light and dark.
- Consider cultural connotations — red is danger in some cultures, fortune in others.

## Color management

- Apply color profiles to images. sRGB is accurate on most displays.
- Use **Display P3 at 16 bits per channel, exported as PNG** for wide-color assets. P3
  colors generally look fine on sRGB displays, but very similar P3 colors can become
  indistinguishable and P3 gradients can clip — ship per-color-space variants in the asset
  catalog when that matters.
- Test under varied lighting: colors look darker and more muted in bright surroundings,
  brighter and more saturated in the dark.
- Test on devices with True Tone.

## Dark Mode

Use semantic colors and it mostly works. Beyond that:
- Test every custom color and asset in both appearances.
- Don't assume "dark mode = invert". Elevated surfaces get *lighter*, not darker.
- Provide dark variants for app icons (see `app-icons.md`).
