# How Real Apps Solve These Problems

Case studies to reason from when you're deciding *where* something goes. Two tiers of
evidence, kept separate on purpose:

- **[HIG]** — the example is cited in Apple's Human Interface Guidelines or developer
  documentation. Treat as canonical.
- **[press]** — reported by Apple newsroom or credible trade press covering the iOS 26
  redesign and Apple's Liquid Glass Design Gallery. Directionally useful; verify in the app
  before copying.

## Search placement — the clearest worked example

Apple's own apps split three ways, and the HIG explains why each one chose what it did.

| App | Placement | Why |
|---|---|---|
| **Settings** [HIG] | Bottom toolbar, **sole item** | Search is the primary way people navigate a huge flat hierarchy |
| **Mail**, **Notes** [HIG] | Bottom toolbar, **alongside other controls** | Search matters but shares priority with compose and organize actions |
| **Wallet** [HIG] | **Top** toolbar | Event passes stack at the bottom of the screen; covering them would break the app's main job |
| **Apple TV** [HIG] | **Search tab**, standard style | Search doubles as a browse surface — genres and categories ground people before they type |
| **Music** [HIG] | Search tab **plus** an inline field in Library | Global search is a destination; the library filter is scoped to that view, so it lives with the content |
| **Freeform** [HIG] | Toolbar (iPad/Mac) | Results appear in the detail view below, so the toolbar keeps both visible |
| **Notes**, **Mail** on iPad [HIG] | Above the content-list column when compact | Keeps search attached to the list it searches as the window narrows |

**The rule to extract:** search goes where it *belongs to* — the bottom when it's a primary
action, a tab when it's a destination, inline when it's scoped to one view's content, the
top only when the bottom is spoken for.

## Tab bars

**Clock** [HIG] — Alarm, Stopwatch, Timer. The HIG's canonical example of a tab bar doing
one job: navigating top-level sections, nothing else.

**Music** [HIG] — the reference implementation of the two new iOS 26 tab bar features at
once: the MiniPlayer rides as a **bottom accessory** and moves inline with the tab bar when
it minimizes on scroll. If you have a persistent now-playing / active-session UI, this is
the pattern.

**Music on iPad** [HIG] — lets people pin a favorite playlist *into* the tab bar. Tab
customization is worth it when your app has more sections than fit and people's priorities
differ.

**Photos** [press] — split into Library and Collections tabs in the redesign, with a fully
transparent floating tab bar over the grid.

**Sequel** [press] — added a tab bar to nearly every screen, fixing a long-standing lack of
quick access to core sections. Worth noting: the redesign was an excuse to fix *navigation
architecture*, not just material.

## Content-first chrome

**Safari** [press] — pages flow from the top edge to the bottom of the screen with the
address bar as a floating capsule, so more of the page is visible while refresh and search
stay reachable. The clearest demonstration of "content layer extends everywhere, functional
layer floats."

**Camera** [press] — hid the lesser-used shooting modes to simplify a cramped layout, with
controls in the glass layer over a live viewfinder. This is the `.clear` variant's home
territory: media underneath must stay prominent.

**Crumbl** [press] — moved its signature pink out of the top toolbar and **into the content
layer**, letting the toolbar go monochromatic so brand photography carries the identity.
This is the single most transferable third-party lesson: when Liquid Glass takes the chrome,
your brand color moves to the content.

**Lock Screen / Home Screen** [press] — the clock expands and contracts to fit behind the
wallpaper subject; icons and widgets are built from multiple glass layers. Both are the
system demonstrating that glass reacts to what's behind it rather than sitting on top of it.

## Toolbars

**Keynote** [HIG] — groups toolbar items by function: presentation-level commands, playback
commands, object insertion. Three groups, each coherent. Matches the HIG's "aim for a
maximum of three" guidance.

**Notes** [HIG] — doesn't title the current note when a single window is open, because the
first line of content already provides context; titles appear only when multiple notes are
open in separate windows so people can tell them apart. A reminder that "always show a
title" is not the rule — "always let people confirm where they are" is.

**Safari (macOS)** [HIG] — AutoFill Edit buttons end in an ellipsis because they open
another view. The ellipsis convention still applies.

## Sheets and modality

**Notes** [HIG] — uses a **nonmodal** sheet for text formatting, so people keep editing the
note while the sheet is up. Use nonmodal when the sheet's whole purpose is to act on the
parent view.

**Notes format sheet** [HIG] — rounded bottom corners **concentric with the device**, fixed
radius on top. The concrete example Apple gives for `ConcentricRectangle`.

**Messages and Mail compose** [HIG] — full height only, no medium detent, because creating
content needs the room. Contrast with the share sheet, which puts the most relevant items in
the medium detent and lets people expand for more.

## Color and sidebars

**Maps** [HIG] — light color scheme in map mode, dark in satellite mode. Artwork and
translucency below can force color changes above; check both.

**Mail** [HIG] — the VIP sidebar icon uses a fixed yellow instead of the app accent color,
because the color carries meaning. A legitimate exception to "sidebar icons follow the
accent color" — but note it's *one* icon, used sparingly.

**Weather** [HIG] — page control for saved locations, with the scroll indicator suppressed
on the same axis so people don't see two redundant position indicators.

## App icons

**Photos** [HIG] — separates its centerpiece into multiple layers containing translucent
pieces, so system lighting produces real depth. The model for "vary opacity in foreground
layers."

**Design Gallery third parties** [press] — AllTrails, Carrot Weather, Fantastical, Trello,
Kroger, Le Monde, SketchPro, CNN, OmniFocus 4, Photoroom, American Airlines, Lowe's, LTK,
Sky Guide, Lumy, Tide Guide, CardPointers, Linearity, Essayist, Lucid Motors, GrowPal.
Apple's own curated set of apps that rebuilt around native controls. Useful as a sampler of
how the same visual system reads across very different categories — outdoors, weather,
productivity, news, retail, automotive.

Be honest about what the gallery is: roughly a dozen apps out of millions, selected because
those teams had the resources and incentive to rebuild. It shows what good adoption looks
like, not what typical adoption looks like.

## What went wrong in the field

Worth knowing, because these are the failure modes reviewers will find in your app too.

**Lensing and legibility** [press] — the most contested aspect of Liquid Glass through 2025.
Refraction at glass edges over busy content made text hard to read, and Apple damped the
effect over the course of the beta and subsequent releases. The design lesson stands: the
material is only as legible as what you put behind it. Restraint, spacing, and `.regular`
over `.clear` are the fixes.

**Icons reading as "crooked"** [press] — users reported layered icons looking misaligned
after the redesign, generally traceable to artwork that wasn't optically centered against
the new grid. Preview against the updated grids from Apple Design Resources rather than
trusting your old 1024 master.

**Glass in the content layer** [press] — the recurring third-party mistake. Apps that put
glass on cards, rows, and decorative chrome end up with stacked translucency and collapsed
contrast. The material is correct; the architecture underneath it isn't.

## Using this file

When you're stuck on a placement decision, find the closest analogue above and ask what
constraint drove it. Most of these choices come from one of three questions:

1. **What is this screen's primary job?** (Wallet's passes; Messages' compose room)
2. **What does this element belong to — content or navigation?** (Music's scoped library
   filter vs. its global search tab)
3. **What's underneath?** (Camera's viewfinder; Crumbl's photography)
