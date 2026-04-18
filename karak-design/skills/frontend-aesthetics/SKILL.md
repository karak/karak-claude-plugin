---
name: frontend-aesthetics
description: Use when generating, reviewing, or modifying frontend HTML/CSS/React code to detect and eliminate AI-generated design patterns ("AI slop") — purple gradients, Inter font, three-column icon cards, centered hero sections, cookie-cutter layouts. Fires on symptoms like generic aesthetics, lack of brand personality, distributional convergence toward safe defaults.
---

# Frontend Aesthetics: AI-Smell Detection & Elimination

## Overview

AI-generated frontends suffer from **distributional convergence** — LLMs default to the statistical center of their training data, producing interfaces that are instantly recognizable as machine-made. This skill is a diagnostic checklist that identifies these "AI smells" and provides concrete human-design alternatives.

**This is NOT a generative design guide.** It is a quality gate. Run this checklist against any frontend code — AI-generated or not — to catch and fix patterns that signal "no human designer touched this."

## When to Use

- Reviewing or generating frontend HTML/CSS/JSX/TSX
- User asks to "make it look more professional" or "less generic"
- You notice your output uses Inter, purple gradients, or three-column card grids
- After generating any landing page, dashboard, or component library
- When the result "works" but feels forgettable

## The AI-Smell Checklist

Run every item. If 3+ items trigger, the design needs intervention.

### 1. Typography Smells

| Smell | What to look for | Fix |
|-------|-------------------|-----|
| **Default font stack** | Inter, Roboto, Open Sans, Lato, Arial, system-ui as primary font | Pick a font with character: Playfair Display, Bricolage Grotesque, Cabinet Grotesk, Syne, Fraunces, IBM Plex Serif, Outfit, Geist |
| **Timid weight range** | Weights clustered around 400-600 | Use extreme contrast: 200 vs 800, or 100 vs 900 |
| **Uniform sizing** | Heading sizes step by 1.2-1.5x increments | Use dramatic jumps: 3x+ between body and display text |
| **Single typeface** | Everything in one sans-serif | Pair contrasting families: serif + mono, geometric + humanist, display + text |
| **No typographic hierarchy** | All text looks the same weight/size | Establish clear levels: oversized display, medium subhead, compact body, tiny caption |

**Quick test:** Cover the content. Can you tell the heading from the body just by shape? If not, the typography is flat.

### 2. Color Smells

| Smell | What to look for | Fix |
|-------|-------------------|-----|
| **The Purple Gradient** | `#667eea`, `#764ba2`, `bg-indigo-500`, purple-to-blue/pink linear-gradient | Choose a color with actual meaning: warm amber, deep teal, muted olive, burnt sienna, slate blue-gray |
| **White background default** | `#ffffff` or `#f8f9fa` as the only backgrounds | Use tinted whites (warm: `#faf8f5`, cool: `#f0f4f8`), dark modes, or colored surfaces |
| **Evenly distributed palette** | 3-5 colors used in equal amounts | Establish dominance: 60% base, 30% secondary, 10% accent. One color should own the page. |
| **Generic grays** | `#6b7280`, `#4b5563`, `#9ca3af` (Tailwind grays) | Tint your grays toward your brand hue. Pure gray = no personality. |
| **Gradient as decoration** | Gradients used because they look "modern" with no semantic purpose | Use color to communicate: state, hierarchy, emotion. If a solid color works, use it. |

**Quick test:** Squint at the page. Do you see one dominant color with sharp accents, or a timid wash of samey hues?

### 3. Layout Smells

