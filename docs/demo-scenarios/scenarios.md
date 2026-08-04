# Helvetia demo scenarios

Fifteen curated seed overrides with stable codes. After `scripts/seed_db.py`, look up these `client_code` / `account_code` / `transaction_code` / `request_code` values to demonstrate operational cases without an LLM. Restriction pins use notes prefixed `[RST-SCEN-NN]` (no separate restriction code column).

All data is synthetic. Read-only inspection is in scope; mutating banking state, drafting/sending client email, and lifting restrictions are out of scope for every scenario.

## Index

| ID | Scenario | Client | Primary codes |
| -- | -------- | ------ | ------------- |
| SCEN-01 | Expired KYC document | `CLI-SCEN-01` | `ACC-SCEN-01` |
| SCEN-02 | Account restriction | `CLI-SCEN-02` | `ACC-SCEN-02`, `RST-SCEN-02`, `SRQ-SCEN-02` |
| SCEN-03 | Delayed transfer | `CLI-SCEN-03` | `ACC-SCEN-03`, `TXN-SCEN-03`, `SRQ-SCEN-03` |
| SCEN-04 | Unusual transaction | `CLI-SCEN-04` | `ACC-SCEN-04`, `TXN-SCEN-04`, `SRQ-SCEN-04` |
| SCEN-05 | Incomplete onboarding | `CLI-SCEN-05` | `ACC-SCEN-05` |
| SCEN-06 | Unresolved complaint | `CLI-SCEN-06` | `SRQ-SCEN-06` |
| SCEN-07 | Missing suitability questionnaire | `CLI-SCEN-07` | `ACC-SCEN-07` |
| SCEN-08 | Cross-border communication restriction | `CLI-SCEN-08` | `ACC-SCEN-08` |
| SCEN-09 | Dormant relationship | `CLI-SCEN-09` | `ACC-SCEN-09` |
| SCEN-10 | Portfolio decline enquiry | `CLI-SCEN-10` | `ACC-SCEN-10` |
| SCEN-11 | Communication-preference conflict | `CLI-SCEN-11` | `SRQ-SCEN-11` |
| SCEN-12 | Previous unresolved email | `CLI-SCEN-12` | `SRQ-SCEN-12` |
| SCEN-13 | High-value cash movement | `CLI-SCEN-13` | `ACC-SCEN-13`, `TXN-SCEN-13`, `SRQ-SCEN-13` |
| SCEN-14 | Failed document upload | `CLI-SCEN-14` | `SRQ-SCEN-14` |
| SCEN-15 | Service-request SLA breach | `CLI-SCEN-15` | `SRQ-SCEN-15` |

UC-1 (delayed transfer + expired KYC) is covered by **SCEN-01**. **SCEN-03** isolates a delayed transfer with valid KYC.

---

## SCEN-01 — Expired KYC document

An RM looks up why a client’s outbound transfer is stuck. The passport on file has expired, a KYC hold sits on the account, and a refresh ticket is already open. So the delay is explained by compliance data, not by a payment-rail failure.

**Codes:** `CLI-SCEN-01`, `ACC-SCEN-01`, `TXN-SCEN-01` (pending transfer), `SRQ-SCEN-01` (KYC refresh), `RST-SCEN-01` (KYC hold)

**Facts**

- Client active; passport KYC `status=expired`, `document_expiry` in the past
- Outbound transfer `TXN-SCEN-01` `status=pending`, `delay_reason_code=kyc_expired`
- Active account restriction `RST-SCEN-01` `restriction_type=kyc_hold`
- Open service request `SRQ-SCEN-01` type `kyc_refresh`
- Interaction noting a prior document request

**Operator can verify**

- KYC expiry and pending transfer delay reason
- Restriction and linked service request / interaction

**Out of scope / forbidden via product APIs**

- Approve or send KYC refresh email
- Clear KYC or release the transfer

**Escalation**

- Compliance may review KYC and restriction fields; no write path

---

## SCEN-02 — Account restriction

Compliance put a manual block on an account. The RM needs to see that the account is restricted and why, before trying to explain a blocked action to the client.

**Codes:** `CLI-SCEN-02`, `ACC-SCEN-02` (`status=restricted`), `RST-SCEN-02`, `SRQ-SCEN-02`

