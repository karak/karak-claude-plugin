# Example: an order payment API (a model REPORT.md)

`app/` is a small 2-tier app under test, and `tla/` holds its models. This README follows the `REPORT.md` layout the skill asks for. Every result below was produced with TLC v1.7.4 on Java 11.

## 1. Target and conclusion

Examined `POST /orders/:id/pay` (`app/server/payments.js`) and the client's retry loop (`app/client/PayButton.jsx`).

- **Bug 1 (confirmed):** when the client resends after a timeout, the card is charged twice.
- **Bug 2 (confirmed):** after bug 1 is fixed with a conditional UPDATE, a server crash right after the charge leaves the order stuck in `charging`. No later request can ever mark it paid.

## 2. Code ↔ model map

| Variable | Category | Domain | Code |
|---|---|---|---|
| `status` | DB | `"pending"`, `"paid"` (the fixed model adds `"charging"`) | `app/schema.sql` `orders.status` |
| `gatewayCharges` | External side effect, DB side | `0..MaxAttempts` | `payments.js:15` `gateway.charge` |
| `chargeRows` | DB | `0..MaxAttempts` | `payments.js:16` `INSERT INTO charges` |
| `sent`, `responded` | Network | `SUBSET Attempts` | `PayButton.jsx:5-6` `fetch` |
| `clientDone`, `i` | Client | `BOOLEAN`, `1..MaxAttempts` | `PayButton.jsx:3-12` |
| `seen` | Handler-local | domain of `status` | `payments.js:10` result of the SELECT |

| Action (label) | What one step covers | Code |
|---|---|---|
| `Send` | Send one `fetch` | `PayButton.jsx:6` |
| `Wait` | Receive the response, or time out after 5 s and move to the next attempt | `PayButton.jsx:6-10` |
| `Read` | `SELECT status` (one autocommit query) | `payments.js:10` |
| `Check` | 409 if already `paid` | `payments.js:13` |
| `Charge` | `gateway.charge` (one external API call) | `payments.js:15` |
| `InsertCharge` | `INSERT INTO charges` (one query) | `payments.js:16` |
| `MarkPaid` | `UPDATE ... status='paid'` (one query) | `payments.js:17` |
| `Respond` | Return the response | `payments.js:18` |

Assumptions: one order and one client. Double clicks are out of scope here, even though `PayButton.jsx` does not disable the button.

## 3. Invariants

| Invariant | Harm | Seen failing on a broken version? |
|---|---|---|
| `NoDoubleCharge == gatewayCharges <= 1` | The card is charged more than once for one order | Yes, on the model of the original code |
| `PaidHasChargeRow == status = "paid" => chargeRows >= 1` | The order is paid but no charge is recorded | Yes, on a mutant of the fixed version with `MarkPaid` moved before `InsertCharge` |
| `NoStuckCharging` (every process done ⇒ `status # "charging"`) | The order can never be paid | Yes, on `OrderPayCrash` (bug 2) |

## 4. Results

```bash
export TLA2TOOLS=/path/to/tla2tools.jar
bash ../../scripts/tlc.sh tla/OrderPay.tla        # buggy
bash ../../scripts/tlc.sh tla/OrderPayFixed.tla   # fixed
bash ../../scripts/tlc.sh tla/OrderPayCrash.tla   # fixed + crashes
```

| Model | Constants | TLC's final result | Distinct states |
|---|---|---|---|
| `OrderPay` | `MaxAttempts = 2` | `Error: Invariant NoDoubleCharge is violated.` | about 180 (varies with the parallel workers) |
| `OrderPayFixed` | `MaxAttempts = 2` | `Model checking completed. No error has been found.` | 139 |
| `OrderPayFixed` | `MaxAttempts = 3` | `Model checking completed. No error has been found.` | 755 |
| `OrderPayCrash` | `MaxAttempts = 2, MaxCrashes = 1` | `Error: Invariant NoStuckCharging is violated.` | 191 |

