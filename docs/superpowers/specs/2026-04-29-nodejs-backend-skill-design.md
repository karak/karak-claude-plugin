# Design Doc: karak-engineering/nodejs-backend Skill + Agent

**Date:** 2026-04-29  
**Status:** Draft (v2 — post adversarial review)  
**Author:** Claude (brainstorming session)

---

## Context and Scope

This document specifies a new skill (`karak-engineering/nodejs-backend`) and agent (`nodejs-backend-engineer`) for the karak-claude-plugin repository. The skill provides Claude with comprehensive knowledge to develop modern Node.js backends and to scaffold new projects from scratch.

**In scope:**
- Node.js 24 + TypeScript 5.8 backend development
- Vite 7 and Vite 8 build pipeline knowledge (both versions retained; scaffold uses tsup for prod, tsx for dev)
- Express 5 API patterns
- Drizzle ORM and Prisma ORM patterns
- Vitest 3 + supertest testing patterns (TDD)
- A fully working Todo API scaffold that passes tests on first run (`npm install && npm test`)

**Out of scope:**
- Frontend/SSR (React, Next.js)
- Cloud deployment (covered by `gcp-infrastructure-engineer` agent)
- GraphQL / tRPC

---

## Goals and Non-Goals

### Goals
1. Claude can develop a Node.js 24 + TypeScript backend without common pitfalls (tsconfig misconfiguration, Node.js 24 type-stripping constraints, Express 5 path-to-regexp breakage, ORM connection misuse)
2. Claude can scaffold a new backend project from the Todo app template with one command sequence
3. The skill covers both Drizzle and Prisma with clear guidance on when to choose each
4. Vite 7→8 breaking changes are documented so Claude doesn't regress on either version
5. References are sourced from official docs and leading-company GitHub repos (Vercel, tRPC, Prisma, goldbergyoni/nodejs-testing-best-practices)

### Non-Goals
- This skill does not replace dedicated ORM migration tooling; it guides usage
- The Todo app template is a test harness and learning scaffold, not a production starter kit

---

## Architecture

### Skill Structure (Hub-and-Spokes)

The `karak-engineering` sub-plugin owns this skill. New files integrate into its existing layout:

```
karak-engineering/
├── .claude-plugin/
│   └── plugin.json                   # ← update skills[] and agents[] arrays only
├── skills/
│   └── nodejs-backend/               # NEW
│       ├── SKILL.md                  # Navigator (< 200 lines)
│       └── references/
│           ├── node24-ts.md          # Node.js 24 + TypeScript 5.8 pitfalls
│           ├── vite-config.md        # Vite 6→7 and 7→8 breaking changes + build config
│           ├── express5.md           # Express 5 patterns + path-to-regexp migration
│           ├── prisma.md             # Prisma patterns, migrations, connection pooling
│           ├── drizzle.md            # Drizzle schema, migrations, sync API, testing
│           ├── testing.md            # Vitest 3 + supertest TDD patterns
│           └── todo-app/             # Scaffold: complete working Todo API
│               ├── README.md
│               ├── package.json
│               ├── tsconfig.json
│               ├── tsup.config.ts    # Production build (replaces Vite lib mode)
│               ├── vitest.config.ts
│               ├── drizzle.config.ts # drizzle-kit config (schema path + migrations out)
│               └── src/
│                   ├── server.ts     # Entry point (listen only)
│                   ├── app.ts        # Express app (testable, no listen())
│                   ├── db/
│                   │   ├── schema.ts # Drizzle schema definition
│                   │   └── client.ts # DB singleton: new Database(process.env.DB_FILE ?? ':memory:')
│                   ├── routes/
│                   │   └── todos.ts  # CRUD route handlers
│                   └── __tests__/
│                       ├── setup.ts  # beforeAll: programmatic migrate() for :memory: DB
│                       └── todos.test.ts  # TDD: tests written before implementation
└── agents/
    └── nodejs-backend-engineer.md   # NEW
```

**plugin.json update** — update only the `skills` and `agents` arrays in `karak-engineering/.claude-plugin/plugin.json`; preserve all other fields (`name`, `description`, `author`, `homepage`, etc.):
```json
"skills": ["./skills/codex-review", "./skills/google-design-docs", "./skills/nodejs-backend"],
"agents": ["./agents/code-refactorer.md", "./agents/quality-assurance-manager.md", "./agents/nodejs-backend-engineer.md"]
```

