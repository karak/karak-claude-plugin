# Round-Trip Workflow

How change flows between design and code without drift, and exactly which Figma
skill handles which leg. This skill governs *where a change lands in the catalog
and what rule applies*; the Figma skills perform the per-component mechanics.
Invoke them — do not re-implement them here.

## The two legs

```
                design->code (implement a design)
   Figma  ───────────────────────────────────────────▶  Code catalog
  (design                                                (Storybook = SSoT
   source                                                 in code world)
   of truth)  ◀───────────────────────────────────────
                code->design (build/refresh the DS in Figma)
```

Both legs converge on the same done-state: Storybook and the automated checks
agree with the intent, and any deviation is recorded rather than silent.

## Leg 1 — design -> code (implement or update a component from a design)

Use when a design exists (or changed) and code must follow.

> **Design source.** The source of truth for this leg is normally Figma. A
> Claude Design (or any other) export is consumed the *same way*: treat it as the
> design intent to reproduce and run the identical steps below (reuse tokens,
> land in catalog conventions, verify) — only step 1's extraction mechanism
> differs (Figma has `get_design_context`; for a static export you read the
> provided design/spec directly). The catalog norms and verification are
> source-agnostic.

1. **Pull the design context** with `figma-design-to-code`
   (`get_design_context` on the node) when the source is Figma. Treat its output
   as a *reference*, not final code — it comes back as generic React/Tailwind that
   you must adapt.
2. **Reuse before you create.** Check the catalog for an existing component,
   layout, or — above all — an existing **semantic token** that matches the design
   intent. Map the design's values to catalog tokens; do not introduce a new raw
   value that duplicates a token you already have.
3. **Land it in the catalog conventions.** Place/extend the component per
   [catalog-norms.md](catalog-norms.md): colocated files, token-bound enum props,
   one story per comp/state, full `argTypes`.
4. **Verify against what renders** (see [verification](#verification)), then
   record any intentional visual change in the spec and pin it in a test.
5. If the design's component is published and you want the link to persist, map
   it with `figma-code-connect` so future design->code lookups resolve to your
   catalog component directly.

Honor the `get_design_context` hint priority (Code Connect > component docs >
annotations > tokens > raw hex); the `figma-design-to-code` skill (invoke it by
name via the Skill tool) owns the details of that call.

## Leg 2 — code -> design (build or refresh the design system in Figma)

Use when the catalog is ahead of Figma — new tokens/components exist in code and
Figma should reflect them.

1. **Delegate the build to `figma-generate-library`.** It runs the phased
   Figma-side workflow (variables before components, one component per page,
   scopes + code syntax on every variable). Note it requires the `figma-use`
   skill co-loaded — that companion carries the Plugin API mechanics every
   `use_figma` call depends on — so load both. Your job from this skill is to feed
   `figma-generate-library` the *catalog's* token architecture and naming so the
   Figma variables mirror your semantic tiers 1:1.
2. **Respect the external-quota reality.** Figma MCP write capacity is
   metered per seat/plan and can hard-stop mid-build (the reference sample
   exhausted a 6-calls/month View-seat quota after writing 36 variables, blocking
   all component/screen generation — [failure-catalog.md](failure-catalog.md#quota)).
   Before starting: confirm the seat type and per-call cost, and design the write
   as a **batched runbook** that accomplishes the maximum per call, so a quota
   stop leaves you at a coherent checkpoint rather than half a component.
3. **Keep the vocabulary aligned.** Variable code-syntax must use the real CSS
   variable names (`var(--color-accent)`), so a designer inspecting Figma sees the
   exact token an engineer reads. This is the code->design half of "tokens are the
   shared language."

<a id="verification"></a>
## Verification (applies to both legs)

Verification is the guardrail that makes "aligned by construction" true rather
than aspirational. The rule from principle #4: **check what renders, not what you
wrote.**

- **Rendered DOM + computed styles, via the Storybook iframe.** Open the story at
  `iframe.html?id=<story-id>` in a real browser (Playwright) and assert on
  `getComputedStyle` / layout metrics. A JSDOM-style environment cannot resolve
  `var()`, so token-driven styling *must* be checked in a real browser.
- **Never assert on CSS text or class strings.** Matching `class="bg-accent"`
  proves a string, not a pixel; the pixel is what the designer signed off on.
- **Wait on semantic visibility, never a fixed sleep.** Storybook compiles
  stories on demand; a `waitForTimeout` can screenshot the loading screen. Wait for
  the actual element (`expect(el).toBeVisible()` by role/text), and for
  token-driven color, poll until `var()` has resolved to a concrete value (a small
  "settle" helper) before asserting.
- **Pin the environment for color-exact assertions.** Exact `rgb()` checks assume
  a color scheme; pin it (`colorScheme: 'light'`) or the check fails on a
  dark-mode runner.

See [failure-catalog.md#verification](failure-catalog.md#verification) for the
concrete incidents these rules come from.

## Deviations are recorded, not silent

The round-trip only stays trustworthy if disagreements between design and code
are made explicit:

- An **intentional** visual change (e.g. a line-height that differs from the
  "equivalent refactor" you claimed) is documented in the spec and **pinned in a
  test**, so it is verified rather than discovered later.
- A **known limitation you are deferring** (e.g. an accent that misses WCAG AA)
  goes into an issues ledger with the *measured* value, the reason it is out of
  scope now, and a candidate fix — not left as an unmarked failing check that
  everyone learns to ignore.
