# Material Design 3 Color System

## Dynamic Color - Tonal Palettes

Material 3 generates colors from a single seed color using HCT color space.

### Primary Tonal Palette

```css
:root {
  /* Primary - Main brand color */
  --md-ref-palette-primary0: #000000;
  --md-ref-palette-primary10: #21005D;
  --md-ref-palette-primary20: #381E72;
  --md-ref-palette-primary30: #4F378B;
  --md-ref-palette-primary40: #6750A4;
  --md-ref-palette-primary50: #7F67BE;
  --md-ref-palette-primary60: #9A82DB;
  --md-ref-palette-primary70: #B69DF8;
  --md-ref-palette-primary80: #D0BCFF;
  --md-ref-palette-primary90: #EADDFF;
  --md-ref-palette-primary95: #F6EDFF;
  --md-ref-palette-primary99: #FFFBFE;
  --md-ref-palette-primary100: #FFFFFF;
}
```

### Secondary Tonal Palette

```css
:root {
  /* Secondary - Less prominent accent */
  --md-ref-palette-secondary10: #1D192B;
  --md-ref-palette-secondary20: #332D41;
  --md-ref-palette-secondary30: #4A4458;
  --md-ref-palette-secondary40: #625B71;
  --md-ref-palette-secondary50: #7A7289;
  --md-ref-palette-secondary60: #958DA5;
  --md-ref-palette-secondary70: #B0A7C0;
  --md-ref-palette-secondary80: #CCC2DC;
  --md-ref-palette-secondary90: #E8DEF8;
  --md-ref-palette-secondary95: #F6EDFF;
  --md-ref-palette-secondary99: #FFFBFE;
  --md-ref-palette-secondary100: #FFFFFF;
}
```

### Tertiary Tonal Palette

```css
:root {
  /* Tertiary - Contrasting accent */
  --md-ref-palette-tertiary10: #31111D;
  --md-ref-palette-tertiary20: #492532;
  --md-ref-palette-tertiary30: #633B48;
  --md-ref-palette-tertiary40: #7D5260;
  --md-ref-palette-tertiary50: #986977;
  --md-ref-palette-tertiary60: #B58392;
  --md-ref-palette-tertiary70: #D29DAC;
  --md-ref-palette-tertiary80: #EFB8C8;
  --md-ref-palette-tertiary90: #FFD8E4;
  --md-ref-palette-tertiary95: #FFECF1;
  --md-ref-palette-tertiary99: #FFFBFA;
  --md-ref-palette-tertiary100: #FFFFFF;
}
```

### Neutral Tonal Palette

```css
:root {
  /* Neutral - Surfaces and backgrounds */
  --md-ref-palette-neutral10: #1C1B1F;
  --md-ref-palette-neutral20: #313033;
  --md-ref-palette-neutral30: #484649;
  --md-ref-palette-neutral40: #605D62;
  --md-ref-palette-neutral50: #787579;
  --md-ref-palette-neutral60: #939094;
  --md-ref-palette-neutral70: #AEAAAE;
  --md-ref-palette-neutral80: #C9C5CA;
  --md-ref-palette-neutral90: #E6E1E5;
  --md-ref-palette-neutral95: #F4EFF4;
  --md-ref-palette-neutral99: #FFFBFE;
  --md-ref-palette-neutral100: #FFFFFF;
}
```

## Color Roles - Light Theme

```css
:root {
  /* Primary colors */
  --md-sys-color-primary: #6750A4;
  --md-sys-color-on-primary: #FFFFFF;
  --md-sys-color-primary-container: #EADDFF;
  --md-sys-color-on-primary-container: #21005D;

  /* Secondary colors */
  --md-sys-color-secondary: #625B71;
  --md-sys-color-on-secondary: #FFFFFF;
  --md-sys-color-secondary-container: #E8DEF8;
  --md-sys-color-on-secondary-container: #1D192B;

  /* Tertiary colors */
  --md-sys-color-tertiary: #7D5260;
  --md-sys-color-on-tertiary: #FFFFFF;
  --md-sys-color-tertiary-container: #FFD8E4;
  --md-sys-color-on-tertiary-container: #31111D;

  /* Error colors */
  --md-sys-color-error: #B3261E;
  --md-sys-color-on-error: #FFFFFF;
  --md-sys-color-error-container: #F9DEDC;
  --md-sys-color-on-error-container: #410E0B;

  /* Surface colors */
  --md-sys-color-surface: #FFFBFE;
  --md-sys-color-on-surface: #1C1B1F;
  --md-sys-color-surface-variant: #E7E0EC;
  --md-sys-color-on-surface-variant: #49454F;

  /* Outline */
  --md-sys-color-outline: #79747E;
  --md-sys-color-outline-variant: #CAC4D0;

  /* Background */
  --md-sys-color-background: #FFFBFE;
  --md-sys-color-on-background: #1C1B1F;

  /* Inverse */
  --md-sys-color-inverse-surface: #313033;
  --md-sys-color-inverse-on-surface: #F4EFF4;
  --md-sys-color-inverse-primary: #D0BCFF;

  /* Scrim */
  --md-sys-color-scrim: #000000;

  /* Shadow */
  --md-sys-color-shadow: #000000;
}
```

