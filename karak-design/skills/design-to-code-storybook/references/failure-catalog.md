# Failure Catalog

Real failure classes from building a design-to-code Storybook catalog. Each entry
is **two layers**: an *abstract principle* that transfers to any stack, and a
*concrete case* from the reference sample (`design-to-code-demo`, a Vue 3 / Vite /
Storybook 8 repo) with the commit hash or file that proves it. Use this as the
checklist before declaring a change done: if your change touches one of these
areas, confirm you have not re-created the failure.

> Provenance note: commit hashes and paths are from the reference sample repo,
> cited so a reviewer can verify each lesson at its source. The *principle* is
> what you carry into a different stack; the *case* is evidence, not a template to
> copy verbatim.

## Table of contents

- [Verification failures](#verification)
- [Token & design-data failures](#tokens)
- [Multi-axis CSS failures](#css)
- [Round-trip / external-quota failures](#quota)
- [Toolchain traps](#toolchain)
- [Test-hygiene failures](#test-hygiene)

<a id="verification"></a>
## Verification failures

### Fixed sleeps silently capture the wrong frame

- **Principle.** A `waitForTimeout` before a screenshot or assertion is a bet
  that rendering finished in time. When it loses, you capture a loading/compiling
  frame and bake it in as the baseline — a *silent* corruption, because the test
  still "passes." Wait on a semantic signal (the element is visible, the token has
  resolved), never on a clock.
- **Case.** Storybook compiles stories on first access; ~40% of the sample's
  screenshot baselines were the Storybook loader, taken after a fixed 300ms sleep.
  Fixed sleeps were replaced with per-story `expect(el).toBeVisible()` by
  role/text, image-decode waits, and `--workers=1` to preserve the compile cache;
  all 14 re-captured (commit `1a39acc`).

### "Equivalent refactor" that isn't, caught only by review

- **Principle.** Claiming a change is visually equivalent is itself a claim to be
  verified. A blind reviewer (or a rendered-DOM diff) is what catches the values
  you changed without noticing. Make intentional changes explicit and pin them.
- **Case.** A token-ization sold as "appearance-equivalent" actually shifted
  line-heights (Button 1.2->22px, Badge 1.4->16px, Input normal->22px). A final
  blind review flagged the spec as false; the fix documented line-height as an
  intended HIG change and pinned computed line-height in E2E (commit `a37cf60`).

### Environment-dependent color assertions

- **Principle.** An exact color assertion silently assumes the runner's color
  scheme. Pin the scheme, or the same test that passes locally fails on a
  dark-mode CI machine.
- **Case.** Exact `rgb()` assertions assumed Light tokens and broke on dark-OS
  runners; fixed by pinning `colorScheme: 'light'` in the test (commit `f529763`,
  which also recorded that one reviewer flag was a false positive).

### Token-resolution race in the browser

- **Principle.** CSS custom properties injected asynchronously are not resolved
  the instant the DOM appears. Reading a computed style too early yields the
  unresolved `var()`. Poll until the value is concrete, and share that settle
  logic so every spec waits the same way.
- **Case.** `var()` was read before resolution in the theme spec, then the same
  flake recurred in the palette spec; fixed with a requestAnimationFrame settle
  loop, later extracted into a shared helper (commits `7ada269`, `2860075`).

<a id="tokens"></a>
## Token & design-data failures

### Transcription errors in unconsumed tokens hide from tests

- **Principle.** A token no component reads yet is invisible to your test net. A
  wrong transcribed value (a tracking, a line-height) sits latent until something
  consumes it. Cross-check transcribed design values against the design source in
  review, or generate them rather than hand-typing.
- **Case.** A HIG tracking token was defined `0.0019em` instead of `0.019em` — a
  10x error that no test caught because nothing consumed it; found in code review
  and corrected, with the spec table synced afterward (commits `beeafec`,
  `6298c11`).

### Accent/text contrast deferred without a record

- **Principle.** Measure WCAG contrast for accent × text at introduction. If you
  must ship below AA, that is a *recorded* decision with the measured ratio and a
  candidate fix — not an unmarked shortfall that surfaces months later.
- **Case.** The cool accent measured 4.02:1 (below the 4.5:1 AA threshold) but was
  consciously deferred to honor HIG systemBlue, logged as issue RI-001 with the
  measurement and candidate; closed 8 days later via TDD (RED contrast assertion ->
  darken tokens -> GREEN), evidence under `docs/superpowers/evidence/ri-001/`
  (commit `af919af`).

<a id="css"></a>
## Multi-axis CSS failures

### Specificity-based precedence collapses under multiple axes

- **Principle.** When two independent axes (theme, brand palette) both style a
  component, plain selector specificity makes "who wins" depend on how selectors
  were written and their source order — so a maximal mode can lose to a palette
  rule. Fix precedence by *origin* with `@layer`.
- **Case.** A cool/warm palette axis built on attribute-selector specificity drew
  five-plus BLOCKERs from an architecture review: high-contrast couldn't beat warm,
  dark×warm was source-order-dependent, cool was double-defined. The spec was
  rewritten onto `@layer` with explicit R1/R2 declaration rules (commit `33294e0`).

### CSS that assumes a JS-set attribute breaks in the bare state

- **Principle.** If your color scheme depends on an attribute JS applies
  (`data-palette`), the "attribute not yet set" state (JS not run, hydration
  pending) must still be readable. Keep a self-contained fallback on the
  single-axis block.
- **Case.** Stripping colors from a single-attribute dark block (per rule R1) left
  a dark-OS, no-`data-palette` state rendering white-on-white; fixed by restoring
  cool fallbacks on owned tokens in the single-attr dark block (commit `b822667`).

### A rule outside the layers overrides everything inside them

- **Principle.** An unlayered normal declaration (a leftover `:root {}`) always
  beats layered ones regardless of layer order — in the cascade, unlayered normal
  styles rank above all named layers within the same origin. When you adopt
  `@layer`, move existing global rules into a layer or they silently neutralize
  the whole system.
- **Case.** The `@layer` migration (`e687248`) wrapped the token declarations into
  `@layer base/palette/theme/overrides` while deliberately leaving the non-token reset
  unlayered — precisely because a *token* rule left outside the layers would
  outrank every named layer and neutralize the color-axis override system. The
  commit guards against this hazard by construction (its message: "Non-token CSS
  stays unlayered intentionally"); read it as a designed-in precaution, not as the
  record of a bug that shipped.

<a id="quota"></a>
## Round-trip / external-quota failures

### External SaaS quota is the real rate limiter, not the API

- **Principle.** For the code->design leg, the binding constraint is often the
  Figma seat/plan write quota, not technical capability. Confirm seat type and
  per-call cost *before* starting, and design writes as a batched runbook that
  reaches a coherent checkpoint per call, so a mid-run stop doesn't strand you with
  half a component.
- **Case.** Writing 36 Figma Variables exhausted a View-seat quota of 6 calls/month,
  blocking all component/screen generation. The plan was rewritten as an "ON HOLD"
  ≤6-call runbook to run once after a seat upgrade
  (`docs/00_management/figma-to-code-plan.md`).

<a id="toolchain"></a>
## Toolchain traps

These fail quietly or with cryptic errors and cost disproportionate time. When you
hit one, write it into the host project's CLAUDE.md/gotchas so the next person
doesn't re-pay. (The sample maintained exactly such a running list in
`.remember/` and its CLAUDE.md.)

### Test-runner ↔ bundler major mismatch

- **Principle.** A test runner that transitively pulls an older major of the
  bundler alongside the project's newer major produces confusing config type
  errors. Pin the runner to the major that matches the bundler.
- **Case.** Vitest 2 dragged in Vite 5 beside the project's Vite 6, yielding a
  `defineConfig({ test })` type error; pinning Vitest 3 resolved it (recorded in
  `.remember/archive.md`).

### Storybook manager UI needs its own peer deps

- **Principle.** Storybook's manager UI is built with React even in a non-React
  project, so it needs `react`/`react-dom` as devDeps regardless of your app
  framework; without them the manager crashes on a cryptic exit code.
- **Case.** The Vue sample still required React devDeps or Storybook 8 exited 7
  (recorded in `.remember/archive.md`).

### Missing addon = silent no-op, not an error

- **Principle.** A custom toolbar global renders nothing — with no error — if the
  essentials addon is absent; and `main` config changes need a full restart (no
  HMR). Silent, not loud, so it wastes time until you suspect config.
- **Case.** The `globalTypes` toolbar silently didn't render until
  `@storybook/addon-essentials` was added in `main` (commit `4de3671`; also noted
  in `.remember/` for 2026-06-15).

### E2E webServer reuse races

- **Principle.** A Playwright config that manages its own webServer will race an
  already-running dev/Storybook server and time out. Split configs by purpose so
  local fast-iteration and CI don't fight over the server.
- **Case.** The sample kept three configs — `playwright.config.ts` (managed
  webServer, for CI), `playwright.reuse.config.ts` (no webServer, full suite, fast
  local runs), and `playwright.theme.config.ts` (theme/palette only, generous
  cold-compile timeouts) — each with the reason in a header comment.

<a id="test-hygiene"></a>
## Test-hygiene failures

### Scaffold placeholder tests that drift from the implementation

- **Principle.** A test written during scaffolding, before the feature is real,
  becomes a permanent red once the implementation diverges from the placeholder —
  and a suite with a "known failure you always ignore" erodes the credibility of
  every other check. Sync scaffold tests to the implementation when it lands, or
  delete them.
- **Case.** A scaffold `login.spec.ts` expected an "Enter chat" button; the
  implementation shipped "Sign in" + validation, leaving the full suite red for 22
  days and forcing a per-run "known-excluded failure" annotation, logged as the
  still-open issue RI-002 (`docs/00_management/remaining_issues.md`).

### Keep an acceptance-criteria -> evidence map

- **Principle.** For a change worth verifying, maintain a table mapping each
  acceptance criterion to its raw evidence (log, test, commit SHA). It makes "is
  this actually done" answerable without re-deriving it, and it keeps screenshots
  honest by naming their role (visual-regression baseline, *not* an assertion).
- **Case.** The sample kept `docs/superpowers/plans/evidence-map.md` mapping eight
  acceptance criteria to raw logs/tests/SHAs, with screenshots explicitly scoped as
  visual baselines rather than pass/fail assertions.
