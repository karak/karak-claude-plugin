# Todo API — Node.js 24 scaffold

Express 5 + Drizzle ORM + SQLite + Vitest 3 TDD scaffold.

## Quick start

```bash
npm install
npm run generate   # generate migration files (required before first test)
npm test           # run all tests (6 tests expected to pass)
npm run dev        # start dev server with hot reload
npm run build      # production build → dist/server.js
```

## Stack

| Layer | Tool |
|-------|------|
| Runtime | Node.js 24 + TypeScript 5.8 |
| Server | Express 5 |
| ORM | Drizzle ORM v0.36+ |
| DB | better-sqlite3 (dev: `dev.db`, test: `:memory:`) |
| Test | Vitest 3 + supertest |
| Build | tsup |
| Dev | tsx watch |

## Key constraints

- `pool: forks` in vitest.config.ts — required for better-sqlite3 native addon
- `npm run generate` must run before `npm test` — creates the `drizzle/` migrations folder
- Drizzle queries are **synchronous** (better-sqlite3 driver) — no `await` on DB calls
