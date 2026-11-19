# Running TLC and reading its results

## Setup

- You need Java 11 or later.
- Get `tla2tools.jar` from https://github.com/tlaplus/tlaplus/releases. This skill was checked with v1.7.4.
- Before downloading, show the user the file name, source and size, and get their approval.
- Keep the jar out of the app's repo, and pass its location in `TLA2TOOLS`.
- The same jar also runs inside the VS Code extension (tlaplus.vscode-ide) and the TLA+ Toolbox. The rerun instructions in the report must still give the CLI command.

## Commands

`bash scripts/tlc.sh Spec.tla [Spec.cfg] [extra TLC args]` runs the stages below in order. To run one stage by hand, set `J=$TLA2TOOLS` and use the same command.

| Stage | Command | Sign of success |
|---|---|---|
| PlusCal translation | `java -cp $J pcal.trans -nocfg Spec.tla` | `Translation completed.` |
| Syntax and semantic check | `java -cp $J tla2sany.SANY Spec.tla` | No `Semantic errors` |
| Model checking | `java -cp $J tlc2.TLC -workers auto -config Spec.cfg Spec.tla` | `Model checking completed. No error has been found.` |

- `pcal.trans` rewrites the part of the `.tla` file between `\* BEGIN TRANSLATION` and `\* END TRANSLATION`. Do not edit that part by hand.
- `pcal.trans` keeps the previous file as `.old`. The wrapper deletes it.
- Without `-nocfg`, `pcal.trans` overwrites your hand-written `.cfg`.
- TLC creates a `states/` directory in the working directory. The wrapper sends it to a temporary directory with `-metadir`.

## .cfg template

```text
SPECIFICATION Spec
CONSTANTS MaxAttempts = 2
          MaxCrashes = 1
INVARIANTS TypeOK NoDoubleCharge PaidHasChargeRow
```

- Start with the smallest constants. Adding one more handler, attempt or crash multiplies the state count several times over.
- Make the default for reruns the largest bound that finishes within about a minute.
- While hunting, give each invariant its own `.cfg` (for example `Spec_NoDouble.cfg`). With parallel workers, which of several invariants gets reported first, and the state count at the violation, change from run to run. Add `-workers 1` when you need deterministic output.

## Deadlocks

TLC reports a deadlock when it reaches a state with no successor. There are three causes.

| Cause | How to tell | What to do |
|---|---|---|
| Normal termination (every process is `Done`) | In the final state, every `pc` is `"Done"` | In PlusCal this does not happen, because the translation includes `Terminating`. In hand-written TLA+, add `Terminating == AllDone /\ UNCHANGED vars` to `Next` |
| A process waiting for input that never comes | In the final state, some `pc` is stuck at an `await` label | Let that wait also exit on a termination condition ([modeling-2tier.md](modeling-2tier.md#waiting-for-a-request-that-never-came)) |
| A real deadlock | The wait cannot be satisfied without something outside the model | **This is a finding.** Report it as a counterexample in the code's terms |

The `-deadlock` flag switches off deadlock checking entirely. With it, the third row (real deadlocks) becomes invisible too. This skill does not use it; remove false deadlocks with the first or second row instead.

## PlusCal pitfalls

- `define` cannot refer to `ProcSet`, because `ProcSet` is defined after `define`. `pc` is part of the variable declaration, so it can be referred to.
  - Put invariants that read `ProcSet` (such as "once every process has finished") below `\* END TRANSLATION`, above the module's closing `====` ([example](../examples/order-pay/tla/OrderPayCrash.tla)).
  - To keep one inside `define`, spell out the set of process IDs instead of `ProcSet`, for example `{0} \union Attempts`.
- One label is one atomic step. Assigning the same variable twice within one label is a translation error.
- An `await` at the head of an `either ... or ...` branch makes that branch selectable only when its condition holds.
- A `goto` must be followed by a label. So `if c then goto L; end if; x := 1;` inside one label fails with `Missing label`. To keep the check and the action in one atomic step, put the action in the `else` branch: `if c then goto L; else x := 1; end if;`.
- If the `\* BEGIN TRANSLATION` and `\* END TRANSLATION` markers are missing, `pcal.trans` adds them. A new spec can be translated with nothing after `(* --algorithm ... end algorithm; *)`.

## Reading a counterexample trace

1. The first line, `Error: Invariant X is violated.`, tells you which invariant broke.
2. Each `State n: <Label line ...>` tells you which label (action) ran in that step.
3. Follow the changes in the variables. The change in `pc` tells you which process moved.
4. Map each step to a `file:line` in the code, and rewrite the trace as a numbered sequence of steps.

TLC searches breadth-first and returns one shortest counterexample. To find the next bug, rerun with a model in which the found bug is blocked.

TLC also writes the counterexample to `*_TTrace_*.tla` in the `-metadir` directory. The wrapper deletes that directory on exit, so read the trace from standard output, or run TLC directly if you want to keep the file.

## When the state space is too large

- Shrink the constants.
- Use symmetry:
  - Make ID sets model values instead of integers (`CONSTANT Clients = {c1, c2}` in the `.cfg`).
  - Define `Perms == Permutations(Clients)` in the spec, with `EXTENDS TLC`.
  - Add `SYMMETRY Perms` to the `.cfg`.
  - Symmetry makes liveness checking unsound, so use it only for safety invariants.
- Reset local variables to their initial values once they are no longer needed.
- Bound the search with a state constraint such as "attempts <= N" under `CONSTRAINT` in the `.cfg`.
- If it is still too large, try random runs with `-simulate -depth 50`. If no violation shows up, do not write "verified", because a random search is not exhaustive.
- Do not shrink the state space by cutting invariants or meaning out of the model.

## Liveness (things that must eventually happen)

This skill mainly deals with safety: never reaching a bad state. To check liveness, such as "eventually paid", put a temporal formula like `PROPERTY Termination` in the `.cfg`. PlusCal's translation already defines `Termination`.

Liveness also needs fairness: `fair process` in PlusCal, or `WF_vars(Action)` in TLA+. Without it, TLC returns "nobody ever does anything" as a counterexample.
