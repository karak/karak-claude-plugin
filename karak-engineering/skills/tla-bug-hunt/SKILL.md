---
name: tla-bug-hunt
description: |
  Use when hunting race conditions, double submission / double charge, lost updates, retry duplicates, or client-server-DB state mismatches in a 2-tier web app (browser or mobile client + API server + DB) that has no written spec, by modeling it in TLA+ or PlusCal and model-checking with TLC. Also use when a TLC counterexample, false deadlock, or SANY parse error comes up in such a model.
  Triggers: "TLA+ でバグを探して", "レースコンディション", "二重決済", "二重送信", "冪等性", "状態不整合", "モデル検査", "形式検証", "tla bug hunt", "model-check this endpoint", "can this retry double-charge".
---

# TLA+ bug hunt for 2-tier web apps

A test checks only the orderings someone thought of. TLC checks every ordering inside a small model. This skill reverse-engineers a state machine from the code of a 2-tier app that has no spec, uses TLC to find counterexamples, fixes the design in TLA+ first, and then translates the fix into code-change instructions for the app.

Put the output in the app's repo under `tla/<area>/`: the model (`.tla` and `.cfg`), a `REPORT.md`, and a one-command rerun. Do not change the app's code unless the user asks.

## What to read first

| When | Read |
|---|---|
| Writing the model (Steps 1–3) | [references/modeling-2tier.md](references/modeling-2tier.md): state classification, atomicity table, network patterns, invariant catalog |
| Running TLC (Step 4) | [references/running-tlc.md](references/running-tlc.md): setup, commands, `.cfg`, false deadlocks, reading traces |
| You want a worked example | [examples/order-pay/](examples/order-pay/README.md): a retry that double-charges, with the counterexample and the fixed model's pass both confirmed in TLC |
| Citing sources | [references/sources.md](references/sources.md) |

Run TLC with `bash scripts/tlc.sh <Spec>.tla [<Spec>.cfg]`. It runs the PlusCal translation, SANY and TLC in that order.

## Procedure

Each step has a goal (the artifact to produce) and constraints. Start with one client, one server and one request (Start Small). Once TLC passes, add concurrency one rung at a time. Asking for a large spec in one go tends to stall on SANY parse errors.

### Step 1: Reverse-engineer the abstract state from the code

**Goal:** write two tables into `REPORT.md`.

1. State variables. Columns: variable / category / domain / code location `file:line`.
2. Actions. Columns: action / what one step covers, from where to where / code location `file:line`.

**Constraints:**
- Sort state variables into three categories:
  - **Client:** e.g. idle, sending, done.
  - **Network:** requests sent, responses delivered, delay, out-of-order arrival.
  - **Server/DB:** sessions, table flags and values, side effects of external APIs.
- Keep only what affects concurrency control and state transitions. Drop string formatting, validation messages and ORM syntax.
- **List every entry point.** Keep a row for every path that reaches the same handler. Candidates are double clicks, multiple tabs, client retries, proxy or load-balancer resends, and jobs or workers.
- Attach a `file:line` to every row, and check line numbers against `nl -ba <file>`. A row you cannot attach a location to is a guess; mark it as an assumption.
- Find out which DB and isolation level are in use (the default, and anything set in code or per transaction), and record them in the table. They decide the atomicity.

### Step 2: Write it in PlusCal / TLA+

**Goal:** write `Init` and `Next` (processes and labels, in PlusCal), `TypeOK` and a `.cfg`, such that SANY parses the spec and TLC completes with `TypeOK` alone.

