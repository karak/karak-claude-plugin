# Material Design 3 Motion System

## Easing Curves

Material 3 uses expressive easing curves for natural, physical motion.

```css
:root {
  /* Standard easing - most common */
  --md-sys-motion-easing-standard: cubic-bezier(0.2, 0.0, 0, 1.0);

  /* Standard accelerate - exiting elements */
  --md-sys-motion-easing-standard-accelerate: cubic-bezier(0.3, 0, 1, 1);

  /* Standard decelerate - entering elements */
  --md-sys-motion-easing-standard-decelerate: cubic-bezier(0, 0, 0, 1);

  /* Emphasized - important transitions */
  --md-sys-motion-easing-emphasized: cubic-bezier(0.2, 0.0, 0, 1.0);

  /* Emphasized accelerate */
  --md-sys-motion-easing-emphasized-accelerate: cubic-bezier(0.3, 0, 0.8, 0.15);

  /* Emphasized decelerate */
  --md-sys-motion-easing-emphasized-decelerate: cubic-bezier(0.05, 0.7, 0.1, 1.0);

  /* Linear - mechanical motion */
  --md-sys-motion-easing-linear: cubic-bezier(0, 0, 1, 1);
}
```

## Duration Tokens

```css
:root {
  /* Short durations - simple, small elements */
  --md-sys-motion-duration-short1: 50ms;
  --md-sys-motion-duration-short2: 100ms;
  --md-sys-motion-duration-short3: 150ms;
  --md-sys-motion-duration-short4: 200ms;

  /* Medium durations - standard transitions */
  --md-sys-motion-duration-medium1: 250ms;
  --md-sys-motion-duration-medium2: 300ms;
  --md-sys-motion-duration-medium3: 350ms;
  --md-sys-motion-duration-medium4: 400ms;

  /* Long durations - complex, large elements */
  --md-sys-motion-duration-long1: 450ms;
  --md-sys-motion-duration-long2: 500ms;
  --md-sys-motion-duration-long3: 550ms;
  --md-sys-motion-duration-long4: 600ms;

  /* Extra long - full page transitions */
  --md-sys-motion-duration-extra-long1: 700ms;
  --md-sys-motion-duration-extra-long2: 800ms;
  --md-sys-motion-duration-extra-long3: 900ms;
  --md-sys-motion-duration-extra-long4: 1000ms;
}
```

## Transition Patterns

### Fade Through

Elements fade out then fade in.

```css
/* Fade out */
.fade-through-exit {
  animation: fadeOut var(--md-sys-motion-duration-short4)
             var(--md-sys-motion-easing-standard-accelerate) forwards;
}

@keyframes fadeOut {
  from { opacity: 1; }
  to { opacity: 0; }
}

/* Fade in */
.fade-through-enter {
  animation: fadeIn var(--md-sys-motion-duration-short4)
             var(--md-sys-motion-easing-standard-decelerate) forwards;
}

@keyframes fadeIn {
  from { opacity: 0; }
  to { opacity: 1; }
}
```

### Shared Axis

Elements move along a shared axis (X, Y, or Z).

```css
/* Forward on X axis */
.shared-axis-x-enter {
  animation: slideInRight var(--md-sys-motion-duration-medium2)
             var(--md-sys-motion-easing-emphasized-decelerate) forwards;
}

@keyframes slideInRight {
  from {
    opacity: 0;
    transform: translateX(30px);
  }
  to {
    opacity: 1;
    transform: translateX(0);
  }
}

.shared-axis-x-exit {
  animation: slideOutLeft var(--md-sys-motion-duration-medium1)
             var(--md-sys-motion-easing-emphasized-accelerate) forwards;
}

@keyframes slideOutLeft {
  from {
    opacity: 1;
    transform: translateX(0);
  }
  to {
    opacity: 0;
    transform: translateX(-30px);
  }
}

/* Forward on Y axis */
.shared-axis-y-enter {
  animation: slideInUp var(--md-sys-motion-duration-medium2)
             var(--md-sys-motion-easing-emphasized-decelerate) forwards;
}

@keyframes slideInUp {
  from {
    opacity: 0;
    transform: translateY(30px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

.shared-axis-y-exit {
  animation: slideOutUp var(--md-sys-motion-duration-medium1)
             var(--md-sys-motion-easing-emphasized-accelerate) forwards;
}

@keyframes slideOutUp {
  from {
    opacity: 1;
    transform: translateY(0);
  }
  to {
    opacity: 0;
    transform: translateY(-30px);
  }
}

/* Forward on Z axis (scale) */
.shared-axis-z-enter {
  animation: scaleIn var(--md-sys-motion-duration-medium2)
             var(--md-sys-motion-easing-emphasized-decelerate) forwards;
}

@keyframes scaleIn {
  from {
    opacity: 0;
    transform: scale(0.8);
  }
  to {
    opacity: 1;
    transform: scale(1);
  }
}
```

