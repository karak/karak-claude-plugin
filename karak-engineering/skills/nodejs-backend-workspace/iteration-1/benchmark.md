# nodejs-backend skill — Iteration 1 Benchmark

## Summary

| Config | Pass Rate | Evals |
|---|---|---|
| with_skill | **100%** (14/14) | eval-0: 6/6, eval-1: 4/4, eval-2: 4/4 |
| without_skill | **57%** (8/14) | eval-0: 3/6, eval-1: 4/4, eval-2: 1/4 |

**Delta: +43 percentage points**

---

## Per-Eval Breakdown

### Eval 0: new-project-setup

| Assertion | with_skill | without_skill |
|---|---|---|
| pool:forks in vitest config | ✅ | ✅ |
| WHY pool:forks (native addon / segfault) | ✅ | ❌ (vague: "問題が起きることがある") |
| DB_FILE :memory: for tests | ✅ | ❌ (hardcodes :memory: in test helper instead) |
| programmatic migrate() in setup | ✅ | ✅ (but doesn't explain drizzle-kit CLI limitation) |
| drizzle.config.ts relative paths | ✅ (+ explains CJS reason) | ✅ (shows it, no explanation) |
| erasableSyntaxOnly in tsconfig | ✅ | ❌ (not mentioned) |
| **Score** | **6/6** | **3/6** |

### Eval 1: express5-wildcard-routing

| Assertion | with_skill | without_skill |
|---|---|---|
| path-to-regexp v8 as root cause | ✅ | ✅ |
| correct Express 5 wildcard syntax | ✅ | ✅ |
| Express 5 breaking change | ✅ | ✅ |
| throws at startup | ✅ | ✅ |
| **Score** | **4/4** | **4/4** |

### Eval 2: vitest-drizzle-no-such-table

| Assertion | with_skill | without_skill |
|---|---|---|
| identifies missing pool:forks | ✅ | ❌ (missed entirely; diagnosed connection sharing instead) |
| native addon / worker_threads incompatibility | ✅ | ❌ |
| relative migrationsFolder path issue | ✅ | ✅ (uses fileURLToPath workaround) |
| each fork = own :memory: DB | ✅ | ❌ |
| **Score** | **4/4** | **1/4** |

---

## Key Observations

1. **Eval 1 is non-discriminating** — path-to-regexp v8 is widely known; both configs score 100%. Consider replacing with a harder Express 5 question.

2. **Eval 2 is the strongest discriminator** — without skill makes a significant factual error: claims `migrate()` needs `await` (wrong — better-sqlite3 is synchronous), never identifies the actual root cause (pool:forks for native addon). With skill hits all 4 assertions.

3. **Eval 0 skill benefit is real but more subtle** — both mention pool:forks, but only with-skill explains WHY correctly, mentions DB_FILE pattern, and includes erasableSyntaxOnly. The CJS drizzle.config.ts note is unique to the skill.

4. **The false assertion (migrate() needs await)** in the without-skill response for eval 2 is a dangerous mislead — a developer following it would add unnecessary async complexity and still not fix the real issue.

---

## Conclusion

Skill adds clear value for non-obvious Node.js 24 + Drizzle + Vitest pitfalls. Consider adding a harder Express 5 eval for iteration 2.