Each `.cfg` lists several invariants. To check that no other invariant was being masked, the violated one was removed and each remaining invariant was run with its own `.cfg`:
- in `OrderPay`, only `NoDoubleCharge` is violated;
- in `OrderPayCrash`, only `NoStuckCharging` is violated.

Deadlock checking stayed on (no `-deadlock`). A handler for an attempt that was never sent exits at `Arrive` once it sees that the client is done.

## 5. Counterexamples

**Bug 1 (`OrderPay`)**

1. The client sends attempt 1.
2. Handler 1 runs `SELECT status` and reads `pending` (`payments.js:10`).
3. Five seconds pass. The client gives up on attempt 1 and sends attempt 2. Handler 1 is still running.
4. Handler 2 also runs `SELECT status` and reads `pending`. Nobody has written `paid` yet.
5. Handler 1 calls `gateway.charge`: first charge.
6. Handler 2 also passes the `paid` check (`payments.js:13`) and calls `gateway.charge`: second charge.

**Bug 2 (`OrderPayCrash`)**

1. Handler 1 moves `pending` to `charging` with the conditional UPDATE.
2. The client gives up, sends attempt 2, and finishes.
3. The process crashes right after handler 1 calls `gateway.charge`. The card has been charged, and `status` stays `charging`.
4. Handler 2's conditional UPDATE matches 0 rows, and it returns 409.
5. Every request has finished, and the order is still `charging`. No later request can mark it paid.

## 6. Code-change instructions

**Instruction 1 (blocks bug 1; verified with `OrderPayFixed`)**

Replace the SELECT and the `paid` check at `payments.js:10-13` with a single conditional UPDATE:

```sql
UPDATE orders SET status = 'charging'
WHERE id = $1 AND status = 'pending'
RETURNING amount
```

On 0 rows, do not charge; return 409 (or 202 for "in progress"). This removes steps 4 and 6 of the counterexample: the check and the update become one step, so the second handler can no longer read `pending`. Add `charging` to the domain of `status` in `app/schema.sql`.

"0 rows" also covers a missing order. To keep 404 distinct from 409, read whether the order exists when the UPDATE matches 0 rows.

`OrderPayFixed` verifies only that the double charge of bug 1 is gone. It does not model `gateway.charge` throwing (a declined card or a timeout). In that case the order stays `charging`, the same state as bug 2. Until a `catch` that reverts to `pending` is added and modeled, that path is unverified.

**Instruction 2 (for bug 2; unverified)**

Pass an idempotency key derived from the order ID to `gateway.charge`. Then add a recovery job: for orders stuck in `charging` past a time limit, query the gateway and move them to `paid` or back to `pending`.

This is not modeled yet. The next round adds the recovery job and the assumption "the gateway honors the key" to the model, and checks `NoStuckCharging` and `NoDoubleCharge` together. Until then, instruction 2 is an unverified proposal.

## 7. Scope

Checked: one order, 2 attempts (3 for the fixed version), and 1 crash.

Not modeled:

- More than one order.
- Double clicks and multiple tabs.
- Gateway failures or declines.
- The unique constraint on `charges`.
- Lost responses, other than as timeouts.
- Liveness ("eventually paid").
- Response kinds. `PayButton.jsx:7` treats a 409 as success, but the model's `responded` does not distinguish 200 from 409. So client/DB mismatch (the screen says done while the DB says `charging`) is unchecked. The next round puts the response code in a variable and checks `clientDone => status = "paid"`.
- Crash points. `OrderPayCrash` crashes only right after `Charge`, and only one handler stops. Crashing right after `Claim`, or a process crash that stops every handler at once, is not modeled.

## 8. Sync point

This example matches the current contents of `app/`. In a real project, write here the SHA of the commit the model describes.

## 9. Rerun

```bash
bash ../../scripts/tlc.sh tla/OrderPay.tla
```