**Constraints:**
- **Match the grain of atomicity to the code.** One label (one action) must equal a span of code that nothing can interleave with. Each of these is one step: one `await`, one autocommit query, one transaction, one external API call. Putting a DB read and its update in the same step makes the race disappear. When unsure, follow the [atomicity table](references/modeling-2tier.md#atomicity).
- Model network uncertainty as explicit actions:
  - the server keeps working after the client times out;
  - retries create duplicates;
  - messages arrive out of order;
  - responses get lost.
- Comment each label or action with its code location.
- Start with the smallest constants: 2 attempts, 2 clients, 1 order, and so on.

### Step 3: Write the invariants

**Goal:** write each state that must never happen as a concrete predicate over the variables. Give each invariant a one-sentence statement of the harm.

**Constraints:**
- Write conditions that must be `TRUE` in every reachable state (`Spec => []Inv`). Write `gatewayCharges <= 1` or `status = "paid" => chargeRows >= 1`. Do not write abstract predicates such as "no error occurs".
- **See each invariant fail at least once.** Make a mutant of the model that breaks what the invariant guards, for example by removing a guard or reordering two steps, and confirm TLC reports a violation. An invariant you have never seen fail may guarantee nothing.
- The [invariant catalog](references/modeling-2tier.md#invariant-catalog) has candidates for double processing, double charging, lost updates, client/DB mismatch and stuck intermediate states.

### Step 4: Run TLC and read the counterexamples

**Goal:** record every run in `REPORT.md`:
- the command and the constants;
- TLC's final line, such as `No error has been found.` or `Invariant X is violated.`;
- the number of states generated.

Rewrite each counterexample as a numbered sequence of steps in the code's terms.

**Constraints:**
- **Do not switch off deadlock checking wholesale with `-deadlock`.** If TLC reports a deadlock for a model that just finished normally, follow [handling false deadlocks](references/running-tlc.md#deadlocks) and change the model so that only normal termination is allowed. Keep the ability to catch real deadlocks, where a wait can never be satisfied.
- When a counterexample appears, do not make it go away by weakening the spec or the invariant. First decide, against the code locations, whether it can happen in the real app. If you conclude it is a modeling error (wrong grain, a branch the code does not have), write down the code lines that show it before you fix the model.
- **Do not stop at the first counterexample.** TLC reports one violation per run:
  - Run each invariant with its own `.cfg` (`INVARIANTS TypeOK X`, one at a time) to get each counterexample. With several invariants in one `.cfg`, which one gets reported changes from run to run because of the parallel workers.
  - Block the bug you found, either with the fixed version or with a model whose entry point to that bug is temporarily closed, and rerun so TLC shows the next bug.
  - Anything you only reasoned about ("there is probably another one") stays "unconfirmed" until TLC produces a counterexample for it.
- If the state space explodes, shrink the constants. Do not shrink it by cutting meaning out of the model.

### Step 5: Fix it in TLA+, then translate to code-change instructions

**Goal:** a fixed model with a protective mechanism, such as `<Spec>Fixed.tla`, reaches `No error has been found.` with the same `.cfg` and constants as Step 4. Example mechanisms:
- exclusion through a conditional UPDATE;
- idempotency keys;
- unique constraints;
- a changed transaction isolation level;
- optimistic locking.

Then write the code-change instructions for the app.

**Constraints:**
- Do not move on to code-change instructions until TLC passes.
- Run the fixed version with the same constants and the same invariants as the buggy one. If the fixed version is a separate file, keep the `.cfg` contents identical. Switching within one file, for example with `CONSTANT Fixed \in BOOLEAN`, is also fine.
- Call something "verified" only if it is in the model. That includes new intermediate states or failure paths the fix creates, such as an exception thrown while the order is still `charging`. Mark anything not modeled as "unverified".
- Map each protective mechanism in the fixed version to a `file:line` code-change instruction. Each instruction says why it is needed and quotes which step of the Step 4 counterexample it blocks.
- If the fix relies on something outside the model, write it down as an assumption. For example, "the payment gateway honors the idempotency key" is an assumption unless it is modeled.
- Do not edit the app's code unless the user asks. This skill's job ends at the written instructions.

## Layout of REPORT.md

Write `tla/<area>/REPORT.md` in this order.

1. **Target and conclusion.** Which handler was examined and what was found. State the harm in one sentence.
2. **Code ↔ model map.** The two tables from Step 1.
3. **Invariants.** For each: the predicate, the harm, and the record of it failing on a mutant.
4. **Results.** Command, constants, TLC's final line and state count, for both the buggy and the fixed versions.
5. **Counterexamples.** Numbered step sequences in the code's terms.
6. **Code-change instructions.** `file:line`, the change, the counterexample step it blocks, and its assumptions.
7. **Scope.** What was checked (the bounds on the constants) and what was not modeled (crashes, multiple orders, gateway failures, and so on).
8. **Sync point.** The commit SHA of the code the model describes. If the covered files change after that commit, revisit the model.
9. **Rerun.** One command.

## Common mistakes

| Mistake | Instead |
|---|---|
| Adding `-deadlock` because normal termination shows up as a deadlock | Allow only normal termination. Let a wait for a request that never came be exited (see `Arrive` in the [example](examples/order-pay/tla/OrderPay.tla)) |
| Putting a SELECT and its UPDATE in one label | One autocommit query is one step. Merging them hides the race |
| Modeling a timeout as the request disappearing | The client gives up, but the server handler keeps running |
| Client retry is the only entry point | Also list double clicks, multiple tabs and proxy resends |
| Weakening an invariant after seeing a counterexample | Decide against the code whether it can happen. If it can, it is a finding |
| Reporting a second bug from reasoning alone | Block the first bug and rerun to get a counterexample |
| Several invariants in one `.cfg` while hunting | One invariant per `.cfg`, or `-workers 1` |
| Passing the fixed version with different constants | Run it with the same `.cfg` and constants as the buggy version |
| Modeling every feature at once | Start from one request and add one rung at a time |
