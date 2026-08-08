# Accessibility (iOS 26+)

Liquid Glass raises the stakes: translucency, lensing, and fluid morphing are exactly the
things that break for people with low vision, motion sensitivity, or attention differences.
Apple's answer is a set of system settings that modify or remove those effects. Standard
components respond automatically. **Anything custom you build will not, unless you check.**

An accessible interface is *intuitive* (familiar, consistent interactions), *perceivable*
(no single required sense), and *adaptable* (respects system settings and personalization).

Use **Accessibility Inspector** to audit, and publish **Accessibility Nutrition Labels** in
App Store Connect to declare what you support.

## Settings that change Liquid Glass

Test with each of these on:

| Setting | What it does | What to check |
|---|---|---|
| **Reduce Transparency** | Makes materials more opaque | Custom glass and any text you placed over it |
| **Increase Contrast** | Amplifies color differences, strengthens borders | That your custom colors have increased-contrast variants |
| **Reduce Motion** | Removes or damps fluid morphing and large animations | Every custom animation, parallax, and glass transition |
| **Liquid Glass appearance preference** | User-selected look for the material | Custom glass in both settings |
| **Dark Mode** | Appearance switch | All custom colors and assets |
| **Bold Text** | Heavier system font | Custom fonts must respond too |
| **Larger Text (Dynamic Type)** | Scales text, incl. accessibility sizes | Layout at every size |

## Vision

### Text size

Aim to let people enlarge text by at least **200%**. Adopt Dynamic Type; if you use custom
type styles, follow the platform default and minimum sizes.

| Platform | Default | Minimum |
|---|---|---|
| iOS, iPadOS | 17 pt | 11 pt |
| macOS | 13 pt | 10 pt |
| tvOS | 29 pt | 23 pt |
| visionOS | 17 pt | 12 pt |
| watchOS | 16 pt | 12 pt |

Thin weights need to be larger than these minimums to stay legible.

### Contrast

WCAG Level AA, as used by Accessibility Inspector:

| Text size | Weight | Minimum ratio |
|---|---|---|
| Up to 17 pt | All | 4.5:1 |
| 18 pt | All | 3:1 |
| Any | Bold | 3:1 |

Check both light and dark. If the default palette can't meet these, at minimum ship a
higher-contrast scheme that activates with Increase Contrast.

### Color

- **Never convey information by color alone.** Add shape, icon, or text. Red-green and
  blue-orange are the classic failures.
- **Prefer system colors** — they carry accessible variants that adapt automatically.
- Consider letting people customize chart colors or similar palettes.

### VoiceOver

```swift
Image(systemName: "star.fill")
    .accessibilityLabel("Favorite")

Button {
    toggleFavorite()
} label: {
    Image(systemName: isFavorite ? "heart.fill" : "heart")
}
.accessibilityLabel(isFavorite ? "Remove from favorites" : "Add to favorites")

// Collapse a decorative composite into one element
HStack { avatar; name; subtitle }
    .accessibilityElement(children: .combine)
    .accessibilityAddTraits(.isButton)
```

**Every icon needs an accessibility label**, whether or not a text label is visible — that's
how people using VoiceOver or Voice Control opt into the text.

Include a grabber on resizable sheets: it's the VoiceOver-accessible way to resize.

## Hearing

- Provide **captions** (synchronized text for audio content), **subtitles** (live dialogue in
  the person's language), **audio descriptions** (spoken narration of visual-only
  information), and **transcripts** (complete textual description, good for long-form).
- Let people customize how that text is presented.
- **Pair audio cues with haptics** — success chimes, error sounds, game feedback.
- **Pair audio cues with visual cues**, especially where the relevant thing is offscreen.

## Mobility

| Platform | Default control size | Minimum |
|---|---|---|
| iOS, iPadOS | 44×44 pt | 28×28 pt |

Target 44×44 pt. Treat 28×28 pt as an absolute floor, not a design goal.

```swift
Button { action() } label: {
    Image(systemName: "plus")
        .font(.system(size: 20))
}
.frame(minWidth: 44, minHeight: 44)
```

Also:
- Provide enough space *around* controls so people can distinguish and hit them.
- Every gesture needs a visible affordance and a non-gesture alternative.
- Support Switch Control and Assistive Access where relevant (`AssistiveAccess` scene
  support is available in SwiftUI).

## Dynamic Type layout

```swift
@Environment(\.dynamicTypeSize) private var dynamicTypeSize

var body: some View {
    if dynamicTypeSize.isAccessibilitySize {
        VStack(alignment: .leading) { label; value }
    } else {
        HStack { label; Spacer(); value }
    }
}
```

- Minimize truncation as size grows; let labels use as many lines as they need.
- Reduce column count at large sizes.
- Scale meaningful icons with the text — SF Symbols do this for you.
- Keep the information hierarchy stable: primary elements stay near the top.
- Not everything should scale. Tab titles, for example, don't need to.

## Reduce Motion

```swift
@Environment(\.accessibilityReduceMotion) private var reduceMotion

withAnimation(reduceMotion ? nil : .snappy) { expand() }
```

Applies to parallax, zoom, large-area movement, and any custom glass morphing you author.

## Audit checklist

- [ ] Every interactive element has a label; images that convey meaning have labels
- [ ] Decorative images are hidden from assistive technology
- [ ] Contrast meets 4.5:1 / 3:1 in both light and dark
- [ ] Nothing depends on color alone
- [ ] All hit targets ≥ 44×44 pt
- [ ] Layout verified at every Dynamic Type size including accessibility sizes
- [ ] Verified with Reduce Transparency, Increase Contrast, Reduce Motion, Bold Text
- [ ] Custom animations respect Reduce Motion
- [ ] Custom colors define light, dark, and increased-contrast variants
- [ ] Every gesture has a visible affordance and a non-gesture alternative
- [ ] Media has captions/subtitles/transcripts as appropriate
- [ ] Audio cues paired with haptics and visual cues
- [ ] Accessibility Inspector run clean
