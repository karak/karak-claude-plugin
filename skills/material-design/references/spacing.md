# Material Design 3 Spacing & Layout System

## 4dp Baseline Grid

Material Design uses a 4dp baseline grid for all components and spacing.

```css
:root {
  /* Spacing tokens */
  --md-sys-spacing-0: 0px;
  --md-sys-spacing-1: 4px;
  --md-sys-spacing-2: 8px;
  --md-sys-spacing-3: 12px;
  --md-sys-spacing-4: 16px;
  --md-sys-spacing-5: 20px;
  --md-sys-spacing-6: 24px;
  --md-sys-spacing-7: 28px;
  --md-sys-spacing-8: 32px;
  --md-sys-spacing-9: 36px;
  --md-sys-spacing-10: 40px;
  --md-sys-spacing-12: 48px;
  --md-sys-spacing-14: 56px;
  --md-sys-spacing-16: 64px;
  --md-sys-spacing-20: 80px;
  --md-sys-spacing-24: 96px;
}
```

## Window Size Classes

Material 3 defines responsive breakpoints based on window width.

```css
:root {
  /* Compact: 0-599dp (phones) */
  --md-sys-breakpoint-compact: 0px;

  /* Medium: 600-839dp (foldables, small tablets) */
  --md-sys-breakpoint-medium: 600px;

  /* Expanded: 840dp+ (tablets, desktops) */
  --md-sys-breakpoint-expanded: 840px;

  /* Large: 1200dp+ (large tablets, desktops) */
  --md-sys-breakpoint-large: 1200px;

  /* Extra-large: 1600dp+ (large desktops) */
  --md-sys-breakpoint-extra-large: 1600px;
}
```

### Responsive Layout Examples

```css
/* Compact (mobile phones) */
@media (max-width: 599px) {
  .container {
    padding: 16px;
  }
  .grid {
    grid-template-columns: 1fr;
  }
}

/* Medium (small tablets, foldables) */
@media (min-width: 600px) and (max-width: 839px) {
  .container {
    padding: 24px;
  }
  .grid {
    grid-template-columns: repeat(2, 1fr);
  }
}

/* Expanded (large tablets, laptops) */
@media (min-width: 840px) {
  .container {
    padding: 24px;
    max-width: 1040px;
    margin: 0 auto;
  }
  .grid {
    grid-template-columns: repeat(3, 1fr);
  }
}
```

## Layout Grid

### Column Grid

```css
/* 4-column grid (compact) */
.grid-compact {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 8px;
  padding: 16px;
}

/* 8-column grid (medium) */
@media (min-width: 600px) {
  .grid-medium {
    grid-template-columns: repeat(8, 1fr);
    gap: 16px;
    padding: 24px;
  }
}

/* 12-column grid (expanded) */
@media (min-width: 840px) {
  .grid-expanded {
    grid-template-columns: repeat(12, 1fr);
    gap: 24px;
    padding: 24px;
  }
}
```

### Margin and Gutters

```css
:root {
  /* Compact */
  --md-sys-layout-margin-compact: 16px;
  --md-sys-layout-gutter-compact: 8px;

  /* Medium */
  --md-sys-layout-margin-medium: 24px;
  --md-sys-layout-gutter-medium: 16px;

  /* Expanded */
  --md-sys-layout-margin-expanded: 24px;
  --md-sys-layout-gutter-expanded: 24px;
}
```

## Touch Targets

### Minimum Touch Target Size

```css
/* Material minimum: 48x48dp */
.touch-target {
  min-height: 48px;
  min-width: 48px;
}

/* Icon button with proper touch area */
.icon-button {
  width: 48px;
  height: 48px;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 50%;
}

/* Text button with padding */
.text-button {
  min-height: 48px;
  padding: 0 24px;
}
```

## Component Dimensions

### Top App Bar

```css
.top-app-bar {
  height: 64px;
  padding: 0 16px;
  display: flex;
  align-items: center;
}

/* Small top app bar */
.top-app-bar-small {
  height: 64px;
}

/* Medium top app bar */
.top-app-bar-medium {
  height: 112px;
}

/* Large top app bar */
.top-app-bar-large {
  height: 152px;
}
```

