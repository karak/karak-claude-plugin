---
name: material-design
description: >
  Create modern, expressive UI designs following Google's Material Design 3 (Material You) guidelines.
  This skill should be used when users request creating HTML/CSS mockups, web interfaces,
  or UI screens with Android-style aesthetics - featuring Roboto typography, dynamic color system,
  elevation shadows, ripple effects, and mobile-first responsive design.
  Applies to dashboards, forms, cards, navigation, dialogs, FABs, and any interface requiring
  Material Design's signature expressive, adaptable look with attention to motion, color harmony, and accessibility.
---

# Material Design Skill

This skill enables creation of modern, expressive UI designs following Google's Material Design 3 (Material You) with a focus on mobile-first, Android-native aesthetics.

## Design Philosophy

Material Design 3 is characterized by:
- **Personal**: Dynamic color that adapts to user preferences
- **Expressive**: Bold color, typography, and motion
- **Adaptive**: Responsive layouts that work across devices

## When to Use This Skill

Use this skill when creating:
- Mobile-first web interfaces with Android-native appearance
- Dashboard screens and data visualizations
- Forms and input interfaces with outlined/filled text fields
- Card-based layouts with elevation
- Navigation systems (bottom navigation, navigation drawer, rail)
- Dialogs, bottom sheets, and snackbars
- Any UI requiring Material Design's expressive, colorful aesthetic

## Core Design System

### Typography

Use Roboto for all text content with Material's type scale. Reference `references/typography.md` for complete font specifications.

```css
/* System font stack for Material typography */
font-family: 'Roboto', 'Google Sans', -apple-system, BlinkMacSystemFont,
             'Segoe UI', Arial, sans-serif;
```

### Color System

Reference `references/colors.md` for the complete dynamic color system including:
- Primary, Secondary, Tertiary color roles
- Surface colors and elevation tones
- On-colors for text/icons
- Error, outline, and scrim colors
- Light and dark theme support

### Spacing & Layout

Reference `references/spacing.md` for Material's spacing system:
- 4dp baseline grid
- Responsive layout grid
- Breakpoints and window size classes
- Touch target sizes

### Components

Reference `references/components.md` for Material 3 component patterns:
- Buttons (filled, outlined, tonal, elevated, text)
- Cards with elevation
- Navigation (bottom nav, drawer, rail)
- Text fields (filled, outlined)
- Dialogs and bottom sheets
- FABs and extended FABs
- Chips and badges

### Motion & Animation

Reference `references/motion.md` for Material's motion principles:
- Easing curves
- Duration tokens
- Transitions and shared axis
- Container transforms

## Implementation Workflow

1. **Analyze Requirements**: Understand the interface purpose and information hierarchy
2. **Generate Color Scheme**: Create dynamic color palette from seed color
3. **Choose Layout Pattern**: Select appropriate Material layout (bottom nav, drawer, rail)
4. **Apply Typography**: Use Roboto with proper type scale
5. **Add Components**: Use Material 3 component patterns with proper elevation
6. **Implement Motion**: Add expressive, purposeful animations
7. **Ensure Accessibility**: Follow Material accessibility guidelines

## File Structure

```
material-design/
├── SKILL.md
├── references/
│   ├── typography.md     - Type scale and text styles
│   ├── colors.md         - Dynamic color system
│   ├── spacing.md        - Grid system and layout
│   ├── components.md     - UI component patterns
│   └── motion.md         - Animation and transitions
└── assets/
    └── (templates as needed)
```

## Key Principles

### Mobile-First Approach
- Design for Android viewport first
- Use responsive breakpoints for larger screens
- Touch-friendly tap targets (48x48dp minimum)

### Elevation & Depth
- Use tonal elevation (surface + overlay) instead of shadows
- Apply elevation tokens consistently
- Create visual hierarchy through surface tones

### Dynamic Color
- Generate palette from single seed color
- Support light and dark themes
- Use color roles semantically

### Accessibility
- Minimum 4.5:1 contrast ratio
- Support large text preferences
- Include focus indicators and state layers