### Progressive Disclosure

The skill uses three loading levels:
1. **Metadata** (name + description) — always in context; triggers broadly on backend/API phrases
2. **SKILL.md body** — navigator logic + command cheat sheet; loaded whenever skill activates
3. **Reference files** — loaded on demand via explicit read instructions in SKILL.md

---

## Component Designs

### SKILL.md (Navigator)

Three blocks:
1. **Frontmatter description**: Trigger conditions listed explicitly — "Node.js バックエンド", "Express API", "Prisma マイグレーション", "Vite でビルド", "新しいバックエンドプロジェクトを作って", etc. Biased toward over-triggering.
2. **Command cheat sheet**: Key dev/build/test/migrate commands for instant reference without reading sub-files.
3. **Reference selector**: Decision table mapping symptom/task → which reference file(s) to read.

### Reference Files

| File | Key content |
|---|---|
| `node24-ts.md` | `erasableSyntaxOnly`, `verbatimModuleSyntax`, `NodeNext` module resolution, `import type`/`export type` enforcement, tsconfig `paths` silently ignored at runtime, OpenSSL 3.5 key-length restrictions, mandatory `.ts` file extensions in imports, **`import.meta.dirname` replaces `__dirname` in ESM** (Node.js 21.2+), **`tsx watch` dev mode**: `tsx` binary intercepts execution before Node 24's native type-stripping; this is intentional — tsx is faster and supports syntax (`const enum`, decorators) that native stripping does not; for loader-cooperative setups use `node --import tsx/esm src/server.ts` instead |
| `vite-config.md` | Vite 6→7 changes AND Vite 7→8 changes (Vite 8 = Rolldown as default bundler); for pure Node.js backends **tsup is recommended over Vite lib mode** (native addon externalization risk with Rolldown); Vite lib mode reference config when used (explicit `external` list for all Node built-ins and `node_modules`); `vite-node` dev runner |
| `express5.md` | `path-to-regexp` v8 migration (`/foo*` → `/foo(.*)`), async error auto-forwarding, removed methods (`req.param()`, `res.json(obj, status)`, `app.del()`), typed request/response patterns, **decorator-based routing libraries (routing-controllers, tsyringe) are incompatible with `erasableSyntaxOnly: true` — use plain function handlers** |
| `prisma.md` | Singleton `PrismaClient`, `migrate deploy` vs `migrate dev`, N+1 avoidance, serverless connection pooling (`?connection_limit=1`), `DateTime` JSON serialization trap |
| `drizzle.md` | `sqliteTable`/`pgTable` schema definition, `drizzle-kit generate` + `migrate`, nullable type inference (`.notNull()` required), explicit connection management, **better-sqlite3 driver makes all operations synchronous — do not `await` Drizzle queries** (sync throws propagate correctly through Express 5 async handlers), `drizzle.config.ts` required for drizzle-kit CLI, comparison with Prisma |
| `testing.md` | Vitest 3 config (`pool: forks` — **mandatory for better-sqlite3 native addon; worker threads crash with native binaries**), `environment: node`, `test: { env: { DB_FILE: ':memory:' } }` pattern (full config block shown), supertest HTTP testing patterns, **`:memory:` DB requires programmatic `migrate()` in `beforeAll` — `drizzle-kit migrate` CLI cannot reach an in-memory DB**, TDD cycle, goldbergyoni component-test philosophy |

### Todo App (Test Scaffold)

**API endpoints:**
```
GET    /todos         List all todos
POST   /todos         Create a todo { title: string }
PATCH  /todos/:id     Update { title?: string, done?: boolean }
DELETE /todos/:id     Delete
```

**Tech stack:**
- Runtime: Node.js 24, TypeScript 5.8 (`erasableSyntaxOnly: true`, `"type": "module"`)
- Build (prod): **tsup** (`tsup src/server.ts --format esm --target node24 --external better-sqlite3 --external drizzle-orm`) — not Vite lib mode; both native addon and ORM must be external to avoid bundling CJS internals into ESM output
- Dev: `tsx watch src/server.ts`
- HTTP: Express 5
- ORM: Drizzle ORM + better-sqlite3 (synchronous API)
- DB: `./dev.db` SQLite file in dev; `:memory:` in tests via `process.env.DB_FILE ?? ':memory:'`
- Test: Vitest 3 (`pool: forks`) + supertest

