---
name: apple-design
description: "Design iOS/iPadOS interfaces for the Liquid Glass era (iOS 26+) following Apple's Human Interface Guidelines. Use when creating or reviewing SwiftUI views and app screens, structuring navigation (tab bars, toolbars, sidebars, search), applying Liquid Glass material and glassEffect APIs, choosing semantic colors and Dynamic Type styles, designing app icons with Icon Composer, or auditing an interface for HIG conformance and accessibility. Targets iOS 26 and later only — no backward-compatibility fallbacks."
---

# Apple Design Skill (iOS 26+ / Liquid Glass)

Design iOS and iPadOS interfaces that feel native in the Liquid Glass design language
introduced in iOS 26 — the largest visual redesign since iOS 7.

**Target: iOS 26 and later. Do not write `if #available` fallbacks, `UIDesignRequiresCompatibility`,
or pre-26 alternatives unless the user explicitly asks for them.**

Verified against Apple's Human Interface Guidelines and the SwiftUI/UIKit reference as of
August 2026 (HIG pages current through the June 8, 2026 revision). Every API named in this
skill is checked against Apple's documentation for its introduced-in version.

## When to Use

- Creating or reviewing SwiftUI views, screens, and navigation structure
- Deciding where Liquid Glass belongs — and where it must not go
- Choosing colors, typography, spacing, symbols, and motion
- Designing app icons for the layered Icon Composer pipeline
- Auditing an interface for HIG conformance, legibility, and accessibility
- Migrating an app that still looks like iOS 18

## The one idea that governs everything: two layers

iOS 26 splits every screen into two planes.

| | Content layer | Functional layer |
|---|---|---|
| What lives here | Your content: text, media, lists, rows, cards, backgrounds | Navigation and controls: tab bars, toolbars, sidebars, floating buttons |
| Material | Opaque backgrounds and **standard** materials (`.ultraThin` … `.thick`) | **Liquid Glass** |
| Behavior | Scrolls, extends edge to edge, passes under the functional layer | Floats above content, adapts its appearance to whatever scrolls beneath |
| Color | Where your brand color belongs | Monochromatic by default; color only for the single primary action |

**Never put Liquid Glass in the content layer.** It is the single most common mistake.
Glass on cards, list rows, and section backgrounds produces a "blur pile": glass cannot
sample other glass, contrast collapses, and the visual hierarchy stops reading. Use
standard materials there instead.

The one sanctioned exception: a control that sits in the content layer and has a
transient interactive element — a `Slider` knob, a `Toggle` thumb — takes on a Liquid
Glass appearance *while the person is manipulating it*. The system does this for you.

If an app's architecture mixes the two layers (controls inside list rows, navigation bars
treated as content, decorative chrome on cards), adopting Liquid Glass will make it look
worse, not better. Fix the layering first.

## Working rules

**1. Let the system do it.** Standard components from SwiftUI and UIKit pick up Liquid
Glass, scroll edge effects, minimize-on-scroll, concentric corners, and adaptive appearance
for free. Custom glass is opt-in complexity — reach for it only for the one or two most
important custom controls in the app.

**2. Delete your custom bar backgrounds.** Custom backgrounds on tab bars, toolbars, split
views, sheets, and popovers now fight the material and the scroll edge effect. Removing
them is usually the single biggest win when migrating an app.

**3. Extend content to every edge.** Backgrounds, artwork, and scroll views must reach the
top, bottom, and sides. Content is *supposed* to pass beneath the floating bars — that
peek-through is what makes the material read as glass. Use `backgroundExtensionEffect()`
where content doesn't span the full window.

**4. Be monochromatic in the chrome.** Toolbars and tab bars default to a monochromatic
appearance that flips light/dark based on what's underneath. Apply color to at most one
prominent action per view, and apply it to the *background* of that control, not to its
label. Brand color belongs in the content layer.

**5. Round things concentrically.** Hardware curvature informs control, sheet, popover,
and window curvature. Use `ConcentricRectangle` or `.rect(corners: .concentric)` rather
than hard-coded radii, so shapes nest correctly across devices.

**6. Test the settings that change the material.** Reduce Transparency, Increase Contrast,
Reduce Motion, the Liquid Glass appearance preference, Dark Mode, and every Dynamic Type
size — including the accessibility sizes. Standard components adapt automatically; your
custom ones will not unless you check.

## Quick decision table

