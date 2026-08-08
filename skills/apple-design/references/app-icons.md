# App Icons (iOS 26+)

App icons are no longer flat images. They are **layered** artifacts that the system lights,
blurs, refracts, and masks at runtime, picking up Liquid Glass attributes — specular
highlights, refraction, translucency — that adapt to icon size and to the system version.

If your app still ships a single flattened 1024×1024 PNG, that's the highest-leverage
visual fix available.

## The pipeline

1. **Design layers** in your tool of choice — foreground, middle, background.
2. **Export** them (prefer vector: SVG or PDF; PNG for mesh gradients and raster artwork).
3. **Compose in Icon Composer** — the app bundled with Xcode and downloadable from Apple
   Design Resources. There you define the background, group layers, adjust opacity and
   Liquid Glass attributes, annotate the appearance variants, preview across system
   versions, and export for Xcode.

iOS, iPadOS, macOS, and watchOS all use this pipeline. tvOS and visionOS instead use an
image stack in an Xcode asset catalog.

## Layer design

- **Split by depth.** Decide which elements read as foreground, middle, and background, then
  separate them. Photos, for instance, splits its centerpiece into multiple translucent
  layers.
- **Clearly defined edges.** Avoid soft or feathered edges on foreground shapes — the
  system-drawn highlights and shadows depend on crisp edges.
- **Vary opacity across foreground layers** to build depth. Import fully opaque layers and
  adjust transparency inside Icon Composer so you can see how it interacts with system
  effects.
- **Background:** a solid color or gradient is usually right, and Icon Composer can generate
  it — you rarely need to import one. If you do, make it full-bleed and opaque. Verify any
  gradient responds well to system lighting.
- **Convert text to outlines** and outline all artwork.
- **Group layers** in Icon Composer when you want an effect applied to several at once;
  groups expose extra Liquid Glass controls (specular highlights, refraction, translucency).

## Shape and masking

- iOS, iPadOS, macOS: **square** layers; the system applies rounded-rectangle masking
  concentric with system UI and the device bezel.
- watchOS and visionOS: **square** layers; the system applies **circular** masking.
- tvOS: **rectangular** layers.

**Supply unmasked layers.** Pre-masking your artwork degrades specular highlights and
produces jagged edges.

**Keep primary content centered** to survive masking and corner adjustment — especially for
circular masks. Use the production grids from Apple Design Resources.

Irregularly shaped icons receive a system-provided background.

## Let the system do the effects

Do **not** bake in:
- specular highlights
- drop shadows between layers
- beveled edges
- blurs
- glows

These are applied dynamically by the system and are adapted per size, per appearance, and
per OS version. Static versions of the same effects collide with the dynamic ones. If you do
include a custom effect deliberately, test it in Icon Composer and on a real device.

## Appearance variants

People choose **default (light), dark, clear, or tinted** Home Screen icons. You can design
each; the system generates any you don't supply.

- **Keep core features consistent** across all four. Don't swap elements per variant —
  people lose track of your app.
- **Base the dark variant on the light one**, with complementary colors. Avoid excessively
  bright imagery; colored backgrounds give the best contrast in dark icons.
- Dark is more subdued; clear and tinted more so still. Every variant must remain visible,
  legible, and recognizable.
- Design them to sit comfortably next to system icons and widgets.

## Design guidance

- **Simplicity wins.** Fine details look busy under system shadows and highlights and
  disappear at small sizes. Find the one idea that captures the app and express it with a
  minimal number of shapes.
- **Filled, overlapping shapes** with transparency and blur give a good sense of depth.
- **Consistent across platforms.** One recognizable design everywhere so people don't
  mistake your app for several apps.
- **Text only when essential.** It doesn't localize, doesn't support accessibility, is often
  unreadable, and your app's name usually appears right next to the icon anyway. A single
  mnemonic letter can be fine; "Watch", "Play", "New" are not.
- **Illustrate, don't photograph.** Photos carry detail that breaks across appearances,
  small sizes, and layer separation.
- **Don't replicate UI components** or use screenshots.
- **No Apple hardware replicas** — they're copyrighted.
- **Avoid extremely thin lines and sharp corners** — they lose crispness at small sizes.
- **Never use SF Symbols** (or confusingly similar artwork) in an app icon. It's prohibited
  by the SF Symbols license.

## Alternate icons

iOS, iPadOS, tvOS, and compatible apps in visionOS can offer alternate icons selectable from
your app's settings — team colors, seasonal variants, and so on.

- Each alternate needs its **own dark, clear, and tinted variants**.
- Every icon must stay closely related to your app's content and experience.
- All of them are subject to App Review.
