# Liquid Glass

The dynamic material introduced in iOS 26 that forms the functional layer above content.
It blurs what's behind it, reflects surrounding color and light, refracts at its edges, and
reacts to touch and pointer input in real time.

## Where it belongs

Liquid Glass forms a **distinct functional layer** for controls and navigation — tab bars,
toolbars, sidebars, floating buttons — that hovers above the content layer. Content scrolls
and peeks through from beneath, which is what gives the interface its depth.

**Do not use Liquid Glass in the content layer.** Use standard materials there
(`.ultraThin`, `.thin`, `.regular`, `.thick`) plus vibrant label/fill/separator colors.
Glass in the content layer produces unnecessary complexity and a confusing hierarchy, and
glass cannot sample other glass — stacking it destroys contrast.

Sanctioned exception: a content-layer control with a transient interactive element (a
`Slider` knob, a `Toggle` thumb) adopts a Liquid Glass appearance while being manipulated.
The system handles this; you don't apply it.

**Use it sparingly on custom controls.** Standard components adopt it automatically. Custom
glass should be reserved for the most important functional elements — realistically one or
two per screen. Overuse distracts from the content the material exists to showcase, and
degrades rendering performance.

## The two variants

### `.regular` — the default

Blurs and adjusts the luminosity of background content to keep foreground text legible.
Most system components use it. Scroll edge effects further enhance legibility by blurring
and reducing the opacity of content passing beneath.

Use `.regular` when:
- The background might create legibility issues
- The component carries a significant amount of text — alerts, sidebars, popovers

### `.clear` — for media

Highly translucent. Prioritizes visibility of the underlying content so visually rich
backgrounds stay prominent. Use for components floating over photos and video, to create a
more immersive experience.

Dimming rules for `.clear`:
- **Bright underlying content** → add a dark dimming layer at **35% opacity**
- **Sufficiently dark content**, or standard AVKit playback controls (which supply their
  own dimming) → no dimming layer needed

Both variants change appearance in response to the user's preferred Liquid Glass look and
to Reduce Transparency / Increase Contrast.

## SwiftUI API

All of the following are iOS 26.0+.

### Applying an effect

```swift
// Default: regular variant, Capsule shape
Text("Hello, World!")
    .font(.title)
    .padding()
    .glassEffect()

// Alternate shape — use a rounded rect for larger components
// that would look odd as a capsule
Text("Hello, World!")
    .font(.title)
    .padding()
    .glassEffect(in: .rect(cornerRadius: 16.0))

// Tinted for prominence, and reactive to touch/pointer
Text("Hello, World!")
    .font(.title)
    .padding()
    .glassEffect(.regular.tint(.orange).interactive())
```

`Glass` configuration methods: `.regular`, `.clear`, `.tint(_:)`, `.interactive(_:)`.

Apply `.glassEffect(_:in:)` **after** other modifiers that affect the view's appearance —
the modifier captures the content to hand to the container for rendering.

### Combining multiple effects

Wrap multiple glass views in a `GlassEffectContainer`. This is required for good rendering
performance and it lets the shapes blend and morph into each other.

```swift
GlassEffectContainer(spacing: 40.0) {
    HStack(spacing: 40.0) {
        Image(systemName: "scribble.variable")
            .frame(width: 80.0, height: 80.0)
            .font(.system(size: 36))
            .glassEffect()

        Image(systemName: "eraser.fill")
            .frame(width: 80.0, height: 80.0)
            .font(.system(size: 36))
            .glassEffect()
    }
}
```

**Spacing is the tuning knob.** The larger the container's `spacing`, the sooner the
effects behind views blend together and merge during a transition. A container spacing
*larger* than the interior stack's spacing makes shapes blend while at rest — usually not
what you want unless the merge is deliberate.

To make several views contribute to a single glass capsule even at rest — useful for
dynamically created views or views outside a layout container — use
`glassEffectUnion(id:namespace:)`:

```swift
GlassEffectContainer(spacing: 20.0) {
    HStack(spacing: 20.0) {
        ForEach(symbolSet.indices, id: \.self) { item in
            Image(systemName: symbolSet[item])
                .frame(width: 80.0, height: 80.0)
                .font(.system(size: 36))
                .glassEffect()
                .glassEffectUnion(id: item < 2 ? "1" : "2", namespace: namespace)
        }
    }
}
```

### Morphing during transitions

Give each effect a stable identity with `glassEffectID(_:in:)` inside a `@Namespace`, so
SwiftUI animates the right shapes as views come and go.

```swift
@State private var isExpanded = false
@Namespace private var namespace

var body: some View {
    GlassEffectContainer(spacing: 40.0) {
        HStack(spacing: 40.0) {
            Image(systemName: "scribble.variable")
                .frame(width: 80.0, height: 80.0)
                .font(.system(size: 36))
                .glassEffect()
                .glassEffectID("pencil", in: namespace)

            if isExpanded {
                Image(systemName: "eraser.fill")
                    .frame(width: 80.0, height: 80.0)
                    .font(.system(size: 36))
                    .glassEffect()
                    .glassEffectID("eraser", in: namespace)
            }
        }
    }

    Button("Toggle") {
        withAnimation { isExpanded.toggle() }
    }
    .buttonStyle(.glass)
}
```

`GlassEffectTransition` picks the transition style via `glassEffectTransition(_:)`:
- `.matchedGeometry` — the default for effects positioned within the container's spacing
- `.materialize` — for effects farther apart than the container's spacing, or when you want
  a simpler/custom transition

