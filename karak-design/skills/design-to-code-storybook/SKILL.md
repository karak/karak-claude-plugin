---
name: design-to-code-storybook
description: >-
  Build and operate a norm-governed, code-first component catalog with Storybook as
  the hub, so designers and engineers hand off through code (Figma or Claude
  Design) and keep improving in both directions (design->code and code->design).
  Use this whenever you are setting up a new component library / design system in
  a frontend repo, adding Storybook, establishing design tokens or naming
  conventions, wiring Figma-to-code or code-to-Figma sync, or reviewing an
  existing catalog that drifts from its designs. Reach for it even when the user
  only says "component library", "Storybook", "design tokens", "design system",
  "keep Figma and code in sync", "handoff", or "make our components match the
  designs" without naming this workflow. It sets the catalog architecture and
  round-trip process; per-component Figma mechanics are delegated to the Figma
  skills.
---

# Design-to-Code Storybook Catalog

## What this skill is for

A component catalog fails the moment design and code start telling different
stories. The usual fix — a human periodically re-syncing Figma against the
codebase — is exactly the labor this workflow removes. Instead you make the two
**aligned by construction**: one design comp maps to one Storybook story, that
story renders the *production* component itself (never a lookalike), and both
sides speak the same token vocabulary. When alignment is structural, "keeping in
sync" stops being a recurring task.

This skill owns the **catalog architecture and the round-trip process** — how
the catalog is structured, named, and governed, and how change flows
design->code and code->design without drift. It does **not** re-implement the
per-component Figma plumbing; that lives in the Figma skills, which this skill
calls as mechanisms (see [round-trip-workflow.md](references/round-trip-workflow.md)).

Use it in two situations, both first-class:

- **Bootstrap** — standing up a new catalog (toolchain, token layers, first
  components, Storybook as the hub).
- **Operation** — running an existing catalog: taking a design change into code,
  pushing a code change back to Figma, onboarding a new component, or repairing a
  catalog that has drifted.

## The five load-bearing principles

Everything below rests on these. Read them before touching files; they are the
"why" behind every convention in the references.

1. **Aligned by construction, not by syncing.** One comp = one story; the story
   renders the real component. If you ever find yourself hand-copying values from
   design into code (or code into design), stop and ask what structural link is
   missing — that manual step is the bug.
2. **Tokens are the shared language.** Design and code agree on *named* values
   (semantic tokens), not raw hexes or pixels. A component reads only the
   semantic layer; theming is a swap at that layer with zero component edits.
3. **Storybook is the single source of truth in the "code world."** It is
   simultaneously the designer's review surface, the component's API
   documentation, and the fixture that automated verification renders against.
4. **Verify what renders, not what you wrote.** Correctness is checked against
   the real browser's computed styles and layout metrics — never by reading CSS
   text or matching class strings, which prove nothing about the pixels.
5. **The catalog adapts to the host stack.** The conventions here are
   stack-agnostic. The bundled templates happen to be React / Shadcn / Tailwind /
   Vite, and the reference sample was Vue 3 — proof the *norms* transfer even when
   the *syntax* doesn't. Always match the consuming project's real framework,
   styling system, and idioms.

## How to use this skill

Start by reading the reference that matches your situation. Each is
self-contained; you rarely need all three at once.

| You are… | Read | Then |
|----------|------|------|
| Standing up a new catalog | [catalog-norms.md](references/catalog-norms.md) | Scaffold structure + token layers, then add components one at a time |
| Taking a design change into code, or pushing code back to Figma | [round-trip-workflow.md](references/round-trip-workflow.md) | Follow the direction-specific flow; delegate per-component work to the Figma skills |
| About to declare something done, or debugging drift/flakiness | [failure-catalog.md](references/failure-catalog.md) | Check your change against the recorded failure classes before you ship |

Templates for the example stack live in [assets/](assets/) — copy and adapt them
to the host project rather than authoring from scratch. Read
[assets/stack-adaptation.md](assets/stack-adaptation.md) first when the host
stack is not React/Tailwind, so you translate the norms instead of the syntax.

### Bootstrap flow (new catalog)

Work in small, validated steps — a catalog built in one shot is a catalog you
cannot trust. The sequence mirrors dependency order: nothing renders correctly
until the layer beneath it exists.

1. **Toolchain.** Add the framework + Vite + Storybook. Watch the version and
   peer-dep traps in [failure-catalog.md](references/failure-catalog.md#toolchain)
   — they cost hours and produce silent, not loud, failures.
2. **Token layers before components.** Establish the three-tier token structure
   (primitive -> semantic -> component) and the cascade-layer ordering *before*
   building any component. Components bind to tokens; a component built before its
   tokens exist bakes in raw values you will have to tear out later. See
   [catalog-norms.md#tokens](references/catalog-norms.md#tokens).
3. **Storybook as the hub.** Configure `preview` so stories apply the theme
   exactly the way the app does (same mechanism, not a Storybook-only shim), and
   inject any store/router the page-level stories need. This is what makes a story
   a faithful stand-in for the app. See
   [catalog-norms.md#storybook-hub](references/catalog-norms.md#storybook-hub).
4. **Components, one at a time.** For each: colocate `Component` + `story` +
   `spec`, bind every visual property to a semantic token, expose a
   **token-bound enum** prop API (no raw color/size/style pass-through), and
   document every prop in `argTypes` so Storybook Docs reads as the spec. Validate
   with rendered-DOM assertions before moving on.

### Operation flow (existing catalog)

For a design change or a code change, the direction determines the entry point —
but both end at the same place: Storybook and the automated checks agree with the
intent, and any deviation is documented, not silent. See
[round-trip-workflow.md](references/round-trip-workflow.md) for the full flow,
including exactly which Figma skill handles which leg.

## Delegation: this skill vs. the Figma skills

Keep the layers straight so you neither duplicate the Figma mechanics nor skip
the catalog governance:

- **This skill** decides catalog structure, naming, token architecture, the
  round-trip process, and the guardrails that keep design and code aligned.
- **`figma-design-to-code`** owns pulling one node's context out of Figma — it
  guides the `get_design_context` call so you can implement it — the design->code
  leg, per component.
- **`figma-generate-library`** builds/updates the design system *inside* Figma
  from code — the code->design leg, per component set.
- **`figma-code-connect`** maps a Figma component to its code component so the
  two stay linked.

When a round-trip step needs any of those, invoke the Figma skill for the
mechanics and stay in this skill for the "where does it go in the catalog and
what rule governs it" decisions.

## What "done" looks like

A catalog change is done when: the component renders from semantic tokens only;
its story renders the production component and exposes the theme matrix for review
via the theme toolbar global, with automated assertions covering the tokens whose
value actually changes across themes (a theme-invariant component needs no
duplicate per-theme assertion);
`argTypes` documents the full prop API; rendered-DOM assertions (not CSS-text
checks) pass; and any intentional visual change or known-limitation is recorded
(in the spec and pinned in a test, or in an issues ledger with measured values)
rather than left implicit. The [failure catalog](references/failure-catalog.md)
is the checklist for the "recorded, not silent" part.
