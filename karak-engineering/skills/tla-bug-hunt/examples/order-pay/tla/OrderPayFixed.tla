---------------------------- MODULE OrderPayFixed ----------------------------
(* FIXED model of POST /orders/:id/pay (server/payments.js) and the client's     *)
(* postWithRetry (client/PayButton.jsx). One order, MaxAttempts requests.   *)
EXTENDS Naturals, FiniteSets

CONSTANTS MaxAttempts   \* client/PayButton.jsx:3 attempts = 3; check with 2

Attempts == 1..MaxAttempts

(* --algorithm OrderPay
variables
  status = "pending",      \* orders.status            (schema.sql)
  gatewayCharges = 0,      \* cards charged by gateway.charge (payments.js:15)
  chargeRows = 0,          \* rows in charges table     (payments.js:16)
  sent = {},               \* attempts the client has put on the wire
  responded = {},          \* attempts whose HTTP response reached the client
  clientDone = FALSE;

define
  TypeOK ==
    /\ status \in {"pending", "charging", "paid"}
    /\ gatewayCharges \in 0..MaxAttempts
    /\ chargeRows \in 0..MaxAttempts
    /\ sent \subseteq Attempts /\ responded \subseteq sent
    /\ clientDone \in BOOLEAN
  \* Harm: the customer's card is charged more than once for one order.
  NoDoubleCharge == gatewayCharges <= 1
  \* Harm: the DB says paid but no charge row explains it (or vice versa).
  PaidHasChargeRow == (status = "paid") => (chargeRows >= 1)
end define;

\* client/PayButton.jsx:3-12  postWithRetry: send, then either get a
\* response or time out (5s) and retry, up to MaxAttempts.
process Client = 0
variable i = 1;
begin
  Send:
    sent := sent \union {i};
  Wait:
    either
      await i \in responded;          \* fetch resolved
      clientDone := TRUE;
      goto Finish;
    or
      \* AbortSignal.timeout fired: the request may still be in flight
      if i < MaxAttempts then i := i + 1; goto Send;
      else clientDone := TRUE; goto Finish;
      end if;
    end either;
  Finish:
    skip;
end process;

\* server/payments.js:9-19, one handler per attempt. Each `await db.query`
\* and `await gateway.charge` is its own atomic step: autocommit, no lock.
process Handler \in Attempts
begin
  Arrive:
    \* an attempt never sent must still be able to finish, or TLC
    \* reports a false deadlock
    await self \in sent \/ clientDone;
    if self \notin sent then goto Done; end if;
  Claim:                                  \* FIX: one atomic statement
    \* UPDATE orders SET status='charging'
    \*   WHERE id=$1 AND status='pending' RETURNING id
    if status = "pending" then status := "charging";
    else goto Respond;                    \* 0 rows -> 409 / 202
    end if;
  Charge:                                 \* payments.js:15
    gatewayCharges := gatewayCharges + 1;
  InsertCharge:                           \* payments.js:16
    chargeRows := chargeRows + 1;
  MarkPaid:                               \* payments.js:17
    status := "paid";
  Respond:                                \* payments.js:18 (or :13 409)
    responded := responded \union {self};
end process;
end algorithm; *)
\* BEGIN TRANSLATION (chksum(pcal) = "a6878cf0" /\ chksum(tla) = "495c481d")
VARIABLES status, gatewayCharges, chargeRows, sent, responded, clientDone, pc

(* define statement *)
TypeOK ==
  /\ status \in {"pending", "charging", "paid"}
  /\ gatewayCharges \in 0..MaxAttempts
  /\ chargeRows \in 0..MaxAttempts
  /\ sent \subseteq Attempts /\ responded \subseteq sent
  /\ clientDone \in BOOLEAN

NoDoubleCharge == gatewayCharges <= 1

PaidHasChargeRow == (status = "paid") => (chargeRows >= 1)

VARIABLE i

vars == << status, gatewayCharges, chargeRows, sent, responded, clientDone, 
           pc, i >>

ProcSet == {0} \cup (Attempts)

Init == (* Global variables *)
        /\ status = "pending"
        /\ gatewayCharges = 0
        /\ chargeRows = 0
        /\ sent = {}
        /\ responded = {}
        /\ clientDone = FALSE
        (* Process Client *)
        /\ i = 1
        /\ pc = [self \in ProcSet |-> CASE self = 0 -> "Send"
                                        [] self \in Attempts -> "Arrive"]

Send == /\ pc[0] = "Send"
        /\ sent' = (sent \union {i})
        /\ pc' = [pc EXCEPT ![0] = "Wait"]
        /\ UNCHANGED << status, gatewayCharges, chargeRows, responded, 
                        clientDone, i >>

Wait == /\ pc[0] = "Wait"
        /\ \/ /\ i \in responded
              /\ clientDone' = TRUE
              /\ pc' = [pc EXCEPT ![0] = "Finish"]
              /\ i' = i
           \/ /\ IF i < MaxAttempts
                    THEN /\ i' = i + 1
                         /\ pc' = [pc EXCEPT ![0] = "Send"]
                         /\ UNCHANGED clientDone
                    ELSE /\ clientDone' = TRUE
                         /\ pc' = [pc EXCEPT ![0] = "Finish"]
                         /\ i' = i
        /\ UNCHANGED << status, gatewayCharges, chargeRows, sent, responded >>

Finish == /\ pc[0] = "Finish"
          /\ TRUE
          /\ pc' = [pc EXCEPT ![0] = "Done"]
          /\ UNCHANGED << status, gatewayCharges, chargeRows, sent, responded, 
                          clientDone, i >>

Client == Send \/ Wait \/ Finish

Arrive(self) == /\ pc[self] = "Arrive"
                /\ self \in sent \/ clientDone
                /\ IF self \notin sent
                      THEN /\ pc' = [pc EXCEPT ![self] = "Done"]
                      ELSE /\ pc' = [pc EXCEPT ![self] = "Claim"]
                /\ UNCHANGED << status, gatewayCharges, chargeRows, sent, 
                                responded, clientDone, i >>

Claim(self) == /\ pc[self] = "Claim"
               /\ IF status = "pending"
                     THEN /\ status' = "charging"
                          /\ pc' = [pc EXCEPT ![self] = "Charge"]
                     ELSE /\ pc' = [pc EXCEPT ![self] = "Respond"]
                          /\ UNCHANGED status
               /\ UNCHANGED << gatewayCharges, chargeRows, sent, responded, 
                               clientDone, i >>

Charge(self) == /\ pc[self] = "Charge"
                /\ gatewayCharges' = gatewayCharges + 1
                /\ pc' = [pc EXCEPT ![self] = "InsertCharge"]
                /\ UNCHANGED << status, chargeRows, sent, responded, 
                                clientDone, i >>

InsertCharge(self) == /\ pc[self] = "InsertCharge"
                      /\ chargeRows' = chargeRows + 1
                      /\ pc' = [pc EXCEPT ![self] = "MarkPaid"]
                      /\ UNCHANGED << status, gatewayCharges, sent, responded, 
                                      clientDone, i >>

MarkPaid(self) == /\ pc[self] = "MarkPaid"
                  /\ status' = "paid"
                  /\ pc' = [pc EXCEPT ![self] = "Respond"]
                  /\ UNCHANGED << gatewayCharges, chargeRows, sent, responded, 
                                  clientDone, i >>

Respond(self) == /\ pc[self] = "Respond"
                 /\ responded' = (responded \union {self})
                 /\ pc' = [pc EXCEPT ![self] = "Done"]
                 /\ UNCHANGED << status, gatewayCharges, chargeRows, sent, 
                                 clientDone, i >>

Handler(self) == Arrive(self) \/ Claim(self) \/ Charge(self)
                    \/ InsertCharge(self) \/ MarkPaid(self)
                    \/ Respond(self)

(* Allow infinite stuttering to prevent deadlock on termination. *)
Terminating == /\ \A self \in ProcSet: pc[self] = "Done"
               /\ UNCHANGED vars

Next == Client
           \/ (\E self \in Attempts: Handler(self))
           \/ Terminating

Spec == Init /\ [][Next]_vars

Termination == <>(\A self \in ProcSet: pc[self] = "Done")

\* END TRANSLATION 
=============================================================================
