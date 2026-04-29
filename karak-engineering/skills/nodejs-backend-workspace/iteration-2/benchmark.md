# nodejs-backend skill — Iteration 2 Benchmark

## Summary

| Config | Pass Rate | Evals |
|---|---|---|
| with_skill | **100%** (14/14) | eval-0: 6/6, eval-1: 4/4, eval-2: 4/4 |
| without_skill | **43%** (6/14) | eval-0: 2/6, eval-1: 4/4, eval-2: 0/4 |

**Delta: +57 percentage points**

---

## Per-Eval Breakdown

### Eval 0: new-project-setup (same as iteration 1)

| Assertion | with_skill | without_skill |
|---|---|---|
| pool:forks in vitest config | ✅ | ✅ |
| WHY pool:forks (native addon / segfault) | ✅ | ❌ (says "ESM安定性") |
| DB_FILE :memory: for tests | ✅ | ❌ (uses DATABASE_URL instead) |
| programmatic migrate() in setup | ✅ | ❌ (says beforeEach re-creation, misses CLI limitation) |
| drizzle.config.ts relative paths | ✅ (+ CJS reason) | ✅ |
| erasableSyntaxOnly in tsconfig | ✅ | ❌ |
| **Score** | **6/6** | **2/6** |

### Eval 1: drizzle-sync-api (NEW — replaces express5-wildcard-routing)

| Assertion | with_skill | without_skill |
|---|---|---|
| better-sqlite3 is synchronous | ✅ | ✅ |
| await on non-Promise harmless but misleading | ✅ | ✅ |
| sync errors propagate in Express 5 async handler | ✅ | ✅ |
| pg/mysql2 contrast | ✅ | ✅ |
| **Score** | **4/4** | **4/4** |

⚠️ **Non-discriminating again** — better-sqlite3 sync API is also general knowledge.

### Eval 2: vitest-drizzle-no-such-table (same as iteration 1)

| Assertion | with_skill | without_skill |
|---|---|---|
| identifies missing pool:forks | ✅ | ❌ |
| native addon / worker_threads incompatibility | ✅ | ❌ |
| relative migrationsFolder path issue | ✅ | ❌ |
| each fork = own :memory: DB | ✅ | ❌ |
| **Score** | **4/4** | **0/4** |

---

## Cross-Iteration Comparison

| Eval | Iter1 with | Iter1 without | Iter2 with | Iter2 without |
|---|---|---|---|---|
| new-project-setup | 6/6 | 3/6 | 6/6 | 2/6 |
| eval-1 slot | 4/4 | 4/4 | 4/4 | 4/4 |
| vitest-drizzle | 4/4 | 1/4 | 4/4 | 0/4 |
| **Total** | **14/14** | **8/14** | **14/14** | **6/14** |

---

## Key Observations

1. **Eval slot 1 consistently non-discriminating.** Both express5-wildcard-routing and drizzle-sync-api were known without the skill. Need a question that specifically tests the *unique* knowledge in the reference files.

2. **Eval 2 is the clearest signal.** Without-skill agent consistently makes the same critical errors: claims `migrate()` needs `await` (wrong for better-sqlite3), never identifies `pool:forks` as the cause. With-skill: 4/4 both iterations.

3. **Eval 0 without-skill degraded iteration 2 (2/6 vs 3/6).** Different random response; the pattern inconsistency confirms baseline without-skill is unreliable for the hard assertions.

4. **with_skill is perfectly stable: 100% both iterations.** The reference files are delivering the right answers every time.

## Recommended Discriminating Eval for Slot 1

Replace with a question that specifically targets content unique to the skill reference files:

> "drizzle.config.ts で `import.meta.dirname` を使ってスキーマパスを指定したところ、`drizzle-kit generate` で `"import.meta" is not available with the "cjs" output format` エラーが出ます。なぜですか？どう直しますか？"

This targets the CJS compilation pitfall in `drizzle.md` — a non-obvious fact that the without-skill agent was not aware of in either iteration.

---

## Conclusion

Skill is validated and production-ready. The two discriminating evals (0 and 2) consistently show +50 pp or more. The skill reliably surfaces pitfalls (pool:forks, drizzle.config.ts CJS, programmatic migrate, erasableSyntaxOnly) that a highly capable model gets wrong without it.
