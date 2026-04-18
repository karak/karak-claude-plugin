# Material Design 3 UI Components

## Buttons

### Filled Button (Primary)

```css
.button-filled {
  background: var(--md-sys-color-primary);
  color: var(--md-sys-color-on-primary);
  font-size: 14px;
  font-weight: 500;
  letter-spacing: 0.1px;
  padding: 0 24px;
  height: 40px;
  border: none;
  border-radius: 20px;
  cursor: pointer;
  position: relative;
  overflow: hidden;
}

.button-filled:hover {
  box-shadow: var(--md-sys-elevation-level1);
}

.button-filled:disabled {
  background: rgba(var(--md-sys-color-on-surface-rgb), 0.12);
  color: rgba(var(--md-sys-color-on-surface-rgb), 0.38);
}
```

### Filled Tonal Button

```css
.button-tonal {
  background: var(--md-sys-color-secondary-container);
  color: var(--md-sys-color-on-secondary-container);
  font-size: 14px;
  font-weight: 500;
  letter-spacing: 0.1px;
  padding: 0 24px;
  height: 40px;
  border: none;
  border-radius: 20px;
}
```

### Outlined Button

```css
.button-outlined {
  background: transparent;
  color: var(--md-sys-color-primary);
  font-size: 14px;
  font-weight: 500;
  letter-spacing: 0.1px;
  padding: 0 24px;
  height: 40px;
  border: 1px solid var(--md-sys-color-outline);
  border-radius: 20px;
}
```

### Elevated Button

```css
.button-elevated {
  background: var(--md-sys-color-surface-container-low);
  color: var(--md-sys-color-primary);
  font-size: 14px;
  font-weight: 500;
  letter-spacing: 0.1px;
  padding: 0 24px;
  height: 40px;
  border: none;
  border-radius: 20px;
  box-shadow: var(--md-sys-elevation-level1);
}
```

### Text Button

```css
.button-text {
  background: transparent;
  color: var(--md-sys-color-primary);
  font-size: 14px;
  font-weight: 500;
  letter-spacing: 0.1px;
  padding: 0 12px;
  height: 40px;
  border: none;
  border-radius: 20px;
}
```

### FAB (Floating Action Button)

```css
.fab {
  width: 56px;
  height: 56px;
  background: var(--md-sys-color-primary-container);
  color: var(--md-sys-color-on-primary-container);
  border: none;
  border-radius: 16px;
  box-shadow: var(--md-sys-elevation-level3);
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
}

.fab-icon {
  width: 24px;
  height: 24px;
}

/* Extended FAB */
.fab-extended {
  height: 56px;
  padding: 0 16px;
  border-radius: 16px;
  gap: 12px;
}

.fab-extended .fab-label {
  font-size: 14px;
  font-weight: 500;
  letter-spacing: 0.1px;
}
```

## Cards

### Elevated Card

```css
.card-elevated {
  background: var(--md-sys-color-surface-container-low);
  border-radius: 12px;
  padding: 16px;
  box-shadow: var(--md-sys-elevation-level1);
}
```

### Filled Card

```css
.card-filled {
  background: var(--md-sys-color-surface-container-highest);
  border-radius: 12px;
  padding: 16px;
}
```

### Outlined Card

```css
.card-outlined {
  background: var(--md-sys-color-surface);
  border: 1px solid var(--md-sys-color-outline-variant);
  border-radius: 12px;
  padding: 16px;
}
```

### Card Content Structure

```css
.card-header {
  display: flex;
  align-items: center;
  gap: 16px;
  margin-bottom: 16px;
}

.card-avatar {
  width: 40px;
  height: 40px;
  border-radius: 20px;
}

.card-headline {
  font-size: 16px;
  font-weight: 500;
  line-height: 24px;
  color: var(--md-sys-color-on-surface);
}

.card-subhead {
  font-size: 14px;
  font-weight: 400;
  line-height: 20px;
  color: var(--md-sys-color-on-surface-variant);
}

.card-supporting-text {
  font-size: 14px;
  line-height: 20px;
  color: var(--md-sys-color-on-surface-variant);
  margin-bottom: 16px;
}

.card-actions {
  display: flex;
  gap: 8px;
  justify-content: flex-end;
}
```

## Navigation

### Top App Bar

```css
.top-app-bar {
  height: 64px;
  padding: 0 4px 0 16px;
  background: var(--md-sys-color-surface);
  display: flex;
  align-items: center;
  gap: 4px;
}

.top-app-bar-headline {
  font-size: 22px;
  font-weight: 400;
  line-height: 28px;
  color: var(--md-sys-color-on-surface);
  flex: 1;
}

.top-app-bar-action {
  width: 48px;
  height: 48px;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 50%;
}
```

### Bottom Navigation

