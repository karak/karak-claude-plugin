---
name: material-design
description: >
  Create modern, expressive UI designs following Google's Material Design 3 (Material You) guidelines.
  Use this skill when building HTML/CSS mockups, web interfaces, dashboards, or UI screens with
  Android-style or Google-style aesthetics. Covers Roboto typography, dynamic color system with tonal
  palettes, elevation shadows, ripple effects, state layers, and mobile-first responsive design.
  Trigger this skill whenever the user mentions Material Design, Material You, M3, Android UI,
  Google-style interface, tonal elevation, dynamic color, or wants to build any web UI that should
  look and feel like a modern Android or Google app — even if they don't say "Material Design" explicitly.
  Also use when the user asks for a dark/light theme toggle with tonal surfaces, or card-based layouts
  with Material-style elevation and rounded corners.
---

# Material Design 3 Skill

Build expressive, adaptive web interfaces following Google's Material Design 3 (Material You) system. Material 3 emphasizes personal dynamic color, bold typography, and purposeful motion — creating UIs that feel alive and adapt to user preferences.

## When to Use

- Building web UIs with Android-native or Google-style appearance
- Creating dashboards, forms, card layouts, or data visualizations with M3 aesthetics
- Implementing dark/light theme toggle with tonal surface elevation
- Designing navigation systems (bottom nav, drawer, rail)
- Building dialogs, bottom sheets, snackbars, FABs
- Any HTML/CSS/React interface that should feel like a modern Android app

## Core Design System

### Typography

Use Roboto for body text; Google Sans for headlines. Material 3 defines 15 type roles across 5 categories (Display, Headline, Title, Body, Label), each with Large/Medium/Small variants.

```html
<link href="https://fonts.googleapis.com/css2?family=Roboto:wght@400;500;700&family=Google+Sans:wght@400;500&display=swap" rel="stylesheet">
```

```css
:root {
  --font-plain: 'Roboto', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
  --font-brand: 'Google Sans', 'Roboto', sans-serif;
}

/* Key type roles — see references/typography.md for full scale */
.headline-large { font: 400 32px/40px var(--font-brand); }
.title-medium   { font: 500 16px/24px var(--font-plain); letter-spacing: 0.15px; }
.body-large     { font: 400 16px/24px var(--font-plain); letter-spacing: 0.5px; }
.label-large    { font: 500 14px/20px var(--font-plain); letter-spacing: 0.1px; }
```

Read `references/typography.md` for the complete 15-role type scale with exact sizes, weights, and letter-spacing.

### Color System

Material 3 generates an entire palette from a single seed color using tonal palettes. Each color role has a semantic purpose — use roles, not raw hex values.

```css
:root {
  /* Primary — brand identity, key actions */
  --md-sys-color-primary: #6750A4;
  --md-sys-color-on-primary: #FFFFFF;
  --md-sys-color-primary-container: #EADDFF;
  --md-sys-color-on-primary-container: #21005D;

  /* Surface — backgrounds at different elevations */
  --md-sys-color-surface: #FFFBFE;
  --md-sys-color-on-surface: #1C1B1F;
  --md-sys-color-surface-container: #F3EDF7;
  --md-sys-color-surface-container-high: #ECE6F0;

  /* Outline — borders, dividers */
  --md-sys-color-outline: #79747E;
  --md-sys-color-outline-variant: #CAC4D0;
}
```

Material 3 uses **tonal elevation** instead of shadows: higher surfaces get subtly lighter background tones (surface-container-low through surface-container-highest). This creates depth without heavy drop shadows.

Read `references/colors.md` for full light/dark theme tokens, tonal palettes, state layers, and accessibility contrast requirements.

### Spacing & Shape

4dp baseline grid. Touch targets minimum 48x48dp.

```css
:root {
  /* Spacing */
  --spacing-xs: 4px;  --spacing-sm: 8px;  --spacing-md: 16px;
  --spacing-lg: 24px; --spacing-xl: 32px; --spacing-2xl: 48px;

  /* Shape — rounded corners define component identity */
  --shape-none: 0px;
  --shape-xs: 4px;    /* text fields */
  --shape-sm: 8px;    /* chips */
  --shape-md: 12px;   /* cards */
  --shape-lg: 16px;   /* FABs */
  --shape-xl: 28px;   /* dialogs */
  --shape-full: 9999px; /* buttons, pills */
}
```

Read `references/spacing.md` for responsive breakpoints (compact/medium/expanded), column grids, and component dimensions.

### Key Components

#### Buttons

```css
/* Filled button — primary actions */
.btn-filled {
  background: var(--md-sys-color-primary);
  color: var(--md-sys-color-on-primary);
  font: 500 14px/20px var(--font-plain);
  letter-spacing: 0.1px;
  height: 40px; padding: 0 24px;
  border: none; border-radius: var(--shape-full);
  cursor: pointer;
}

/* Outlined button — secondary actions */
.btn-outlined {
  background: transparent;
  color: var(--md-sys-color-primary);
  border: 1px solid var(--md-sys-color-outline);
  height: 40px; padding: 0 24px;
  border-radius: var(--shape-full);
}

/* Tonal button — medium emphasis */
.btn-tonal {
  background: var(--md-sys-color-secondary-container);
  color: var(--md-sys-color-on-secondary-container);
  border: none; height: 40px; padding: 0 24px;
  border-radius: var(--shape-full);
}
```

#### Cards

