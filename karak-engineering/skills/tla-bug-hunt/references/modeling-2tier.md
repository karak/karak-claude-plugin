# Modeling patterns for 2-tier apps

## State classification

| Category | Typical variables | Example domain |
|---|---|---|
| Client | Screen state, attempt count, button enabled/disabled | `{"idle","sending","done","error"}`, `1..MaxAttempts` |
| Network | Set of requests sent, set of responses delivered, messages in flight | `SUBSET Attempts`, a bag of `[from, to, body]` |
| Server/DB | Table rows and flags, sessions, locks, count of external-API side effects | `{"pending","charging","paid"}`, `Nat` |
| Handler-local | Values read by a SELECT, program counter | PlusCal `variable` and `pc` |

Put the side effects of external APIs (charges, sent emails, stock reservations) on the DB side, as a count or a set. Most invariants count these side effects.

## Atomicity

One step must equal a span of code that no other request can interleave with.

This table assumes PostgreSQL, whose default isolation level is READ COMMITTED. MySQL InnoDB defaults to REPEATABLE READ. Check the DB and isolation level in the code and configuration before you pick a row.

| Code shape | Steps in the model |
|---|---|
| One autocommit query (`await db.query(...)`) | 1 step |
| `BEGIN ... COMMIT` under READ COMMITTED, reading without a lock and then updating | Separate steps for the read and the write. A lost update on the same row is possible |
| `BEGIN ... COMMIT` that updates only rows read with `SELECT ... FOR UPDATE` | 1 step for the whole transaction, with respect to those rows. Rows not locked, and rows inserted later (phantoms), are not protected. Keep conditions spanning several rows (write skew) as separate steps |
| `BEGIN ... COMMIT` under REPEATABLE READ / snapshot isolation | Reads see the snapshot taken at the start. In PostgreSQL, one of two concurrent updates to the same row fails. Write skew across different rows can still happen, so keep the read and the write as separate steps |
| `BEGIN ... COMMIT` under SERIALIZABLE | 1 step, but it can abort with a serialization failure (SQLSTATE 40001). Model the abort and the app's retry or error response as actions |
| An external API call inside a transaction (the call, then COMMIT) | Not atomic. The external side effect happens before COMMIT. A crash between the call and COMMIT leaves only the side effect |
| One conditional update (`UPDATE ... WHERE status='pending' RETURNING`) | 1 step. The check and the update happen together |
| READ COMMITTED `UPDATE` while another transaction holds the row lock | Waits for the lock. After the other transaction commits, PostgreSQL re-evaluates the `WHERE` against the latest row. A conditional update therefore matches 0 rows and stops correctly. But `SET balance = $1`, computed from a value the app read earlier, overwrites the latest value with a stale one (lost update). To model the wait, keep the lock holder in a variable and `await` on it |
| An additive update (`SET balance = balance + $1`) | 1 step. It adds to the latest value, so no lost update |
| `INSERT ... ON CONFLICT DO NOTHING` (with a unique constraint) | 1 step |
| An external API call (`await gateway.charge()`) | 1 step, separate from the queries before and after it |
| Synchronous JS code (no `await` in between) | 1 step within a single process. Not atomic across server instances |
| In-memory locks or caches (`Map`, `let inFlight`) | Effective with a single instance. With several instances, model them as separate variables per instance |
| React `setState` → re-render → button disabled | Separate steps. A second click can arrive before the button is disabled |

When in doubt, choose the finer grain over the coarser one. A model that is too fine only grows the state space; a model that is too coarse hides bugs.

## Network and entry-point patterns

| Phenomenon | How to model it |
|---|---|
| Retry after timeout | In the client's `either`, put "receive response" and "time out → send the next attempt" side by side. The server handler proceeds regardless of the timeout |
| Lost response | The server responded, but the response never reaches the client. Add a branch that does not add to `responded` |
| Out-of-order arrival | Keep requests in flight as a set, not a sequence, so any one can be received next |
| Double click, multiple tabs | Use two client processes, or let one client resend while a request is in flight |
| Proxy or load-balancer resend | An action that duplicates a request, with a bound on how many times |
| Server crash | An action that sends a handler to `Done`, with a bound on how many times. DB changes survive and memory is lost. A real crash stops every handler in flight in that process. Write down in the report's Scope section where the model crashes and how many handlers it stops at once |
| Several server instances | Give each instance its own variables for in-memory state (caches, locks, queues). Only the DB is shared |

### Waiting for a request that never came

If handlers are declared statically, as in `process Handler \in Attempts`, the handler for an attempt that was never sent waits forever at `await self \in sent`. TLC reports this as a deadlock. Let it exit once the client is done.

```tla
Arrive:
  await self \in sent \/ clientDone;
  if self \notin sent then goto Done; end if;
```

With this shape there is no need for `-deadlock`, and real deadlocks are still detected.

## Invariant catalog

These are templates. Rename the variables to match your model, and see each one fail in TLC once before relying on it.

| Bug | Harm | Predicate shape |
|---|---|---|
| Double charge / double processing | One intent causes a side effect more than once | `gatewayCharges <= 1`, `\A o \in Orders : Cardinality({c \in charges : c.order = o}) <= 1` |
| Lost update | One of two concurrent updates disappears | `stock = InitialStock - Cardinality(reserved)`, `balance = Value * Cardinality(usedCoupons)` (evaluate at termination or when no transaction is open) |
| Negative balance / stock | A constraint is broken | `balance >= 0`, `\A i \in Items : stock[i] >= 0` |
| DB vs side-effect mismatch | Paid with no record of the charge, or the reverse | `status = "paid" => chargeRows >= 1`, `chargeRows = gatewayCharges` |
| Client vs DB mismatch | The screen shows success but the DB is not done | `clientState = "done" => status = "paid"` |
| Processed count vs unique events | Idempotency is not kept | `Cardinality(processed) = Cardinality(uniqueClientEvents)` |
| Stuck intermediate state | Stays `charging` and nobody can move it on | Write it as a termination invariant: `(\A p \in ProcSet : pc[p] = "Done") => status # "charging"`. PlusCal's `define` cannot refer to `ProcSet`, so put it below `\* END TRANSLATION` ([example](../examples/order-pay/tla/OrderPayCrash.tla)) |

Stuck intermediate states often show up once crashes are modeled. After a fix that introduces an intermediate state (such as `charging`), add crashes and rerun.