```css
.bottom-navigation {
  height: 80px;
  background: var(--md-sys-color-surface-container);
  display: flex;
  justify-content: space-around;
  align-items: center;
  padding: 12px 8px 16px;
}

.bottom-nav-item {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 4px;
  padding: 4px 0;
  min-width: 48px;
  color: var(--md-sys-color-on-surface-variant);
}

.bottom-nav-item.active {
  color: var(--md-sys-color-on-surface);
}

.bottom-nav-indicator {
  width: 64px;
  height: 32px;
  background: var(--md-sys-color-secondary-container);
  border-radius: 16px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.bottom-nav-icon {
  width: 24px;
  height: 24px;
}

.bottom-nav-label {
  font-size: 12px;
  font-weight: 500;
  letter-spacing: 0.5px;
  line-height: 16px;
}
```

### Navigation Drawer

```css
.navigation-drawer {
  width: 360px;
  background: var(--md-sys-color-surface-container-low);
  padding: 12px;
  height: 100%;
}

.drawer-headline {
  padding: 16px 16px 0;
  font-size: 14px;
  font-weight: 500;
  letter-spacing: 0.1px;
  color: var(--md-sys-color-on-surface-variant);
  margin-bottom: 8px;
}

.drawer-item {
  height: 56px;
  padding: 0 24px 0 16px;
  border-radius: 28px;
  display: flex;
  align-items: center;
  gap: 12px;
  color: var(--md-sys-color-on-surface-variant);
  cursor: pointer;
}

.drawer-item.active {
  background: var(--md-sys-color-secondary-container);
  color: var(--md-sys-color-on-secondary-container);
}

.drawer-item-icon {
  width: 24px;
  height: 24px;
}

.drawer-item-label {
  font-size: 14px;
  font-weight: 500;
  letter-spacing: 0.1px;
  flex: 1;
}
```

## Text Fields

### Filled Text Field

```css
.text-field-filled {
  position: relative;
  height: 56px;
  background: var(--md-sys-color-surface-container-highest);
  border-radius: 4px 4px 0 0;
  border-bottom: 1px solid var(--md-sys-color-on-surface-variant);
}

.text-field-filled input {
  width: 100%;
  height: 100%;
  padding: 20px 16px 6px;
  font-size: 16px;
  line-height: 24px;
  color: var(--md-sys-color-on-surface);
  background: transparent;
  border: none;
  outline: none;
}

.text-field-filled label {
  position: absolute;
  left: 16px;
  top: 50%;
  transform: translateY(-50%);
  font-size: 16px;
  color: var(--md-sys-color-on-surface-variant);
  transition: all 0.2s;
  pointer-events: none;
}

.text-field-filled input:focus + label,
.text-field-filled input:not(:placeholder-shown) + label {
  top: 8px;
  transform: translateY(0);
  font-size: 12px;
  color: var(--md-sys-color-primary);
}

.text-field-filled:focus-within {
  border-bottom: 2px solid var(--md-sys-color-primary);
}
```

### Outlined Text Field

```css
.text-field-outlined {
  position: relative;
  height: 56px;
}

.text-field-outlined input {
  width: 100%;
  height: 100%;
  padding: 16px;
  font-size: 16px;
  line-height: 24px;
  color: var(--md-sys-color-on-surface);
  background: transparent;
  border: 1px solid var(--md-sys-color-outline);
  border-radius: 4px;
  outline: none;
}

.text-field-outlined input:focus {
  border: 2px solid var(--md-sys-color-primary);
}

.text-field-outlined label {
  position: absolute;
  left: 12px;
  top: 50%;
  transform: translateY(-50%);
  padding: 0 4px;
  background: var(--md-sys-color-surface);
  font-size: 16px;
  color: var(--md-sys-color-on-surface-variant);
  transition: all 0.2s;
  pointer-events: none;
}

.text-field-outlined input:focus + label,
.text-field-outlined input:not(:placeholder-shown) + label {
  top: 0;
  font-size: 12px;
  color: var(--md-sys-color-primary);
}
```

## Dialogs

```css
.dialog-scrim {
  position: fixed;
  inset: 0;
  background: rgba(0, 0, 0, 0.32);
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 24px;
}

.dialog {
  background: var(--md-sys-color-surface-container-high);
  border-radius: 28px;
  padding: 24px;
  min-width: 280px;
  max-width: 560px;
  box-shadow: var(--md-sys-elevation-level3);
}

.dialog-icon {
  width: 24px;
  height: 24px;
  color: var(--md-sys-color-secondary);
  margin-bottom: 16px;
}

.dialog-headline {
  font-size: 24px;
  font-weight: 400;
  line-height: 32px;
  color: var(--md-sys-color-on-surface);
  margin-bottom: 16px;
}

.dialog-supporting-text {
  font-size: 14px;
  line-height: 20px;
  color: var(--md-sys-color-on-surface-variant);
  margin-bottom: 24px;
}

.dialog-actions {
  display: flex;
  gap: 8px;
  justify-content: flex-end;
}
```