| Smell | What to look for | Fix |
|-------|-------------------|-----|
| **The Holy Trinity** | 3-column grid of identical cards with icon + heading + paragraph | Break the grid: use 2 columns, asymmetric layouts, varied card sizes, or a single featured item with supporting list |
| **Centered everything** | Hero text centered, features centered, testimonials centered | Introduce alignment variety: left-aligned hero, right-aligned callout, staggered grid |
| **Uniform section rhythm** | Every section = 80px padding, same width, same structure | Vary section density: tight data sections, generous breathing room, full-bleed images, narrow text columns |
| **Card monoculture** | Every piece of content is a rounded-corner card on gray background | Mix formats: inline text, full-width banners, overlapping elements, bordered sections, floating callouts |
| **Predictable hero** | Big heading + subtitle + centered CTA button on gradient background | Try: split hero (text left, visual right), editorial hero (large type, no CTA), video background, angled sections, scroll-triggered reveal |

**Quick test:** Screenshot your page. Show it to someone for 2 seconds. Can they distinguish it from any other SaaS landing page? If not, the layout is generic.

### 4. Component Smells

| Smell | What to look for | Fix |
|-------|-------------------|-----|
| **Emoji as icons** | Using Unicode emoji (clipboard, people, chart) for feature icons | Use a custom icon set, SVG illustrations, or no icons at all — let typography do the work |
| **Identical card structure** | Every card has exactly: icon → h3 → p, same padding, same radius | Vary card anatomy: some with images, some text-only, some with metrics, some with quotes |
| **Button sameness** | All buttons = solid fill, 8px radius, same padding | Create button hierarchy: primary (bold), secondary (outline/ghost), tertiary (text link). Vary radius (pill, sharp, rounded). |
| **Shadow uniformity** | Same `box-shadow: 0 Npx Npx rgba(0,0,0,0.1)` everywhere | Use shadows semantically: elevated = interactive, flat = static. Vary blur, spread, color. Consider colored shadows. |
| **Generic testimonials** | Three quotes in identical cards, "Name, Title" format | Add photos, asymmetric layout, pull-quote style, video testimonials, or embed actual tweets/reviews |

### 5. Motion & Interaction Smells

| Smell | What to look for | Fix |
|-------|-------------------|-----|
| **translateY on hover** | Every card lifts up on hover with the same `translateY(-2px)` + shadow | Differentiate: scale for emphasis, background-color shift for selection, border-color for focus, subtle rotation for playfulness |
| **transition: all 0.3s ease** | Same generic transition on every element | Tailor: fast (150ms) for toggles, medium (250ms) for reveals, slow (400ms) for page transitions. Use specific properties, not `all`. |
| **No page-load choreography** | Page appears all at once, fully formed | Stagger element entry: header first, hero text fades in, cards cascade with `animation-delay`, background subtly shifts |
| **Hover-only interactivity** | Only hover states, no scroll effects, no micro-interactions | Add scroll-triggered reveals, active/pressed states, loading skeletons, success confirmations |

### 6. Atmosphere Smells