| Question | Answer |
|---|---|
| Glass on a card or list row? | No. Standard material. |
| Glass on a custom floating action button? | Yes — `.glassEffect()`, and wrap siblings in a `GlassEffectContainer`. |
| More than ~2 custom glass elements onscreen? | Reconsider. Performance and legibility both degrade. |
| Which glass variant? | `.regular` by default. `.clear` only over photos/video, and add a 35% dark dimming layer if the media is bright. |
| Colored toolbar buttons? | One prominent action, tinted on its background. Everything else monochrome. |
| Where does search go on iPhone? | Bottom toolbar if there's room; a search *tab* if search is a top-level destination; top toolbar only when bottom content must stay visible. |
| Tab count? | As few as read clearly. Avoid overflow into a More tab. Consider `.sidebarAdaptable` instead of many tabs. |
| Full-width button? | Avoid. Inset from screen edges; if unavoidable, match hardware curvature. |
| Minimum hit target? | 44×44 pt (28×28 pt absolute floor). |
| Section header capitalization? | Title case. The system no longer uppercases them. |

## References

Load the reference that matches the task — they are detailed and meant to be read on demand.

| File | Read it when |
|---|---|
| `references/liquid-glass.md` | Applying, combining, morphing, or debugging glass; scroll edge effects; migration checklist |
| `references/layout-and-navigation.md` | Tab bars, toolbars, sidebars, search placement, sheets, safe areas, adaptivity |
| `references/components.md` | Concrete SwiftUI recipes for buttons, lists, forms, alerts, empty states, controls |
| `references/typography.md` | Text styles, exact Dynamic Type metrics, tracking, custom fonts |
| `references/colors.md` | Semantic colors, Liquid Glass color rules, accent color, dark mode |
| `references/sf-symbols.md` | Rendering modes, gradients, variable color, Draw animations, standard action symbols |
| `references/motion.md` | Animation timing, symbol effects, glass transitions, Reduce Motion |
| `references/app-icons.md` | Layered icons, Icon Composer, the four appearance variants |
| `references/accessibility.md` | Contrast targets, VoiceOver, Dynamic Type layout, the settings that alter Liquid Glass |
| `references/app-patterns.md` | How Apple's own apps and notable third-party apps solved these problems |

## Review checklist

Run this when auditing an existing screen or finishing a new one.

**Layering**
- [ ] No Liquid Glass anywhere in the content layer
- [ ] No custom backgrounds on tab bars, toolbars, sheets, or popovers
- [ ] Content extends edge to edge and scrolls beneath the floating bars
- [ ] At most one or two custom glass elements onscreen; multiples share a `GlassEffectContainer`
- [ ] `.clear` glass used only over rich media, with dimming when the media is bright

**Navigation**
- [ ] Tab bar is for navigation only; actions live in a toolbar
- [ ] Tab bar visible throughout, never disabled or hidden outside modals
- [ ] Search uses the platform-correct entry point (`Tab(role: .search)`, bottom toolbar, or inline)
- [ ] Toolbar has ≤3 logical groups; text-labeled buttons separated by `ToolbarSpacer`
- [ ] Exactly one `.prominent` toolbar action, on the trailing edge
- [ ] Standard Back/Close symbols, not custom text buttons

**Color and type**
- [ ] Only semantic/system colors; no hard-coded system color values
- [ ] Custom colors define light, dark, and increased-contrast variants
- [ ] Chrome is monochromatic; brand color lives in content
- [ ] All text uses Dynamic Type styles, no fixed sizes
- [ ] Body text ≥ 17 pt equivalent; nothing below 11 pt
- [ ] Regular weight or heavier — no Ultralight/Thin/Light

**Shape and spacing**
- [ ] Concentric corners via `ConcentricRectangle`, not magic numbers
- [ ] All hit targets ≥ 44×44 pt
- [ ] No full-width edge-to-edge buttons
- [ ] Section headers in title case

**Adaptivity and accessibility**
- [ ] Verified at every Dynamic Type size including accessibility sizes
- [ ] Verified with Reduce Transparency, Increase Contrast, and Reduce Motion on
- [ ] Verified in light and dark
- [ ] Contrast ≥ 4.5:1 for text ≤ 17 pt, ≥ 3:1 for 18 pt+ or bold
- [ ] Every icon has an accessibility label, whether or not text is visible
- [ ] Nothing conveyed by color alone

**Icon**
- [ ] Layered source composed in Icon Composer, not a flattened PNG
- [ ] No baked-in shadows, highlights, bevels, or blurs
- [ ] Square, unmasked layers with content centered
- [ ] Default, dark, clear, and tinted variants all legible
