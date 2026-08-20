# Catalog Norms

The structural conventions that make a catalog navigable, verifiable, and
aligned-by-construction. These are stack-agnostic; the code fragments show the
example stack (React / Shadcn / Tailwind / Vite) and, where instructive, the Vue
3 reference sample. Translate the idea, not the syntax — see
[stack-adaptation.md](../assets/stack-adaptation.md).

## Table of contents

- [Directory structure & colocation](#structure)
- [Naming & story IDs](#naming)
- [Tokens: three tiers + cascade layers](#tokens)
- [Token-bound enum prop API](#props)
- [argTypes as the prop spec](#argtypes)
- [Storybook as the hub](#storybook-hub)

<a id="structure"></a>
## Directory structure & colocation

Organize by Atomic Design depth (atoms -> molecules -> organisms -> templates ->
pages) and **colocate** each component's implementation, story, and spec in one
folder. Colocation keeps the three artifacts that describe a component — its
code (how), its story (what it looks like across states), and its spec (what it
guarantees) — in one place, so a change touches one folder and reviewers see the
whole contract at once.

```
src/components/
  atoms/
    Button/
      Button.tsx          # implementation (Vue sample: Button.vue)
      Button.stories.tsx  # one story per design comp / state
      Button.spec.ts      # rendered-DOM assertions
  molecules/
  organisms/
  templates/
  pages/
src/styles/
  tokens.css              # the token layers (see below)
```

Build in dependency order: atoms before the molecules that compose them. A
molecule whose atoms are not yet token-bound will inherit their raw values.

<a id="naming"></a>
## Naming & story IDs

The story ID is not cosmetic — it is the address your automated checks use to
load a component in isolation. Design the hierarchy so the ID is stable and
predictable.

- **Story title** = the atomic path: `Atoms/Button`, `Molecules/SearchField`.
- **Story ID** derives from title + story name: `atoms-button--primary`. Your
  E2E/visual checks open the Storybook iframe directly at
  `iframe.html?id=atoms-button--primary`, so treat IDs as a contract — renaming a
  story breaks every check that targets it.
- **One design comp = one story.** If a design has a "primary" and a "disabled"
  comp, those are two named stories under the same component, not two components.

<a id="tokens"></a>
## Tokens: three tiers + cascade layers

Tokens are the vocabulary design and code share. Structure them in three tiers
with a **one-way dependency**, so intent is separable from raw values and theming
never touches components.

| Tier | Example | Who may reference it |
|------|---------|----------------------|
| **Primitive** | `--blue-500: #3b82f6` | Only the semantic tier. Never a component. |
| **Semantic** | `--color-accent`, `--label-primary` | Components, and other semantic tokens. |
| **Component** | `--button-bg-pressed` | Only its own component. Create lazily. |

Rules that keep this honest:

- **Components read only the semantic tier.** A component that reaches for a
  primitive (`--blue-500`) or a raw value has broken the vocabulary — theming and
  rebranding will skip it.
- **Create component tokens lazily.** If a semantic token expresses the need,
  use it; only introduce a component token when no semantic token fits. Every
  premature component token is a value that theming must now remember to override.
- **Theme/brand = semantic-layer overrides only.** Switch themes by overriding
  semantic tokens under a selector (`html[data-theme="dark"]`), leaving
  primitives and components untouched. The test of a correct token structure:
  adding a new theme or brand palette requires **zero component edits**. The
  reference sample proved this twice (adding high-contrast, then a warm palette).

### Multi-axis theming: use cascade layers, not specificity

When you have more than one independent axis (e.g. theme × brand-palette),
**order the axes with CSS `@layer`, not selector specificity.** Specificity ties
"who wins" to how the selector was written, so a high-contrast rule can silently
lose to a same-specificity palette rule depending on source order. Layers fix
precedence by *origin*:

```css
@layer base, palette, theme, overrides;
/* later layer always wins, regardless of selector specificity */
```

Two rules the reference sample codified for a two-axis (theme × palette) system:

- **R1** — a palette owns a token only where it composes with the theme; put the
  owned color on the composed cell, not the single-axis block.
- **R2** — a maximal mode (e.g. high-contrast) ignores the palette axis and
  enumerates its tokens completely, so no palette rule can bleed through.

And two traps this exposed (both in [failure-catalog.md](failure-catalog.md)):
a pre-existing `:root` rule sitting *outside* the layers overrides everything
inside them; and stripping a color from a single-axis block per R1 can leave the
"no attribute set" state (JS not yet run) unreadable — always keep a self-contained
fallback.

<a id="props"></a>
## Token-bound enum prop API

A catalog's props are a governance surface, not a convenience API. Keep them
**discrete and token-bound** so design variants and code props stay 1:1 and no
caller can smuggle in an off-system value.

- Every prop is an **enum or boolean** — `variant`, `size`, `shape`, `status` —
  each value mapping to a design variant and a set of semantic tokens.
- **No raw pass-through.** No arbitrary color, arbitrary pixel size, or
  `style`/`class` pass-through props. Those are the escape hatches through which a
  catalog decays into one-off styling.
- **New prop's default = current behavior.** When you add a prop, its default
  must reproduce the existing rendering, so the change is backward-compatible and
  reviewable as additive.

This 1:1 discipline is what lets a Figma variant, an `argTypes` control, and a
code prop describe the same axis — the precondition for Code Connect to map them.

<a id="argtypes"></a>
## argTypes as the prop spec

Write `argTypes` for every **catalog** prop with a control, a description, and
the type + default in the table. Storybook Docs then renders as a
**designer-readable API specification** — the same surface serves engineering
(the contract), design (what can vary), and QA (what to exercise). A catalog prop
absent from `argTypes` is a prop no reviewer can see, so treat the `argTypes`
block as part of the component's public definition, not documentation you add
later. Native HTML passthrough attributes (`onClick`, `type`, `aria-*`) need not
be enumerated — spec the catalog-specific props, not the platform's.

<a id="storybook-hub"></a>
## Storybook as the hub

Storybook earns "single source of truth in the code world" only if a story is a
faithful stand-in for the app. Two configuration moves make it so:

- **Apply the theme with the app's own mechanism.** In `preview`, drive the
  theme from the *same* mechanism the app uses (the same `data-theme` on the
  document root — plus `data-palette` or another attribute only if you actually
  run a second axis, the same hook), via a single unified decorator. If Storybook
  themes differently from the app, the review surface lies. Add a toolbar global
  per axis so a reviewer can sweep the matrix (e.g. light / dark) on any story.
- **Inject app context so page-level stories render standalone.** Provide the
  store and an in-memory router in `preview` setup, so organism/page stories
  render without a live backend. This is what lets a whole screen be a story, not
  just leaf atoms.

Storybook then simultaneously is: the designer's review surface, the API docs
(`argTypes`), and the fixture that [rendered-DOM verification](failure-catalog.md#verification)
loads via the iframe. See the [preview template](../assets/) for the concrete
wiring.