**Facts**

- Active client; account marked restricted
- Restriction `compliance_block`, `reason_code=manual_review`, `status=active`
- Open service request and interaction documenting the compliance block

**Operator can verify**

- Account status and restriction reason / effective dates

**Out of scope**

- Lift or amend the restriction

**Escalation**

- Compliance viewer is the intended review role for the restriction record

---

## SCEN-03 — Delayed transfer

A transfer is pending for an operational review, while KYC is still valid. This isolates “ops delay” from the expired-KYC story in SCEN-01.

**Codes:** `CLI-SCEN-03`, `ACC-SCEN-03`, `TXN-SCEN-03`, `SRQ-SCEN-03`

**Facts**

- Pending outbound transfer with `delay_reason_code=ops_review`
- KYC otherwise valid (isolates transfer delay from SCEN-01)
- Open payment-ops service request and inbound client chase note

**Operator can verify**

- Transaction status, delay reason, counterparty, amount

**Out of scope**

- Release or cancel the transfer via API

**Escalation**

- Client-service / RM review of ops delay; compliance only if linked to a restriction

---

## SCEN-04 — Unusual transaction

A booked cash movement looks atypical for the client. An operator inspects the flagged transaction and recent activity to understand what raised the alert.

**Codes:** `CLI-SCEN-04`, `ACC-SCEN-04`, `TXN-SCEN-04`, `SRQ-SCEN-04`

**Facts**

- Booked cash movement with `is_unusual=true` and elevated amount
- Optional note in description referencing unusual pattern
- Open AML-style review request and outbound flag note

**Operator can verify**

- Flagged transaction and surrounding recent activity

**Out of scope**

- File an AML case or block payments in an external engine

**Escalation**

- Compliance viewer for read of unusual activity

---

## SCEN-05 — Incomplete onboarding

The relationship is not fully live yet: onboarding is unfinished, KYC is incomplete, and suitability is missing. Useful when showing a client who cannot yet be treated as an active mandate.

**Codes:** `CLI-SCEN-05` (`status=onboarding`), `ACC-SCEN-05`

**Facts**

- Client still in onboarding
- KYC `status=incomplete`; suitability `status=missing`
- At most a placeholder custody account, limited holdings

**Operator can verify**

- Client status and incomplete profile records

**Out of scope**

- Complete onboarding or activate the client via API

**Escalation**

- RM ownership via assignment; compliance may view incomplete KYC

---

## SCEN-06 — Unresolved complaint

The client raised a complaint that is still open. Prior notes exist, but nothing has closed the case. Classical ticket-history demo (SLA not yet breached; see SCEN-15 for breach).

**Codes:** `CLI-SCEN-06`, `SRQ-SCEN-06`

**Facts**

- Open service request `request_type=complaint`, `status=open`, priority high
- Prior interactions summarizing the complaint thread
- SLA due date may still be in the future (SLA breach is SCEN-15)

**Operator can verify**

- Complaint subject, status, interaction history

**Out of scope**

- Close, reassign, or reply to the client via API

**Escalation**

- Client-service primary; RM via assignment

---

## SCEN-07 — Missing suitability questionnaire

KYC is fine, but the suitability questionnaire was never completed. The gap shows up clearly against otherwise healthy accounts.

**Codes:** `CLI-SCEN-07`, `ACC-SCEN-07`

**Facts**

- Active client; suitability `status=missing`, `risk_profile` null, `completed_at` null
- KYC valid

**Operator can verify**

- Suitability gap vs otherwise healthy KYC / accounts

**Out of scope**

- Submit or update suitability via API

**Escalation**

- RM to chase questionnaire; compliance read-only

---

## SCEN-08 — Cross-border communication restriction

The client lives abroad and has not consented to cross-border contact. Staff must see that outbound communication is constrained before attempting follow-up.

**Codes:** `CLI-SCEN-08`, `ACC-SCEN-08`

**Facts**

- Residency outside CH (e.g. `US`)
- Communication preference `cross_border_ok=false`
- Interaction noting outbound contact was declined / constrained

**Operator can verify**

- Preference flags and residency vs interaction notes

**Out of scope**

- Override preferences or send cross-border marketing / advice email

**Escalation**

- Compliance / RM review before any client communication (communication itself not productized)