### Container Transform

Seamlessly transforms one element into another.

```css
.container-transform {
  animation: containerExpand var(--md-sys-motion-duration-long2)
             var(--md-sys-motion-easing-emphasized) forwards;
}

@keyframes containerExpand {
  from {
    border-radius: var(--md-sys-shape-corner-medium);
    transform: scale(0.85);
  }
  to {
    border-radius: var(--md-sys-shape-corner-large);
    transform: scale(1);
  }
}

/* Card to full screen */
.card-expand {
  transition: all var(--md-sys-motion-duration-long2)
              var(--md-sys-motion-easing-emphasized);
}

.card-expand.expanded {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  border-radius: 0;
  z-index: 100;
}
```

## Component Transitions

### Button States

```css
.button {
  transition:
    background-color var(--md-sys-motion-duration-short2) var(--md-sys-motion-easing-standard),
    box-shadow var(--md-sys-motion-duration-short2) var(--md-sys-motion-easing-standard),
    transform var(--md-sys-motion-duration-short1) var(--md-sys-motion-easing-standard);
}

.button:hover {
  /* State layer applied */
}

.button:active {
  transform: scale(0.98);
}
```

### Ripple Effect

```css
.ripple {
  position: relative;
  overflow: hidden;
}

.ripple::after {
  content: '';
  position: absolute;
  width: 100%;
  padding-bottom: 100%;
  border-radius: 50%;
  background: currentColor;
  opacity: 0;
  transform: scale(0);
  pointer-events: none;
}

.ripple:active::after {
  animation: rippleEffect var(--md-sys-motion-duration-medium4)
             var(--md-sys-motion-easing-standard);
}

@keyframes rippleEffect {
  0% {
    opacity: 0.12;
    transform: scale(0);
  }
  100% {
    opacity: 0;
    transform: scale(2.5);
  }
}
```

### FAB Animation

```css
/* FAB enter */
.fab {
  animation: fabEnter var(--md-sys-motion-duration-medium2)
             var(--md-sys-motion-easing-emphasized-decelerate);
}

@keyframes fabEnter {
  from {
    opacity: 0;
    transform: scale(0.6) rotate(-45deg);
  }
  to {
    opacity: 1;
    transform: scale(1) rotate(0);
  }
}

/* Extended FAB expand */
.fab-extended {
  transition: width var(--md-sys-motion-duration-medium2)
              var(--md-sys-motion-easing-standard);
}
```

### Dialog

```css
/* Dialog scrim */
.dialog-scrim {
  animation: fadeIn var(--md-sys-motion-duration-short3)
             var(--md-sys-motion-easing-linear);
  background: rgba(0, 0, 0, 0.32);
}

/* Dialog container */
.dialog {
  animation: dialogEnter var(--md-sys-motion-duration-medium2)
             var(--md-sys-motion-easing-emphasized-decelerate);
}

@keyframes dialogEnter {
  from {
    opacity: 0;
    transform: scale(0.9);
  }
  to {
    opacity: 1;
    transform: scale(1);
  }
}

.dialog-exit {
  animation: dialogExit var(--md-sys-motion-duration-short4)
             var(--md-sys-motion-easing-emphasized-accelerate) forwards;
}

@keyframes dialogExit {
  to {
    opacity: 0;
    transform: scale(0.9);
  }
}
```

### Bottom Sheet

```css
.bottom-sheet {
  animation: bottomSheetEnter var(--md-sys-motion-duration-medium4)
             var(--md-sys-motion-easing-emphasized-decelerate);
}

@keyframes bottomSheetEnter {
  from {
    transform: translateY(100%);
  }
  to {
    transform: translateY(0);
  }
}

.bottom-sheet-exit {
  animation: bottomSheetExit var(--md-sys-motion-duration-medium2)
             var(--md-sys-motion-easing-emphasized-accelerate) forwards;
}

@keyframes bottomSheetExit {
  to {
    transform: translateY(100%);
  }
}
```

### Snackbar