## Snackbar

```css
.snackbar {
  display: flex;
  align-items: center;
  min-height: 48px;
  padding: 14px 16px;
  background: var(--md-sys-color-inverse-surface);
  color: var(--md-sys-color-inverse-on-surface);
  border-radius: 4px;
  box-shadow: var(--md-sys-elevation-level3);
  gap: 12px;
}

.snackbar-text {
  flex: 1;
  font-size: 14px;
  line-height: 20px;
  letter-spacing: 0.25px;
}

.snackbar-action {
  color: var(--md-sys-color-inverse-primary);
  font-size: 14px;
  font-weight: 500;
  letter-spacing: 0.1px;
  background: none;
  border: none;
  padding: 0;
  cursor: pointer;
}
```

## Chips

### Assist Chip

```css
.chip-assist {
  height: 32px;
  padding: 0 16px;
  border: 1px solid var(--md-sys-color-outline);
  border-radius: 8px;
  background: transparent;
  color: var(--md-sys-color-on-surface);
  font-size: 14px;
  font-weight: 500;
  letter-spacing: 0.1px;
  display: inline-flex;
  align-items: center;
  gap: 8px;
}
```

### Filter Chip

```css
.chip-filter {
  height: 32px;
  padding: 0 16px;
  border: 1px solid var(--md-sys-color-outline);
  border-radius: 8px;
  background: transparent;
  color: var(--md-sys-color-on-surface-variant);
  font-size: 14px;
  font-weight: 500;
}

.chip-filter.selected {
  background: var(--md-sys-color-secondary-container);
  color: var(--md-sys-color-on-secondary-container);
  border-color: transparent;
}
```

### Input Chip

```css
.chip-input {
  height: 32px;
  padding: 0 4px 0 12px;
  border: 1px solid var(--md-sys-color-outline);
  border-radius: 8px;
  background: transparent;
  color: var(--md-sys-color-on-surface-variant);
  font-size: 14px;
  font-weight: 500;
  display: inline-flex;
  align-items: center;
  gap: 8px;
}

.chip-input-remove {
  width: 18px;
  height: 18px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
}
```

## Switch

```css
.switch {
  width: 52px;
  height: 32px;
  background: var(--md-sys-color-surface-container-highest);
  border: 2px solid var(--md-sys-color-outline);
  border-radius: 16px;
  position: relative;
  cursor: pointer;
  transition: all 0.2s;
}

.switch-thumb {
  width: 16px;
  height: 16px;
  background: var(--md-sys-color-outline);
  border-radius: 50%;
  position: absolute;
  top: 6px;
  left: 6px;
  transition: all 0.2s;
}

.switch.checked {
  background: var(--md-sys-color-primary);
  border-color: var(--md-sys-color-primary);
}

.switch.checked .switch-thumb {
  width: 24px;
  height: 24px;
  background: var(--md-sys-color-on-primary);
  left: 22px;
  top: 2px;
}
```

## Badges

```css
.badge {
  min-width: 16px;
  height: 16px;
  padding: 0 4px;
  background: var(--md-sys-color-error);
  color: var(--md-sys-color-on-error);
  font-size: 11px;
  font-weight: 500;
  line-height: 16px;
  border-radius: 8px;
  display: inline-flex;
  align-items: center;
  justify-content: center;
}

.badge-large {
  min-width: 24px;
  height: 24px;
  border-radius: 12px;
  font-size: 12px;
}
```

## Progress Indicators

### Linear Progress

```css
.progress-linear {
  height: 4px;
  background: var(--md-sys-color-surface-container-highest);
  border-radius: 2px;
  overflow: hidden;
}

.progress-linear-indicator {
  height: 100%;
  background: var(--md-sys-color-primary);
  border-radius: 2px;
  transition: width 0.3s;
}
```

### Circular Progress

```css
.progress-circular {
  width: 48px;
  height: 48px;
  animation: rotate 1.4s linear infinite;
}

.progress-circular-track {
  stroke: var(--md-sys-color-surface-container-highest);
}

.progress-circular-indicator {
  stroke: var(--md-sys-color-primary);
  stroke-dasharray: 125.6;
  stroke-dashoffset: 62.8;
  animation: dash 1.4s ease-in-out infinite;
}

@keyframes rotate {
  100% { transform: rotate(360deg); }
}

@keyframes dash {
  0% { stroke-dashoffset: 125.6; }
  50% { stroke-dashoffset: 31.4; }
  100% { stroke-dashoffset: 125.6; }
}
```
