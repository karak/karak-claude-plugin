# Plugin Decomposition Design

**Date:** 2026-04-18  
**Branch:** feat/plugin-decomposition  
**Status:** Approved

## Goal

Split the monolithic `karak-claude-plugin` into four domain-focused sub-plugins within a monorepo, while preserving backward compatibility via a meta-package at the root.

## Repository Structure

```
karak-claude-plugin/              ← monorepo root
├── .claude-plugin/
│   ├── plugin.json               ← meta-package (references all skills/agents)
│   └── marketplace.json          ← 5 plugin entries
├── karak-design/                 ← UI/UX/visual design
│   ├── .claude-plugin/plugin.json
│   ├── skills/
│   └── agents/
├── karak-architecture/           ← system architecture & infrastructure
│   ├── .claude-plugin/plugin.json
│   ├── skills/
│   └── agents/
├── karak-engineering/            ← code quality & review
│   ├── .claude-plugin/plugin.json
│   ├── skills/
│   └── agents/
└── karak-product/                ← product management (grows over time)
    ├── .claude-plugin/plugin.json
    └── agents/
```

## Plugin Assignments

### karak-design
**Skills (8):** google-design-docs, apple-design, icon-design, frontend-aesthetics, ux-psychologist, material-design, hifi-design-quality, mobile-auth-screen-design  
**Agents (1):** ui-designer

### karak-architecture
**Skills (1):** write-c4-diagram  
**Agents (2):** system-designer, gcp-infrastructure-engineer

### karak-engineering
**Skills (1):** codex-review  
**Agents (2):** code-refactorer, quality-assurance-manager

### karak-product
**Skills (0):** — (placeholder for future PM skills)  
**Agents (2):** requirements-analyst, agile-project-manager

### karak-claude-plugin (meta)
References all skills and agents from all sub-plugins. Existing users installing `karak-dev/karak-claude-plugin` get everything unchanged.

## Versioning

| Plugin | Version |
|--------|---------|
| karak-claude-plugin (meta) | 1.7.0 |
| karak-design | 1.0.0 |
| karak-architecture | 1.0.0 |
| karak-engineering | 1.0.0 |
| karak-product | 1.0.0 |

Sub-plugins version independently after initial release.

## marketplace.json Changes

`plugins[]` array gains 4 new entries with `source` pointing to sub-directories:

```json
{ "name": "karak-claude-plugin", "source": ".",                   "version": "1.7.0" },
{ "name": "karak-design",        "source": "./karak-design",       "version": "1.0.0" },
{ "name": "karak-architecture",  "source": "./karak-architecture", "version": "1.0.0" },
{ "name": "karak-engineering",   "source": "./karak-engineering",  "version": "1.0.0" },
{ "name": "karak-product",       "source": "./karak-product",      "version": "1.0.0" }
```

## Implementation Order

1. Create `karak-design/` with its plugin.json and copies of skills/agents
2. Create `karak-architecture/` similarly
3. Create `karak-engineering/` similarly
4. Create `karak-product/` similarly
5. Update root `.claude-plugin/marketplace.json` with 5 entries and meta version bump to 1.7.0
6. Validate all plugins with `claude plugin validate .`

## Constraints

- Root `plugin.json` must NOT have a `version` field (stays in marketplace.json only)
- All skill paths in plugin.json must start with `./skills/`
- Sub-plugin `plugin.json` files also must NOT have `version` fields
- Skills and agents are **copied** into each sub-plugin directory (not symlinked) for self-contained install
- `marketplace.json` in the root is the single source of truth for all versions
- The root `skills/` and `agents/` directories are the **canonical source**; sub-plugin copies must be kept in sync. A CI check (e.g. `diff` or checksum) must fail if any sub-plugin copy diverges from its canonical counterpart.