## Color Roles - Dark Theme

```css
[data-theme="dark"] {
  /* Primary colors */
  --md-sys-color-primary: #D0BCFF;
  --md-sys-color-on-primary: #381E72;
  --md-sys-color-primary-container: #4F378B;
  --md-sys-color-on-primary-container: #EADDFF;

  /* Secondary colors */
  --md-sys-color-secondary: #CCC2DC;
  --md-sys-color-on-secondary: #332D41;
  --md-sys-color-secondary-container: #4A4458;
  --md-sys-color-on-secondary-container: #E8DEF8;

  /* Tertiary colors */
  --md-sys-color-tertiary: #EFB8C8;
  --md-sys-color-on-tertiary: #492532;
  --md-sys-color-tertiary-container: #633B48;
  --md-sys-color-on-tertiary-container: #FFD8E4;

  /* Error colors */
  --md-sys-color-error: #F2B8B5;
  --md-sys-color-on-error: #601410;
  --md-sys-color-error-container: #8C1D18;
  --md-sys-color-on-error-container: #F9DEDC;

  /* Surface colors */
  --md-sys-color-surface: #1C1B1F;
  --md-sys-color-on-surface: #E6E1E5;
  --md-sys-color-surface-variant: #49454F;
  --md-sys-color-on-surface-variant: #CAC4D0;

  /* Outline */
  --md-sys-color-outline: #938F99;
  --md-sys-color-outline-variant: #49454F;

  /* Background */
  --md-sys-color-background: #1C1B1F;
  --md-sys-color-on-background: #E6E1E5;

  /* Inverse */
  --md-sys-color-inverse-surface: #E6E1E5;
  --md-sys-color-inverse-on-surface: #313033;
  --md-sys-color-inverse-primary: #6750A4;
}
```

## Surface Elevation (Tonal Elevation)

Material 3 uses surface tint instead of shadows for elevation.

```css
:root {
  /* Surface levels with elevation overlay */
  --md-sys-color-surface-dim: #DED8E1;
  --md-sys-color-surface-bright: #FFFBFE;

  /* Container colors at different elevations */
  --md-sys-color-surface-container-lowest: #FFFFFF;
  --md-sys-color-surface-container-low: #F7F2FA;
  --md-sys-color-surface-container: #F3EDF7;
  --md-sys-color-surface-container-high: #ECE6F0;
  --md-sys-color-surface-container-highest: #E6E0E9;
}

[data-theme="dark"] {
  --md-sys-color-surface-dim: #141218;
  --md-sys-color-surface-bright: #3B383E;

  --md-sys-color-surface-container-lowest: #0F0D13;
  --md-sys-color-surface-container-low: #1D1B20;
  --md-sys-color-surface-container: #211F26;
  --md-sys-color-surface-container-high: #2B2930;
  --md-sys-color-surface-container-highest: #36343B;
}
```

## State Layers

```css
:root {
  /* State layer opacity values */
  --md-sys-state-hover: 0.08;
  --md-sys-state-focus: 0.12;
  --md-sys-state-pressed: 0.12;
  --md-sys-state-dragged: 0.16;
}

/* Example: Primary button with state layers */
.button-primary {
  background: var(--md-sys-color-primary);
  color: var(--md-sys-color-on-primary);
  position: relative;
}

.button-primary::before {
  content: '';
  position: absolute;
  inset: 0;
  background: var(--md-sys-color-on-primary);
  opacity: 0;
  transition: opacity 0.2s;
}

.button-primary:hover::before {
  opacity: var(--md-sys-state-hover);
}

.button-primary:focus::before {
  opacity: var(--md-sys-state-focus);
}

.button-primary:active::before {
  opacity: var(--md-sys-state-pressed);
}
```

## Accessibility

Always ensure:
- **Normal text**: 4.5:1 minimum contrast ratio
- **Large text (24px+)**: 3:1 minimum contrast ratio
- **UI components**: 3:1 minimum contrast ratio

## Dark Mode Implementation

```css
/* Automatic dark mode */
@media (prefers-color-scheme: dark) {
  :root {
    --md-sys-color-primary: #D0BCFF;
    --md-sys-color-surface: #1C1B1F;
    /* ... other dark mode values */
  }
}

/* Manual toggle */
[data-theme="dark"] {
  /* Dark mode overrides */
}
```
