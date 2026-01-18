---
name: icon-design
description: Generate application icons for modern web and mobile applications in major image formats including PNG and SVG. This skill should be used when creating app icons, launcher icons, favicons, or PWA icons. It provides platform-specific specifications (iOS, Android, Web), design best practices, color psychology guidance, and references to popular app icon designs. Use this skill for icon design requests, app branding projects, or when generating icon assets for app stores.
---

# Icon Design

## Overview

This skill enables the creation of professional application icons for iOS, Android, and web platforms. It provides comprehensive guidance on technical specifications, design principles, color psychology, and platform-specific requirements. The skill includes reference materials for popular Japanese apps and standard OS icons to inform design decisions.

## Workflow

### 1. Gather Requirements

Before designing, collect the following information:

- **App Name**: For context and potential letterform design
- **App Category**: (Messaging, Finance, Productivity, Entertainment, etc.)
- **Target Platforms**: iOS, Android, Web/PWA, or all
- **Brand Colors**: Existing brand palette or preference
- **Style Direction**: Minimal, bold, playful, professional, etc.
- **Unique Elements**: Logo, mascot, symbol, or letterform preference

### 2. Design the Icon

Follow these core principles:

1. **Start Simple**: Begin with one primary visual element
2. **Design at 1024x1024**: Work at maximum size, then verify at small sizes
3. **Use Safe Zones**: Keep critical content within platform safe zones
4. **Test Scalability**: Verify clarity at 29px, 60px, 180px, and 1024px
5. **Consider Context**: Test on light/dark backgrounds and various wallpapers

### 3. Export Assets

Export in the required formats for each target platform:

**iOS (App Store)**:
- 1024x1024 PNG (single master file)
- No transparency, no rounded corners
- sRGB or Display P3 color space

**Android (Google Play)**:
- 512x512 PNG for Play Store
- Adaptive icon layers (108x108 dp foreground/background)
- Optional: Monochrome version for Android 13+ theming

**Web/PWA**:
- Multiple PNG sizes: 72, 96, 128, 144, 152, 192, 384, 512
- SVG for scalable use
- favicon.ico for legacy support

## Design Guidelines

### Color Selection

Reference `references/design-principles.md` for detailed color psychology. Quick guide:

| Color | Use For | Examples |
|-------|---------|----------|
| Blue | Trust, Finance, Social | Facebook, LinkedIn |
| Red | Energy, Food, Entertainment | YouTube, PayPay |
| Green | Communication, Health | LINE, WhatsApp |
| Yellow | Creativity, Notes | Snapchat, Keep |
| Black | Premium, Fashion | Uber, ZOZOTOWN |

### Shape Principles

- **Circles**: Social, friendly apps
- **Squares**: Business, productivity apps
- **Organic**: Creative, playful apps

### Typography Rules

- Only include text if essential to brand identity
- Use bold, simple typefaces
- Limit to 1-3 characters maximum
- Ensure legibility at 60px

## Platform Specifications

Reference `references/platform-specifications.md` for complete technical details.

### iOS Quick Reference
```
App Store: 1024x1024 PNG
Format: PNG, no transparency
Color: sRGB or Display P3
Corners: DO NOT round (Apple applies squircle mask)
```

### Android Quick Reference
```
Play Store: 512x512 PNG
Adaptive: 108x108 dp layers (foreground + background)
Safe Zone: 66x66 dp centered circle
Monochrome: Single layer for themed icons (Android 13+)
```

### Web Quick Reference
```
Favicon: 16, 32, 48 PNG + SVG
Apple Touch: 180x180 PNG
PWA: 192, 512 PNG (minimum)
```

## Reference Materials

### Platform Specifications
Read `references/platform-specifications.md` for:
- Complete size tables for all Apple devices
- Android adaptive icon layer specifications
- Web favicon and PWA manifest requirements
- SVG export best practices

### Japanese App Icons
Read `references/japanese-apps-icons.md` for:
- Popular payment apps (PayPay, LINE Pay, Rakuten Pay)
- Messaging apps (LINE)
- E-commerce apps (Mercari, Rakuten, Amazon Japan)
- News apps (Yahoo! JAPAN, SmartNews)
- Design patterns specific to Japanese market

### Standard OS Icons
Read `references/standard-os-icons.md` for:
- iOS built-in app designs (Messages, Calendar, Clock, etc.)
- Android/Google app designs
- Category-specific design patterns
- Platform design language comparison

### Design Principles
Read `references/design-principles.md` for:
- Color psychology and associations
- The 60-30-10 color rule
- Shape and composition guidelines
- Typography best practices
- A/B testing strategies
- Accessibility considerations
- Pre-launch checklist

## SVG Icon Generation

When generating SVG icons, use this template structure:

```svg
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1024 1024">
  <!-- Background -->
  <rect width="1024" height="1024" fill="#BACKGROUND_COLOR"/>

  <!-- Main icon element -->
  <!-- Center content within 680x680 safe zone (172px margin) -->

</svg>
```

### SVG Best Practices
- Use `viewBox="0 0 1024 1024"` for scalability
- Convert text to paths for font independence
- Optimize with SVGO before delivery
- Keep file size under 100KB
- Use semantic naming for layers

## PNG Generation Workflow

To generate PNG exports from SVG:

1. Create master SVG at 1024x1024
2. Export PNG at required sizes using design tools or CLI:
   - macOS: `rsvg-convert` or `sips`
   - Cross-platform: ImageMagick, Sharp (Node.js)
3. Verify quality at each size
4. Compress PNGs without quality loss (pngquant, optipng)

## Quality Checklist

Before delivering icon assets:

- [ ] Clear and recognizable at 29x29 px
- [ ] Maintains visual impact at 1024x1024 px
- [ ] No transparency (iOS requirement)
- [ ] Critical content within safe zones
- [ ] Tested on light and dark backgrounds
- [ ] Color contrast meets accessibility standards (4.5:1)
- [ ] Distinct from competitor apps
- [ ] Matches brand guidelines
- [ ] Correct file formats for each platform
- [ ] Optimized file sizes

## Common Mistakes to Avoid

1. **Too Complex**: Details lost at small sizes
2. **Transparency on iOS**: Creates floating appearance
3. **Pre-rounded Corners**: Platforms apply masks automatically
4. **Text Repetition**: App name appears below icon
5. **Photos/Screenshots**: Don't scale well
6. **Generic Symbols**: Blend in with competitors
7. **Ignored Safe Zones**: Content clipped on Android
