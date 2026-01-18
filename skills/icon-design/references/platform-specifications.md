# Platform Icon Specifications

## Apple iOS/iPadOS

### App Store Submission
- **Size**: 1024 × 1024 px (single master file)
- **Format**: PNG
- **Color Space**: sRGB or Display P3 (for wider color range)
- **Transparency**: NOT allowed (must be fully opaque)
- **Corners**: Do NOT round corners - Apple applies ~20% radius squircle mask automatically

### Runtime Sizes (Auto-generated from 1024px master)
| Device | Size (px) | Scale |
|--------|-----------|-------|
| iPhone (Home screen) | 180×180 | @3x |
| iPhone (Home screen) | 120×120 | @2x |
| iPad Pro | 167×167 | @2x |
| iPad, iPad mini | 152×152 | @2x |
| App Store | 1024×1024 | @1x |
| Spotlight (iPhone) | 120×120 | @3x |
| Spotlight (iPhone) | 80×80 | @2x |
| Settings | 87×87 | @3x |
| Settings | 58×58 | @2x |
| Notification | 60×60 | @3x |
| Notification | 40×40 | @2x |

### iOS 18+ Dark Mode & Tinted Icons
- Light mode: Standard colorful icon
- Dark mode: Design without solid background (Apple provides dark background)
- Tinted mode: Monochrome version for user-selected tint colors

### Apple Watch Icons
| Use Case | Size (px) |
|----------|-----------|
| Home Screen (38mm) | 80×80 |
| Home Screen (40mm) | 88×88 |
| Home Screen (41mm) | 92×92 |
| Home Screen (44mm) | 100×100 |
| Home Screen (45mm) | 102×102 |
| Notification Center | 48×48 |
| Short Look | 172×172 |
| App Store | 1024×1024 |

### macOS Icons
| Size (px) | Scale |
|-----------|-------|
| 16×16 | @1x |
| 32×32 | @1x, @2x |
| 64×64 | @1x, @2x |
| 128×128 | @1x, @2x |
| 256×256 | @1x, @2x |
| 512×512 | @1x, @2x |
| 1024×1024 | @1x |

---

## Android (Google Play)

### Play Store Submission
- **Size**: 512 × 512 px
- **Format**: PNG (32-bit with alpha)
- **Color Space**: sRGB
- **Max File Size**: 1024 KB
- **Shape**: Full square (NO rounded corners - Google applies mask)
- **Shadow**: None (Google handles shadows dynamically)

### Adaptive Icons (Android 8.0+)
Adaptive icons consist of two layers that the system combines:

| Layer | Size | Requirements |
|-------|------|--------------|
| Foreground | 108 × 108 dp | Can have transparency |
| Background | 108 × 108 dp | Must be fully opaque |
| Safe Zone | 66 × 66 dp | Critical content area (centered) |

#### Pixel Dimensions for Adaptive Icons
| Density | Canvas Size | Safe Zone |
|---------|-------------|-----------|
| mdpi (1x) | 108×108 px | 66×66 px |
| hdpi (1.5x) | 162×162 px | 99×99 px |
| xhdpi (2x) | 216×216 px | 132×132 px |
| xxhdpi (3x) | 324×324 px | 198×198 px |
| xxxhdpi (4x) | 432×432 px | 264×264 px |

### Monochrome/Themed Icons (Android 13+)
- Provide single-layer monochrome version
- System applies user's wallpaper-derived colors
- Design with clear silhouette that works in any color

### Legacy Launcher Icons (Android 7.1 and below)
| Density | Size (px) |
|---------|-----------|
| mdpi | 48×48 |
| hdpi | 72×72 |
| xhdpi | 96×96 |
| xxhdpi | 144×144 |
| xxxhdpi | 192×192 |

---

## Web Favicons & PWA Icons

### Favicon Sizes
| Size | Use Case |
|------|----------|
| 16×16 | Browser tabs |
| 32×32 | Taskbar shortcuts |
| 48×48 | Windows site icons |
| 180×180 | Apple Touch Icon |
| 192×192 | Android Chrome |
| 512×512 | PWA splash screens |

### PWA Manifest Icons
```json
{
  "icons": [
    { "src": "icon-72.png", "sizes": "72x72", "type": "image/png" },
    { "src": "icon-96.png", "sizes": "96x96", "type": "image/png" },
    { "src": "icon-128.png", "sizes": "128x128", "type": "image/png" },
    { "src": "icon-144.png", "sizes": "144x144", "type": "image/png" },
    { "src": "icon-152.png", "sizes": "152x152", "type": "image/png" },
    { "src": "icon-192.png", "sizes": "192x192", "type": "image/png" },
    { "src": "icon-384.png", "sizes": "384x384", "type": "image/png" },
    { "src": "icon-512.png", "sizes": "512x512", "type": "image/png" }
  ]
}
```

---

## SVG Export Guidelines

### When to Use SVG
- Web favicons and PWA icons
- Scalable marketing assets
- Documentation and style guides
- Vector-based design systems

### SVG Best Practices
- Optimize with SVGO or similar tools
- Use viewBox for scalability: `viewBox="0 0 1024 1024"`
- Embed fonts or convert to paths
- Remove unnecessary metadata
- Keep file size under 100KB for web use

### PNG vs SVG Decision Matrix
| Use Case | Recommended Format |
|----------|-------------------|
| App Store submission | PNG |
| Android adaptive icons | PNG or Vector Drawable |
| Web favicon | SVG + PNG fallbacks |
| PWA icons | PNG |
| Design system | SVG source + PNG exports |
| Marketing materials | SVG (scalable) |