```css
/* Elevated card — default, with shadow */
.card-elevated {
  background: var(--md-sys-color-surface-container-low);
  border-radius: var(--shape-md);
  padding: var(--spacing-md);
  box-shadow: 0 1px 2px rgba(0,0,0,0.3), 0 1px 3px 1px rgba(0,0,0,0.15);
}

/* Filled card — no shadow, tonal background */
.card-filled {
  background: var(--md-sys-color-surface-container-highest);
  border-radius: var(--shape-md);
  padding: var(--spacing-md);
}

/* Outlined card — minimal, bordered */
.card-outlined {
  background: var(--md-sys-color-surface);
  border: 1px solid var(--md-sys-color-outline-variant);
  border-radius: var(--shape-md);
  padding: var(--spacing-md);
}
```

#### Top App Bar

```css
.top-app-bar {
  height: 64px;
  padding: 0 4px 0 16px;
  background: var(--md-sys-color-surface);
  display: flex; align-items: center; gap: 4px;
}
.top-app-bar h1 {
  font: 400 22px/28px var(--font-plain);
  color: var(--md-sys-color-on-surface);
  flex: 1;
}
```

Read `references/components.md` for full patterns: FABs, text fields, dialogs, snackbars, chips, switches, badges, progress indicators, bottom navigation, navigation drawer/rail.

### Motion

Material 3 motion is expressive and purposeful. Use emphasized easing for important transitions, standard for routine ones.

```css
:root {
  --ease-standard: cubic-bezier(0.2, 0, 0, 1.0);
  --ease-emphasized-decel: cubic-bezier(0.05, 0.7, 0.1, 1.0);
  --ease-emphasized-accel: cubic-bezier(0.3, 0, 0.8, 0.15);
  --dur-short: 200ms;
  --dur-medium: 300ms;
  --dur-long: 500ms;
}

/* Entering elements decelerate, exiting elements accelerate */
.enter { animation: fadeSlideIn var(--dur-medium) var(--ease-emphasized-decel); }
.exit  { animation: fadeSlideOut var(--dur-short) var(--ease-emphasized-accel); }
```

Read `references/motion.md` for transition patterns (fade through, shared axis, container transform), ripple effects, component animations, and reduced-motion support.

## Implementation Workflow

1. **Choose a seed color** — generate primary/secondary/tertiary tonal palettes from it
2. **Set up CSS custom properties** — define all color roles, type scale, spacing, and shape tokens
3. **Pick layout pattern** — bottom nav (mobile), nav rail (tablet), nav drawer (desktop)
4. **Build with semantic tokens** — never hardcode colors or sizes; always use `var(--md-sys-color-*)`
5. **Add state layers** — hover (0.08 opacity), focus (0.12), pressed (0.12) using `::before` pseudo-elements
6. **Implement motion** — decelerate entering, accelerate exiting, support `prefers-reduced-motion`
7. **Support dark theme** — swap color roles via `[data-theme="dark"]` or `prefers-color-scheme`
8. **Verify accessibility** — 4.5:1 contrast for text, 3:1 for large text and UI components

## Dark Theme

Swap the entire color system, not individual properties. Material 3 dark theme is not simply "invert" — it uses carefully chosen tonal values:

```css
[data-theme="dark"] {
  --md-sys-color-primary: #D0BCFF;
  --md-sys-color-on-primary: #381E72;
  --md-sys-color-surface: #1C1B1F;
  --md-sys-color-on-surface: #E6E1E5;
  --md-sys-color-surface-container: #211F26;
  /* ... see references/colors.md for complete dark tokens */
}
```

## Responsive Breakpoints

| Window class | Width | Columns | Navigation | Margin |
|---|---|---|---|---|
| Compact (phone) | 0-599px | 4 | Bottom nav | 16px |
| Medium (tablet) | 600-839px | 8 | Nav rail | 24px |
| Expanded (desktop) | 840px+ | 12 | Nav drawer | 24px |

## Anti-Patterns to Avoid

**Do NOT:**
- Use raw hex colors instead of semantic color roles (breaks theming)
- Apply heavy drop shadows — use tonal elevation (surface-container levels) instead
- Mix Material Design with iOS-style components (blurs, segmented controls)
- Use font sizes outside the 15-role type scale
- Make touch targets smaller than 48x48dp on mobile
- Ignore state layers — interactive elements need visible hover/focus/pressed feedback
- Skip `prefers-reduced-motion` — always provide motion accessibility
- Use pure black (#000) backgrounds in dark mode — Material 3 dark surfaces are dark gray

**Do:**
- Use `var(--md-sys-color-*)` tokens everywhere for automatic theming
- Apply border-radius from shape tokens for consistent corner rounding
- Use tonal button for medium-emphasis actions (not outlined)
- Test with both light and dark themes
- Include ripple feedback on all interactive surfaces

## Quick Reference

| Element | Size | Radius | Elevation |
|---|---|---|---|
| Filled button | 40px h | full (9999px) | level 0 |
| FAB | 56x56px | 16px | level 3 |
| Card | auto | 12px | level 1 |
| Dialog | 280-560px w | 28px | level 3 |
| Top app bar | 64px h | 0 | level 0-2 |
| Bottom nav | 80px h | 0 | level 2 |
| Chip | 32px h | 8px | level 0 |
| Text field | 56px h | 4px top | level 0 |

## Resources

- `references/typography.md` — Complete 15-role type scale with CSS custom properties
- `references/colors.md` — Full light/dark theme tokens, tonal palettes, state layers
- `references/spacing.md` — Responsive grid, breakpoints, touch targets, component dimensions, shape tokens
- `references/components.md` — All M3 component patterns with CSS
- `references/motion.md` — Easing curves, duration tokens, transition patterns, animations