**Vite knowledge retained:** `vite-config.md` covers Vite 7 and 8 build configurations for full-stack or frontend use cases where Vite is already present. The scaffold does not use Vite for the backend build because Vite 8's Rolldown bundler does not reliably externalize native addons (`better-sqlite3`).

**TDD sequence (tests first):**
1. Write `setup.ts` + `todos.test.ts` with all endpoint tests → all Red (schema missing)
2. Implement Drizzle schema (`schema.ts`) + `drizzle.config.ts` + run `drizzle-kit generate`
3. Implement DB client (`client.ts`) with programmatic `migrate()` in `setup.ts`
4. Implement Express routes (`todos.ts`) → Green
5. Refactor

**Critical: schema in `:memory:` DB**  
`drizzle-kit migrate` runs as a separate CLI process and cannot reach `:memory:` databases. Schema must be applied programmatically in `setup.ts`:
```ts
// src/__tests__/setup.ts
import { existsSync } from 'node:fs'
import { join } from 'node:path'
import { migrate } from 'drizzle-orm/better-sqlite3/migrator'
import { db } from '../db/client.ts'

// Anchor to project root via import.meta.dirname (__dirname is undefined in ESM)
const migrationsFolder = join(import.meta.dirname, '../../drizzle')

beforeAll(() => {
  if (!existsSync(migrationsFolder)) {
    throw new Error('Run `npx drizzle-kit generate` before `npm test`.')
  }
  migrate(db, { migrationsFolder })
})
```

With `pool: forks`, each test file runs in its own child process. `beforeAll` therefore runs once per file — the `:memory:` DB is correctly isolated per worker without needing `afterEach` teardown.

**`vitest.config.ts` (complete):**
```ts
import { defineConfig } from 'vitest/config'

export default defineConfig({
  test: {
    pool: 'forks',           // mandatory: better-sqlite3 is a native addon
    environment: 'node',
    env: { DB_FILE: ':memory:' },
    setupFiles: ['./src/__tests__/setup.ts'],
  },
})
```

**`client.ts` pattern:**
```ts
// process.env.DB_FILE injected by vitest env; falls back to ':memory:' if unset
import Database from 'better-sqlite3'
import { drizzle } from 'drizzle-orm/better-sqlite3'
import * as schema from './schema.ts'

const sqlite = new Database(process.env.DB_FILE ?? ':memory:')
export const db = drizzle(sqlite, { schema })
```

**`drizzle.config.ts` (required — missing breaks drizzle-kit CLI):**
```ts
import { defineConfig } from 'drizzle-kit'

export default defineConfig({
  schema: './src/db/schema.ts',
  out: './drizzle',
  dialect: 'sqlite',
  dbCredentials: { url: process.env.DB_FILE ?? './dev.db' },
})
```

**One-shot commands:**
```bash
npm install                  # install all deps
npx drizzle-kit generate     # generate SQL migration files
npm test                     # vitest run → programmatic migrate → all tests pass
npm run dev                  # tsx watch src/server.ts
npm run build                # tsup (ESM output)
```

**`package.json` scripts:**
```json
{
  "type": "module",
  "scripts": {
    "dev": "tsx watch src/server.ts",
      "build": "tsup src/server.ts --format esm --target node24 --external better-sqlite3 --external drizzle-orm",
    "test": "vitest run",
    "migrate": "drizzle-kit migrate"
  }
}
```

### Agent Definition

File: `karak-engineering/agents/nodejs-backend-engineer.md`

```yaml
name: nodejs-backend-engineer
description: |
  Node.js 24 + TypeScript backend specialist. Use when building Express APIs,
  ORM schemas (Prisma or Drizzle), Vitest TDD test suites, or Vite 8 build pipelines.
  Triggers on: "Node.js バックエンド", "Express API", "バックエンドエンジニア",
  "新しいAPIサーバーを作って", "Prisma/Drizzle マイグレーション"
model: sonnet
color: blue
```

Tools: All tools (file read/write, shell execution) — consistent with other agents in the `karak-engineering` namespace.

---

## Data Flow

