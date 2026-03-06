# Material Design 3 Typography System

## Font Family

```css
/* Primary system font stack */
--font-family-plain: 'Roboto', -apple-system, BlinkMacSystemFont,
                     'Segoe UI', Arial, sans-serif;

/* Brand font for headlines */
--font-family-brand: 'Google Sans', 'Roboto', sans-serif;

/* Monospace for code */
--font-family-mono: 'Roboto Mono', ui-monospace, monospace;
```

## Type Scale - Material Design 3

### Display Large
```css
.display-large {
  font-family: var(--font-family-brand);
  font-size: 57px;
  line-height: 64px;
  font-weight: 400;
  letter-spacing: -0.25px;
}
```

### Display Medium
```css
.display-medium {
  font-family: var(--font-family-brand);
  font-size: 45px;
  line-height: 52px;
  font-weight: 400;
  letter-spacing: 0px;
}
```

### Display Small
```css
.display-small {
  font-family: var(--font-family-brand);
  font-size: 36px;
  line-height: 44px;
  font-weight: 400;
  letter-spacing: 0px;
}
```

### Headline Large
```css
.headline-large {
  font-family: var(--font-family-brand);
  font-size: 32px;
  line-height: 40px;
  font-weight: 400;
  letter-spacing: 0px;
}
```

### Headline Medium
```css
.headline-medium {
  font-family: var(--font-family-brand);
  font-size: 28px;
  line-height: 36px;
  font-weight: 400;
  letter-spacing: 0px;
}
```

### Headline Small
```css
.headline-small {
  font-family: var(--font-family-brand);
  font-size: 24px;
  line-height: 32px;
  font-weight: 400;
  letter-spacing: 0px;
}
```

### Title Large
```css
.title-large {
  font-family: var(--font-family-plain);
  font-size: 22px;
  line-height: 28px;
  font-weight: 400;
  letter-spacing: 0px;
}
```

### Title Medium
```css
.title-medium {
  font-family: var(--font-family-plain);
  font-size: 16px;
  line-height: 24px;
  font-weight: 500;
  letter-spacing: 0.15px;
}
```

### Title Small
```css
.title-small {
  font-family: var(--font-family-plain);
  font-size: 14px;
  line-height: 20px;
  font-weight: 500;
  letter-spacing: 0.1px;
}
```

### Body Large
```css
.body-large {
  font-family: var(--font-family-plain);
  font-size: 16px;
  line-height: 24px;
  font-weight: 400;
  letter-spacing: 0.5px;
}
```

### Body Medium
```css
.body-medium {
  font-family: var(--font-family-plain);
  font-size: 14px;
  line-height: 20px;
  font-weight: 400;
  letter-spacing: 0.25px;
}
```

### Body Small
```css
.body-small {
  font-family: var(--font-family-plain);
  font-size: 12px;
  line-height: 16px;
  font-weight: 400;
  letter-spacing: 0.4px;
}
```

### Label Large
```css
.label-large {
  font-family: var(--font-family-plain);
  font-size: 14px;
  line-height: 20px;
  font-weight: 500;
  letter-spacing: 0.1px;
}
```

### Label Medium
```css
.label-medium {
  font-family: var(--font-family-plain);
  font-size: 12px;
  line-height: 16px;
  font-weight: 500;
  letter-spacing: 0.5px;
}
```

### Label Small
```css
.label-small {
  font-family: var(--font-family-plain);
  font-size: 11px;
  line-height: 16px;
  font-weight: 500;
  letter-spacing: 0.5px;
}
```

## Font Weights

```css
:root {
  --font-weight-thin: 100;
  --font-weight-light: 300;
  --font-weight-regular: 400;
  --font-weight-medium: 500;
  --font-weight-bold: 700;
  --font-weight-black: 900;
}
```

## CSS Custom Properties for Type Scale

```css
:root {
  /* Display */
  --md-sys-typescale-display-large: 57px/64px var(--font-family-brand);
  --md-sys-typescale-display-medium: 45px/52px var(--font-family-brand);
  --md-sys-typescale-display-small: 36px/44px var(--font-family-brand);

  /* Headline */
  --md-sys-typescale-headline-large: 32px/40px var(--font-family-brand);
  --md-sys-typescale-headline-medium: 28px/36px var(--font-family-brand);
  --md-sys-typescale-headline-small: 24px/32px var(--font-family-brand);

  /* Title */
  --md-sys-typescale-title-large: 22px/28px var(--font-family-plain);
  --md-sys-typescale-title-medium: 500 16px/24px var(--font-family-plain);
  --md-sys-typescale-title-small: 500 14px/20px var(--font-family-plain);

  /* Body */
  --md-sys-typescale-body-large: 16px/24px var(--font-family-plain);
  --md-sys-typescale-body-medium: 14px/20px var(--font-family-plain);
  --md-sys-typescale-body-small: 12px/16px var(--font-family-plain);

  /* Label */
  --md-sys-typescale-label-large: 500 14px/20px var(--font-family-plain);
  --md-sys-typescale-label-medium: 500 12px/16px var(--font-family-plain);
  --md-sys-typescale-label-small: 500 11px/16px var(--font-family-plain);
}
```

## Typography Best Practices

1. **Use Roboto** for body text and labels
2. **Use Google Sans** for headlines and display text
3. **Maintain proper letter-spacing** for each size
4. **Use medium weight (500)** for emphasis, not bold
5. **Support large text preferences** - scale with user settings
6. **Limit to 3-4 type styles** per screen for clarity
