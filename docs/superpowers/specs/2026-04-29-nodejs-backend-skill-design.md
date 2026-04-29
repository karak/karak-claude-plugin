# Design Doc: karak-engineering/nodejs-backend Skill + Agent

**Date:** 2026-04-29  
**Status:** Draft  
**Author:** Claude (brainstorming session)

---

## Context and Scope

This document specifies a new skill (`karak-engineering/nodejs-backend`) and agent (`nodejs-backend-engineer`) for the karak-claude-plugin repository. The skill provides Claude with comprehensive knowledge to develop modern Node.js backends and to scaffold new projects from scratch.

**In scope:**
- Node.js 24 + TypeScript 5.8 backend development
- Vite 7 and Vite 8 build pipeline (both versions' knowledge retained; test app uses Vite 8)
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
│   └── plugin.json                   # ← add skill + agent entries here
├── skills/
│   └── nodejs-backend/               # NEW
│       ├── SKILL.md                  # Navigator (< 200 lines)
│       └── references/
│           ├── node24-ts.md          # Node.js 24 + TypeScript 5.8 pitfalls
│           ├── vite-config.md        # Vite 6→7 and 7→8 breaking changes + build config
│           ├── express5.md           # Express 5 patterns + path-to-regexp migration
│           ├── prisma.md             # Prisma patterns, migrations, connection pooling
│           ├── drizzle.md            # Drizzle schema, migrations, testing patterns
│           ├── testing.md            # Vitest 3 + supertest TDD patterns
│           └── todo-app/             # Scaffold: complete working Todo API
│               ├── README.md
│               ├── package.json
│               ├── tsconfig.json
│               ├── vite.config.ts
│               ├── vitest.config.ts
│               ├── src/
│               │   ├── server.ts     # Entry point (listen only)
│               │   ├── app.ts        # Express app (testable, no listen())
│               │   ├── db/
│               │   │   ├── schema.ts # Drizzle schema definition
│               │   │   └── client.ts # DB singleton (SQLite / :memory:)
│               │   └── routes/
│               │       └── todos.ts  # CRUD route handlers
│               └── src/__tests__/
│                   └── todos.test.ts # TDD: tests written before implementation
└── agents/
    └── nodejs-backend-engineer.md   # NEW
```

**plugin.json update required** — add to `karak-engineering/.claude-plugin/plugin.json`:
```json
{
  "skills": ["./skills/codex-review", "./skills/google-design-docs", "./skills/nodejs-backend"],
  "agents": ["./agents/code-refactorer.md", "./agents/quality-assurance-manager.md", "./agents/nodejs-backend-engineer.md"]
}
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
| `node24-ts.md` | `erasableSyntaxOnly`, `verbatimModuleSyntax`, `NodeNext` module resolution, `import type` enforcement, tsconfig `paths` silently ignored at runtime, OpenSSL 3.5 key-length restrictions, mandatory `.ts` file extensions in imports |
| `vite-config.md` | Vite 6→7 changes AND Vite 7→8 changes (Vite 8 introduced Rolldown as default bundler replacing esbuild+Rollup); backend lib mode config; `build.rollupOptions.external` for Node built-ins; `vite-node` dev runner; tsup as alternative for pure backends |
| `express5.md` | `path-to-regexp` v8 migration (`/foo*` → `/foo(.*)`), async error auto-forwarding (no more manual try/catch), removed methods (`req.param()`, `res.json(obj, status)`, `app.del()`), typed request/response patterns |
| `prisma.md` | Singleton `PrismaClient`, `migrate deploy` vs `migrate dev`, N+1 avoidance, serverless connection pooling (`?connection_limit=1`), `DateTime` JSON serialization trap |
| `drizzle.md` | `sqliteTable`/`pgTable` schema definition, `drizzle-kit generate` + `migrate`, nullable type inference (`.notNull()` required), explicit connection management, comparison with Prisma |
| `testing.md` | Vitest 3 config (`pool: forks`, `environment: node`), supertest HTTP testing patterns, TDD cycle (Red→Green→Refactor), component-test-over-unit-test philosophy (goldbergyoni), mock placement rules (`beforeEach` vs inline) |

### Todo App (Test Scaffold)

**API endpoints:**
```
GET    /todos         List all todos
POST   /todos         Create a todo { title: string }
PATCH  /todos/:id     Update { title?: string, done?: boolean }
DELETE /todos/:id     Delete
```

**Tech stack:**
- Runtime: Node.js 24, TypeScript 5.8 (`erasableSyntaxOnly: true`)
- Build: Vite 8 lib mode (`vite build`) + tsx watch for dev
- HTTP: Express 5
- ORM: Drizzle ORM + better-sqlite3
- DB: SQLite file in dev, `:memory:` in tests
- Test: Vitest 3 (`pool: forks`) + supertest

**TDD sequence (tests first):**
1. Write `todos.test.ts` with all endpoint tests → all Red
2. Implement Drizzle schema (`schema.ts`) and DB client
3. Implement Express routes (`todos.ts`) → Green
4. Refactor

**One-shot commands:**
```bash
npm install   # install all deps
npm test      # vitest run → all tests pass
npm run dev   # tsx watch src/server.ts
npm run build # vite build
```

**Environment switching:**
- `vitest.config.ts` sets `test.env: { DB_FILE: ':memory:' }` → Drizzle `client.ts` reads `process.env.DB_FILE` and uses `:memory:` during tests
- Default (no env var) → `./dev.db` SQLite file on disk

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
  → Runs npm install && npm test to verify
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
- **Tests fail on first run**: Agent reads test output, cross-references `testing.md` and relevant reference file, fixes before reporting to user
- **Vite build fails**: Agent checks `vite.config.ts` external list against actual Node.js built-ins imported in source

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

---

## Open Questions

None — all design decisions resolved in brainstorming session.
