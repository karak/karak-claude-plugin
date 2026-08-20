/*
 * preview.tsx — Storybook preview template (example stack).
 *
 * Makes Storybook a FAITHFUL stand-in for the app (references/catalog-norms.md
 * #storybook-hub):
 *  1. Apply the theme with the SAME mechanism the app uses (data-theme on the
 *     document root) via ONE unified decorator — never a Storybook-only styling
 *     shim, or the review surface lies.
 *  2. Expose the theme as a toolbar global so a reviewer sweeps the matrix
 *     (here: light / dark) on any story.
 *  3. Inject app context (store, in-memory router) so organism/page stories
 *     render standalone, with no live backend.
 *
 * This example shows one axis (theme). If you add a second axis (e.g. a brand
 * palette), add a second global + attribute the same way.
 *
 * Adapt the framework API to the host (@storybook/vue3-vite etc.); the decorator
 * logic — "apply theme exactly like the app" — is identical across frameworks.
 */
import type { Preview } from "@storybook/react";
import "../src/styles/tokens.css";
// REQUIRED alongside tokens.css: also import your Tailwind entry (the file with
// `@tailwind base; @tailwind components; @tailwind utilities;`). tokens.css only
// defines the custom properties — it does NOT generate the utility classes
// Button.tsx uses (`bg-[var(--color-accent)]`, `h-[…]`, `disabled:opacity-50`).
// Omit it and stories render unstyled and the spec's exact-color/height
// assertions fail. Adjust the path to the host project's entry:
// import "../src/styles/tailwind.css";

// If the app applies theme through a hook/util, import and call THAT here instead
// of re-implementing it, so Storybook and the app cannot diverge.
function applyTheme(theme: string) {
  document.documentElement.setAttribute("data-theme", theme);
}

const preview: Preview = {
  globalTypes: {
    theme: {
      description: "Theme axis",
      toolbar: {
        icon: "circlehollow",
        items: ["light", "dark"],
        dynamicTitle: true,
      },
    },
  },
  initialGlobals: { theme: "light" },
  decorators: [
    (Story, ctx) => {
      applyTheme(ctx.globals.theme ?? "light");
      // Wrap with the app's real providers so page-level stories work standalone:
      //   return <StoreProvider store={makeTestStore()}>
      //            <MemoryRouter><Story /></MemoryRouter>
      //          </StoreProvider>;
      return <Story />;
    },
  ],
};
export default preview;