```css
.snackbar {
  animation: snackbarEnter var(--md-sys-motion-duration-medium1)
             var(--md-sys-motion-easing-emphasized-decelerate);
}

@keyframes snackbarEnter {
  from {
    opacity: 0;
    transform: translateY(100%) scale(0.8);
  }
  to {
    opacity: 1;
    transform: translateY(0) scale(1);
  }
}

.snackbar-exit {
  animation: snackbarExit var(--md-sys-motion-duration-short4)
             var(--md-sys-motion-easing-standard-accelerate) forwards;
}

@keyframes snackbarExit {
  to {
    opacity: 0;
    transform: translateY(100%);
  }
}
```

### Navigation Rail / Drawer

```css
/* Navigation drawer */
.navigation-drawer {
  animation: drawerEnter var(--md-sys-motion-duration-medium4)
             var(--md-sys-motion-easing-emphasized-decelerate);
}

@keyframes drawerEnter {
  from {
    transform: translateX(-100%);
  }
  to {
    transform: translateX(0);
  }
}

/* Active indicator */
.nav-item-indicator {
  transition: all var(--md-sys-motion-duration-medium1)
              var(--md-sys-motion-easing-emphasized);
}
```

### Chip

```css
.chip {
  transition:
    background-color var(--md-sys-motion-duration-short2) var(--md-sys-motion-easing-standard),
    border-color var(--md-sys-motion-duration-short2) var(--md-sys-motion-easing-standard);
}

/* Chip enter animation */
.chip-enter {
  animation: chipEnter var(--md-sys-motion-duration-short4)
             var(--md-sys-motion-easing-emphasized-decelerate);
}

@keyframes chipEnter {
  from {
    opacity: 0;
    transform: scale(0.8);
  }
  to {
    opacity: 1;
    transform: scale(1);
  }
}
```

### Switch

```css
.switch-thumb {
  transition: transform var(--md-sys-motion-duration-short4)
              var(--md-sys-motion-easing-standard);
}

.switch-track {
  transition: background-color var(--md-sys-motion-duration-short3)
              var(--md-sys-motion-easing-standard);
}
```

### Progress Indicators

```css
/* Linear progress - indeterminate */
.linear-progress-indeterminate::before {
  animation: linearIndeterminate 2s var(--md-sys-motion-easing-standard) infinite;
}

@keyframes linearIndeterminate {
  0% {
    transform: translateX(-100%);
  }
  100% {
    transform: translateX(100%);
  }
}

/* Circular progress */
.circular-progress {
  animation: circularRotate 1.4s var(--md-sys-motion-easing-linear) infinite;
}

@keyframes circularRotate {
  100% {
    transform: rotate(360deg);
  }
}

.circular-progress-path {
  animation: circularDash 1.4s var(--md-sys-motion-easing-standard) infinite;
  stroke-dasharray: 80, 200;
  stroke-dashoffset: 0;
}

@keyframes circularDash {
  0% {
    stroke-dasharray: 1, 200;
    stroke-dashoffset: 0;
  }
  50% {
    stroke-dasharray: 100, 200;
    stroke-dashoffset: -15;
  }
  100% {
    stroke-dasharray: 100, 200;
    stroke-dashoffset: -125;
  }
}
```

## Text Field

```css
.text-field-label {
  transition:
    transform var(--md-sys-motion-duration-short4) var(--md-sys-motion-easing-standard),
    font-size var(--md-sys-motion-duration-short4) var(--md-sys-motion-easing-standard),
    color var(--md-sys-motion-duration-short3) var(--md-sys-motion-easing-standard);
}

.text-field:focus-within .text-field-label {
  transform: translateY(-50%);
  font-size: 12px;
}

.text-field-indicator {
  transition: transform var(--md-sys-motion-duration-short4)
              var(--md-sys-motion-easing-standard);
  transform: scaleX(0);
}

.text-field:focus-within .text-field-indicator {
  transform: scaleX(1);
}
```

## Reduced Motion

```css
@media (prefers-reduced-motion: reduce) {
  *,
  *::before,
  *::after {
    animation-duration: 0.01ms !important;
    animation-iteration-count: 1 !important;
    transition-duration: 0.01ms !important;
    scroll-behavior: auto !important;
  }
}
```

## Motion Best Practices

1. **Use appropriate duration**: Small elements need shorter durations
2. **Match easing to intent**: Emphasized for important, standard for routine
3. **Decelerate entering, accelerate exiting**: Elements slow down as they arrive
4. **Maintain continuity**: Related elements should animate together
5. **Support reduced motion**: Always provide accessibility fallbacks
6. **Keep ripples fast**: Don't let them distract from interaction