Use these two consistently across your app so the experience stays predictable. Both
modifiers only take effect during view-hierarchy transitions or animations.

### Button styles

Prefer these over hand-rolling glass on a button.

```swift
Button("Continue") { }.buttonStyle(.glass)
Button("Done") { }.buttonStyle(.glassProminent)
```

UIKit equivalents: `.glass()`, `.prominentGlass()`, `.clearGlass()`, `.prominentClearGlass()`.
AppKit: `NSButton.BezelStyle.glass`.

## Scroll edge effects

A scroll edge effect provides visual separation between floating interface elements and the
content scrolling behind them. System bars adopt it by default.

```swift
ScrollView { content }
    .scrollEdgeEffectStyle(.hard, for: .top)   // .automatic | .soft | .hard
```

Rules:
- **Prefer `.automatic`.** It gives a more opaque separation for top toolbars with many
  controls, text outside glass controls, and pinned table headers.
- If you choose `.soft`, test thoroughly — legibility is on you.
- **Not decorative.** They are not overlays and don't darken content; they exist so controls
  stay distinct. Only apply one where a scroll view actually sits behind floating elements.
- **One effect per view.** In split views each pane may have its own, but keep their heights
  consistent so they align.
- Hide one where it doesn't apply with `scrollEdgeEffectHidden(_:for:)`.

For custom bars containing controls, text, or icons with content scrolling beneath, register
them with `safeAreaBar(edge:alignment:spacing:content:)` (UIKit:
`UIScrollEdgeElementContainerInteraction`).

## Background extension effect

Creates the impression of content stretching beneath a sidebar or inspector — it mirrors
adjacent content and blurs it to keep the sidebar legible. Ideal for edge-to-edge hero
images in split-view layouts.

```swift
HeroImage()
    .backgroundExtensionEffect()
```

UIKit: `UIBackgroundExtensionView`. AppKit: `NSBackgroundExtensionView`.

## Concentric shapes

Hardware curvature informs the curvature of controls, sheets, popovers, and windows.
`ConcentricRectangle` computes each corner's radius relative to its container, so shapes
adapt across devices without hard-coded values.

```swift
// Every corner concentric with the container shape
ConcentricRectangle()
    .fill(Color.green)
    .padding(8.0)
    .ignoresSafeArea()

// Guarantee rounding even when the computed radius would be 0
ConcentricRectangle(corners: .concentric(minimum: 12))
```

System views supply container shapes automatically. In a custom container, declare one with
`containerShape(_:)` using a `RoundedRectangularShape` (`Circle`, `Rectangle`,
`RoundedRectangle`, `Capsule`). Corner styles come from `Edge.Corner.Style`: concentric,
concentric with a minimum, fixed radius, or squared.

UIKit: `cornerConfiguration`.

## Migration checklist

Build with the latest SDK and run on iOS 26+; standard components update themselves. Then
work through this list.

**Remove**
- [ ] Custom backgrounds and appearance overrides on tab bars, toolbars, split views
- [ ] Visual-effect views added to popover and sheet content
- [ ] Hard-coded layout metrics on standard controls (sizes and shapes changed)
- [ ] Hard-coded corner radii near screen or container edges
- [ ] Any `if #available` branches for pre-26 — this skill targets iOS 26+ only

**Fix**
- [ ] Hiding a toolbar item's *content* instead of the item itself (`hidden(_:)` / `isHidden`
      on the item) — otherwise you get an empty glass pill
- [ ] Section headers still written in ALL CAPS; the system now renders title case
- [ ] Crowded or overlapping controls; prefer standard spacing metrics
- [ ] Content that stops short of screen edges
- [ ] Sheet content sitting too close to the now-larger corner radius
- [ ] Action sheets not anchored to their source view/item

**Adopt**
- [ ] `Tab(role: .search)` for a search tab
- [ ] `tabBarMinimizeBehavior(.onScrollDown)` where content should take over on scroll
- [ ] `ToolbarSpacer` between text-labeled toolbar buttons
- [ ] `backgroundExtensionEffect()` where content doesn't span the full window
- [ ] `.glass` / `.glassProminent` button styles instead of custom glass
- [ ] `sidebarAdaptable` tab style on iPad instead of choosing tabs *or* sidebar
- [ ] `Form` with `.grouped` style to pick up the new layout metrics

**Verify**
- [ ] Reduce Transparency, Increase Contrast, Reduce Motion
- [ ] Light and dark, plus the user's Liquid Glass appearance preference
- [ ] All Dynamic Type sizes including accessibility sizes
- [ ] Profile rendering performance — glass is not free

## Known pitfalls

- **Glass on glass.** Stacking glass surfaces (tab bar + glass card + glass sheet) collapses
  contrast. Glass cannot sample glass.
- **Busy backgrounds.** Photographic or high-frequency content behind a control punishes
  translucency. Fix with spacing, restraint, and `.regular` over `.clear`.
- **Too many containers.** Creating many `GlassEffectContainer`s, or applying many effects
  outside a container, degrades performance. Consolidate.
- **Hit testing.** Custom glass views can behave unexpectedly under hit testing; verify tap
  targets on any custom glass control rather than assuming.
- **Color on color.** Colored labels on glass over colorful content read poorly. Keep chrome
  monochromatic when the content layer is colorful.
