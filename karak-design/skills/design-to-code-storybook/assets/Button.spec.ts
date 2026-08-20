/*
 * Button.spec.ts — example-stack verification template (Playwright).
 *
 * This is the third member of the colocation triad (Component + story + SPEC),
 * and the fixture for load-bearing principle #4: VERIFY WHAT RENDERS, NOT WHAT
 * YOU WROTE (references/round-trip-workflow.md#verification,
 * failure-catalog.md#verification). It exists precisely because token-driven
 * styling can only be trusted when checked against a real browser's computed
 * styles — never against CSS text or class strings.
 *
 * Patterns demonstrated (each maps to a recorded failure class):
 *  - Load the PRODUCTION component via the Storybook iframe at a stable story ID
 *    (iframe.html?id=atoms-button--primary) — the ID is a contract (catalog-norms.md#naming).
 *  - Wait on SEMANTIC VISIBILITY, never a fixed sleep (Storybook compiles on
 *    demand; a timeout can assert against the loading screen — failure catalog
 *    "Fixed sleeps silently capture the wrong frame").
 *  - SETTLE until the design tokens have resolved before reading a computed
 *    style (async token-injection race — failure catalog "Token-resolution race
 *    in the browser").
 *  - PIN the rendered theme for exact-color assertions. When tokens are driven by
 *    a Storybook theme global (data-theme, as here), determinism comes from the
 *    default `theme` global; additionally pinning the OS `colorScheme` guards the
 *    separate case where tokens key off `prefers-color-scheme` (failure catalog
 *    "Environment-dependent color assertions").
 *
 * Adapt to the host stack's runner (Vitest browser mode, Cypress, WebdriverIO):
 * the tool changes, the four patterns above do not. See assets/stack-adaptation.md.
 */
import { test, expect, type Page } from "@playwright/test";

const SB = "http://localhost:6006";
const storyUrl = (id: string) => `${SB}/iframe.html?id=${id}&viewMode=story`;

// Open a story and wait for BOTH the element to be visible AND the design
// tokens to have resolved — the shared "settle" helper the prose refers to.
// Reuse it in every spec so all specs wait the same way.
async function gotoStory(page: Page, id: string, sel = "button") {
  await page.goto(storyUrl(id));
  const el = page.locator(sel);
  await expect(el).toBeVisible(); // semantic wait, not a sleep
  await page.waitForFunction((s) => {
    const node = document.querySelector(s);
    if (!node) return false;
    // Detect resolution by reading the CUSTOM PROPERTY itself: an undefined
    // token reads as "" from getPropertyValue, and resolves to a concrete value
    // once tokens.css is applied. Do NOT infer resolution from backgroundColor —
    // an unresolved var() is invalid-at-computed-value-time and falls back to the
    // initial value `transparent` = "rgba(0, 0, 0, 0)", which is itself a valid
    // rgb string, so a `startsWith("rgb")` check would pass in the very state it
    // means to guard against. (Chromium — the Playwright/Storybook default —
    // returns the SUBSTITUTED value for a chained custom property, so this reads
    // "#0a6fd8" once resolved; for maximum cross-browser portability the sample's
    // probe+sentinel pattern, e2e/palette.spec.ts commit 7ada269, applies the
    // token to a real property with a sentinel fallback instead.)
    return getComputedStyle(node).getPropertyValue("--color-accent").trim() !== "";
  }, sel);
  return el;
}

// Pin the OS color scheme too. Harmless here (these tokens key off data-theme via
// the default `theme` global, not prefers-color-scheme), but it keeps the pattern
// portable to catalogs whose tokens DO react to prefers-color-scheme.
test.use({ colorScheme: "light" });

test("primary button renders the accent background from its semantic token", async ({ page }) => {
  const el = await gotoStory(page, "atoms-button--primary");
  // Assert on the RENDERED computed style, not on the class string.
  // --color-accent -> --blue-500 (#0a6fd8) in light theme.
  await expect(el).toHaveCSS("background-color", "rgb(10, 111, 216)");
  // Layout metric: md size keeps the 44px min touch target. (Assumes
  // box-sizing: border-box — on by default via Tailwind preflight; a host that
  // disables preflight would measure padding on top of the height token.)
  const box = await el.boundingBox();
  // toBeCloseTo, not toBe: boundingBox can return sub-pixel values under a
  // non-integer devicePixelRatio even when the height token is an integer.
  expect(box?.height).toBeCloseTo(44, 0);
});

test("disabled button drops interactivity (rendered state, not asserted class)", async ({ page }) => {
  const el = await gotoStory(page, "atoms-button--disabled");
  await expect(el).toBeDisabled();
  expect(Number(await el.evaluate((n) => getComputedStyle(n).opacity))).toBeLessThan(1);
});