---

## SCEN-09 — Dormant relationship

The client is marked dormant: accounts still exist, but there is little recent activity. Useful for “quiet relationship” reviews.

**Codes:** `CLI-SCEN-09` (`status=dormant`), `ACC-SCEN-09`

**Facts**

- Client dormant; little or no recent transaction activity
- Accounts open but portfolio activity stale

**Operator can verify**

- Client status and quiet account / transaction history

**Out of scope**

- Reactivate the relationship via API

**Escalation**

- RM ownership for relationship review

---

## SCEN-10 — Portfolio decline enquiry

The client asked why the portfolio looks weaker. There is an enquiry on file and a current holdings snapshot to inspect, not a full performance engine.

**Codes:** `CLI-SCEN-10`, `ACC-SCEN-10`

**Facts**

- Open service request or interaction about portfolio performance concern
- Holdings present so an operator can inspect current market values (no historical NAV series)

**Operator can verify**

- Enquiry interaction / request and current holdings snapshot

**Out of scope**

- Investment advice generation or performance attribution engine

**Escalation**

- RM advisory conversation (outside this product)

---

## SCEN-11 — Communication-preference conflict

The client’s preferred channel does not match how an open ticket expects to follow up (e.g. postal vs phone). Staff need to spot the mismatch before contacting the client.

**Codes:** `CLI-SCEN-11`, `SRQ-SCEN-11`

**Facts**

- Preferred channel `postal` while an open request expects phone follow-up (or inverse)
- Interaction documenting the conflict

**Operator can verify**

- Preference vs open request / interaction mismatch

**Out of scope**

- Change preferences or contact the client via API

**Escalation**

- Client-service to resolve channel conflict manually

---

## SCEN-12 — Previous unresolved email

The client emailed in and nobody has answered yet. The inbound message sits awaiting reply, linked to an open service request.

**Codes:** `CLI-SCEN-12`, `SRQ-SCEN-12`

**Facts**

- Interaction `channel=email`, `status=awaiting_reply`, inbound from client
- Linked open service request

**Operator can verify**

- Unanswered email thread summary and linked request

**Out of scope**

- Draft, approve, or send an email reply

**Escalation**

- RM / client-service follow-up outside the product

---

## SCEN-13 — High-value cash movement

A very large cash transfer has already booked. Operators can inspect amount and counterparty when reviewing significant cash activity.

**Codes:** `CLI-SCEN-13`, `ACC-SCEN-13`, `TXN-SCEN-13`, `SRQ-SCEN-13`

**Facts**

- Large booked cash transfer (amount well above typical seed ranges)
- May also set `is_unusual=true` when combined with pattern flags
- Open high-value review request and RM inbound confirmation note

**Operator can verify**

- Amount, status, counterparty, account currency

**Out of scope**

- Block or reverse the payment via API

**Escalation**

- Compliance read for large cash movements

---

## SCEN-14 — Failed document upload

The client tried to upload identity documents and it failed. KYC is invalid or annotated accordingly, with a ticket and note explaining the failure.

**Codes:** `CLI-SCEN-14`, `SRQ-SCEN-14`

**Facts**

- KYC `status=invalid` or notes indicating failed upload
- Service request `document_upload` open; interaction summarizing failure

**Operator can verify**

- KYC notes / status and upload-related request

**Out of scope**

- Accept a new document upload via API

**Escalation**

- Client-service to re-request documents

---

## SCEN-15 — Service-request SLA breach

An open ticket has passed its SLA due date without resolution. This is the “late ticket” case, distinct from an open complaint that is still within SLA (SCEN-06).

**Codes:** `CLI-SCEN-15`, `SRQ-SCEN-15`

**Facts**

- Open service request with `sla_due_at` in the past and `resolved_at` null
- Priority elevated; supporting interactions present

**Operator can verify**

- SLA breach by comparing `sla_due_at` to current time and open status

**Out of scope**

- Auto-escalate, close, or reassign the ticket via API

**Escalation**

- Client-service supervisor process outside the product

---

## Related

- Domain: [../architecture/domain.md](../architecture/domain.md)
- Use cases: [../architecture/use-cases.md](../architecture/use-cases.md)
- Data model: [../architecture/data-model.md](../architecture/data-model.md)