### Bottom Navigation

```css
.bottom-navigation {
  height: 80px;
  padding: 12px 0 16px;
  display: flex;
  align-items: center;
  justify-content: space-around;
}

.bottom-nav-item {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 4px;
  min-width: 48px;
}

.bottom-nav-icon {
  width: 24px;
  height: 24px;
}

.bottom-nav-label {
  font-size: 12px;
  line-height: 16px;
  font-weight: 500;
}
```

### Navigation Rail

```css
.navigation-rail {
  width: 80px;
  padding: 44px 0 56px;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 12px;
}

.nav-rail-item {
  width: 56px;
  height: 56px;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 4px;
  border-radius: 16px;
}
```

### Navigation Drawer

```css
.navigation-drawer {
  width: 360px;
  padding: 12px;
}

.drawer-item {
  height: 56px;
  padding: 0 24px 0 16px;
  border-radius: 28px;
  display: flex;
  align-items: center;
  gap: 12px;
}
```

### FAB (Floating Action Button)

```css
/* Standard FAB */
.fab {
  width: 56px;
  height: 56px;
  border-radius: 16px;
}

/* Small FAB */
.fab-small {
  width: 40px;
  height: 40px;
  border-radius: 12px;
}

/* Large FAB */
.fab-large {
  width: 96px;
  height: 96px;
  border-radius: 28px;
}

/* Extended FAB */
.fab-extended {
  height: 56px;
  padding: 0 20px;
  border-radius: 16px;
}
```

### Cards

```css
.card {
  padding: 16px;
  border-radius: 12px;
}

.card-elevated {
  box-shadow: 0 1px 2px rgba(0, 0, 0, 0.3),
              0 1px 3px 1px rgba(0, 0, 0, 0.15);
}

.card-filled {
  background: var(--md-sys-color-surface-container-highest);
}

.card-outlined {
  border: 1px solid var(--md-sys-color-outline);
}
```

### Text Fields

```css
.text-field {
  height: 56px;
  border-radius: 4px 4px 0 0;
}

.text-field-outlined {
  border-radius: 4px;
}
```

## Shape

### Corner Radius Tokens

```css
:root {
  /* Shape tokens */
  --md-sys-shape-corner-none: 0px;
  --md-sys-shape-corner-extra-small: 4px;
  --md-sys-shape-corner-small: 8px;
  --md-sys-shape-corner-medium: 12px;
  --md-sys-shape-corner-large: 16px;
  --md-sys-shape-corner-extra-large: 28px;
  --md-sys-shape-corner-full: 9999px;
}
```

### Component Shapes

```css
/* Buttons */
.button { border-radius: var(--md-sys-shape-corner-full); }

/* Cards */
.card { border-radius: var(--md-sys-shape-corner-medium); }

/* FAB */
.fab { border-radius: var(--md-sys-shape-corner-large); }

/* Dialogs */
.dialog { border-radius: var(--md-sys-shape-corner-extra-large); }

/* Chips */
.chip { border-radius: var(--md-sys-shape-corner-small); }

/* Text fields */
.text-field { border-radius: var(--md-sys-shape-corner-extra-small); }
```

## Elevation

```css
:root {
  /* Elevation shadows */
  --md-sys-elevation-level0: none;
  --md-sys-elevation-level1: 0 1px 2px rgba(0,0,0,0.3), 0 1px 3px 1px rgba(0,0,0,0.15);
  --md-sys-elevation-level2: 0 1px 2px rgba(0,0,0,0.3), 0 2px 6px 2px rgba(0,0,0,0.15);
  --md-sys-elevation-level3: 0 4px 8px 3px rgba(0,0,0,0.15), 0 1px 3px rgba(0,0,0,0.3);
  --md-sys-elevation-level4: 0 6px 10px 4px rgba(0,0,0,0.15), 0 2px 3px rgba(0,0,0,0.3);
  --md-sys-elevation-level5: 0 8px 12px 6px rgba(0,0,0,0.15), 0 4px 4px rgba(0,0,0,0.3);
}
```