| Smell | What to look for | Fix |
|-------|-------------------|-----|
| **Flat solid backgrounds** | Pure white or light gray (#f8f9fa) sections with no depth | Layer: subtle gradients, noise/grain textures, geometric patterns, glassmorphism |
| **No texture** | Every surface is perfectly smooth | Add grain (`background-image: url(noise.svg)`), subtle borders, dot grids, line patterns |
| **Sterile whitespace** | Clean but clinical — whitespace without warmth | Tint the whitespace. Warm projects use cream/ivory (#faf8f5). Cool projects use blue-gray (#f0f4f8). |
| **No visual surprise** | Nothing unexpected — every element is exactly where you'd predict | Add one unexpected element: an oversized decorative letter, an angled section divider, an illustration that breaks the grid, a floating label |

## The Intervention Protocol

When smells are detected:

```
1. COUNT triggered smells
2. If 1-2: Minor tweaks — swap fonts, adjust colors
3. If 3-5: Moderate rework — rethink palette, layout structure, typography system
4. If 6+:  Full redesign — start with a mood/reference, build a design system first
```

**For any intervention:**

1. **Pick a reference.** Find 1-3 real websites (Awwwards, Dribbble, Mobbin) that match the desired aesthetic. Extract their patterns.
2. **Establish constraints.** Define what you will NOT use: "No Inter. No purple. No three-column cards."
3. **Build the system first.** Define CSS variables for colors, spacing, typography before writing any components.
4. **Apply the system.** Every element derives from the system. No one-off hex codes or magic numbers.

## Font Alternatives Quick Reference

Instead of defaulting to the same alternatives every time, rotate through these categorized options:

| Category | Options (rotate, don't repeat) |
|----------|-------------------------------|
| **Editorial/Serif** | Playfair Display, Fraunces, Crimson Pro, Lora, Libre Baskerville, DM Serif Display |
| **Geometric Sans** | Cabinet Grotesk, Outfit, Satoshi, General Sans, Switzer, Manrope |
| **Humanist Sans** | Bricolage Grotesque, Syne, Plus Jakarta Sans, Nunito Sans, Source Sans 3 |
| **Display/Statement** | Clash Display, Archivo Black, Unbounded, Space Grotesk, Sora |
| **Monospace/Technical** | JetBrains Mono, Geist Mono, IBM Plex Mono, Fira Code, Space Mono |

**IMPORTANT:** Do not converge on the same "safe alternative" (e.g., always picking Space Grotesk or JetBrains Mono). Rotate. Each project should feel different.

## Color System Quick Reference

Instead of purple gradients, try palettes rooted in:

| Mood | Base | Accent | Background |
|------|------|--------|------------|
| **Warm Professional** | Charcoal `#2d2a26` | Amber `#d4a853` | Warm white `#faf8f5` |
| **Cool Technical** | Slate `#1e293b` | Cyan `#06b6d4` | Blue-gray `#f0f4f8` |
| **Organic/Natural** | Forest `#1a3a2a` | Sage `#87a878` | Linen `#f5f0eb` |
| **Bold Editorial** | Near-black `#0a0a0a` | Vermillion `#e63b2e` | Off-white `#fafaf9` |
| **Muted Sophisticated** | Dark plum `#2e1f3b` | Dusty rose `#c4a0a0` | Pale lavender `#f4f0f7` |
| **Industrial/Utility** | Graphite `#333333` | Safety orange `#ff6b2b` | Concrete `#e8e6e3` |

## Common Rationalizations

| Excuse | Reality |
|--------|---------|
| "Inter is a good font" | Good =/= distinctive. It's the Helvetica of AI — technically fine, aesthetically invisible. |
| "Purple is our brand color" | Then use YOUR purple with YOUR typography in YOUR layout. Not `#667eea` with Inter in a centered hero. |
| "This layout is clean" | "Clean" is often code for "I didn't make any design decisions." Clean WITH personality is the goal. |
| "Users don't care about fonts" | Users don't consciously notice fonts. They unconsciously feel "cheap" vs "polished." Typography is the single biggest signal of design quality. |
| "Rounded corners are modern" | Uniform 12px radius on everything is not a design choice. Varying radius (4px for inputs, 8px for cards, 24px for pills, 0px for hero images) is. |
| "The gradient looks nice" | The gradient looks like every other AI-generated page. Coincidence is not aesthetics. |
| "Three columns works well for features" | It works. So does every other SaaS page. The question is not "does it work" but "is it memorable." |

## Real-World Impact

Professional designers differentiate through:
- **Intentional imperfection:** Slight asymmetry, organic shapes, hand-drawn elements
- **Cultural specificity:** Color and typography choices rooted in context, not defaults
- **Sensory richness:** Texture, grain, depth — surfaces that feel material, not digital
- **Emotional range:** Warmth, tension, calm, energy — not just "clean and modern"
- **Restraint:** Knowing when NOT to add effects. A single well-placed animation > scattered hover effects everywhere

The goal is not maximalism or minimalism. It is **intentionality** — every choice should be a choice, not a default.
