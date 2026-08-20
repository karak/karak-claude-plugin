# Stack Adaptation

Read this first when the host project is **not** React / Shadcn / Tailwind /
Vite. The templates in this folder are one concrete stack; the reference sample
that produced every lesson in this skill was **Vue 3 + plain CSS custom
properties** — deliberately different, to prove the norms transfer even when the
syntax does not.

## What is stack-agnostic (always applies)

These are the norms — carry them into any stack unchanged:

- One design comp = one story; the story renders the **production** component.
- Three-tier tokens (primitive -> semantic -> component), one-way dependency,
  components read only the semantic tier.
- Multi-axis theming via cascade layers (`@layer`), not selector specificity.
- Token-bound enum props; no raw color/size/style pass-through.
- `argTypes` (or your Storybook framework's equivalent) as the prop spec.
- Verify against rendered DOM / computed styles in a real browser; never assert
  on CSS text.
- Storybook applies theme with the **app's own mechanism**, and injects app
  context (store/router) so page stories render standalone.

## What is stack-specific (translate these)

| Concern | React/Tailwind template | Translate to host by… |
|---------|-------------------------|-----------------------|
| Component file | `Button.tsx` (function component) | Vue SFC `Button.vue`, Svelte `.svelte`, etc. |
| Story format | CSF3 `.stories.tsx` | The Storybook framework for the host (`@storybook/vue3-vite`, `@storybook/svelte-vite`, …) |
| Styling | Tailwind classes bound to CSS vars | Whatever the host uses — CSS Modules, vanilla-extract, plain CSS — as long as it reads semantic tokens |
| Token file | `tokens.css` (`@layer` + custom props) | Same CSS custom-property + `@layer` structure works everywhere; the *consumption* differs |
| Preview wiring | `preview.tsx` decorator + globals | Host framework's `preview` API; the decorator logic (apply theme like the app) is identical |
| Verification spec | `Button.spec.ts` (Playwright, iframe + computed style) | Any real-browser runner (Vitest browser mode, Cypress, WebdriverIO); the four patterns (story-ID targeting, semantic-visibility wait, var() settle, colorScheme pin) are the invariant, the runner API is not |

## How to adapt

1. Detect the host stack (framework, styling system, Storybook builder, test
   runner) from its `package.json` and config files.
2. Take the **structure and rules** from these templates, re-express the
   **syntax** in the host's idioms, and match the surrounding code's conventions.
3. Keep the token file's `@layer` structure as-is — CSS custom properties and
   cascade layers are framework-independent; only how components *read* the tokens
   changes.
4. If the host already has components/tokens, extend its conventions rather than
   imposing these names wholesale (the norms are the goal, not the specific
   identifiers).