### New Project Scaffolding Flow
```
User: "新しいNode.jsバックエンドプロジェクトを作って"
  → Skill triggers
  → SKILL.md selector: read todo-app/ references
  → Agent copies/adapts todo-app scaffold
  → Runs npm install && npx drizzle-kit generate && npm test to verify
  → Reports pass/fail
```

### Debugging Flow
```
User: "Express のルートが 404 になる"
  → Skill triggers
  → SKILL.md selector: read express5.md
  → Agent diagnoses path-to-regexp v8 wildcard breakage
  → Proposes fix
```

---

## Error Handling

- **Scaffold fails npm install**: Agent checks Node.js version (`node --version`), reports if < 24
- **Tests fail with `no such table`**: Agent checks whether `drizzle-kit generate` was run and whether `setup.ts` calls `migrate()` in `beforeAll`
- **Tests fail on first run**: Agent reads test output, cross-references `testing.md` and relevant reference file, fixes before reporting to user
- **Build fails (native addon)**: Agent confirms `better-sqlite3` is listed in tsup `--external`
- **`__dirname is not defined`**: Agent replaces with `import.meta.dirname` (Node.js 24 ESM)

---

## Testing Strategy for the Skill Itself

Per `skill-creator` workflow:
1. Write 2–3 eval prompts (scaffolding, debugging, migration)
2. Run with-skill vs without-skill subagent pairs
3. Grade with quantitative assertions
4. Iterate until user satisfaction
5. Run description optimization loop (`scripts/run_loop.py`)

---

## Alternatives Considered

### Alternative 1: Monolithic SKILL.md
All knowledge in one file. Rejected: would exceed 500-line soft limit; loads unnecessary content on every activation.

### Alternative 2: Skill Family (multiple separate skills)
`nodejs-express`, `nodejs-orm`, `nodejs-testing` as separate skills. Rejected: fragmented triggering; user would need to know which skill to invoke; cross-cutting concerns (e.g., testing + ORM) require reading both.

### Alternative 3: Hub-and-Spokes (chosen)
Thin navigator SKILL.md + reference files. Accepted: matches progressive disclosure model, consistent with existing `apple-design` skill pattern in this repo, focused loading.

### Alternative 4: Vite lib mode for scaffold build
Rejected (adversarial review finding): Vite 8's Rolldown bundler does not reliably externalize `better-sqlite3` native addon without manual enumeration of every dependency. `tsup` wraps esbuild which handles Node.js externalization correctly by default. Vite knowledge is retained in `vite-config.md` for cases where Vite is already part of the stack.

---

## Cross-cutting Concerns

### Security
- No secrets in reference files or scaffold code
- Todo app uses parameterized queries via Drizzle (no SQL injection risk)
- `tsconfig.json` with `strict: true` by default

### Performance
- SKILL.md stays < 200 lines to minimize constant context overhead
- Reference files loaded only when relevant, not on every skill activation

### Maintainability
- Each reference file is independently updatable (e.g., when Vite 9 ships, only `vite-config.md` needs updating)
- Todo app is a self-contained directory; can be packaged as a separate `.skill` asset
- `drizzle.config.ts` is the single source of truth for schema path and migrations output directory

---

## Key Technical Constraints (Summary)

These constraints were identified during adversarial review and must be honored throughout implementation:

| Constraint | Impact |
|---|---|
| better-sqlite3 is synchronous | Do not `await` Drizzle queries; sync throws propagate through Express 5 async handlers |
| `pool: forks` mandatory | better-sqlite3 native addon crashes under Vitest `pool: threads` |
| `:memory:` + drizzle-kit CLI incompatible | Use `migrate()` programmatically in `beforeAll`; CLI runs in a separate process |
| `drizzle.config.ts` required | Without it, `drizzle-kit generate` fails entirely |
| `__dirname` undefined in ESM | Use `import.meta.dirname` (Node.js 21.2+) in `drizzle.config.ts` and build configs |
| Vite lib mode + native addons | Rolldown externalization of native binaries is unreliable; use tsup for backend builds |
| `erasableSyntaxOnly: true` | No enums, no decorators, no parameter properties — use `as const` objects and plain handlers |
| `verbatimModuleSyntax: true` | Both `import type` AND `export type` must be explicit for type-only symbols |

---

## Open Questions

None — all design decisions resolved in brainstorming and adversarial review sessions.
