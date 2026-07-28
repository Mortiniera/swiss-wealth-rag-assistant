# Flagship Use Cases (v0.3)

These three use cases define the **minimum** structured data required for Helvetia Private Bank in v0.3. Schema fields exist because these workflows need them. Email draft, approval, and send are deferred to v0.7.

See also: [domain.md](domain.md).

---

## UC-1 — Delayed transfer + expired KYC

### Actor

Relationship manager (or client-service employee acting on an assigned client).

### Trigger

The employee asks why a client transfer is delayed (today: via inspection of structured APIs; later: via the agent).

### Required entities

| Entity | Why |
| ------ | --- |
| Client | Identify the client under review |
| ClientAssignment | Confirm employee coverage |
| Account | Source account for the transfer |
| Transaction | Pending / delayed outbound transfer |
| KYCProfile | Show expired or missing KYC document |
| Restriction | Optional: KYC-driven operational hold |
| Interaction | Prior notes about document request |
| ServiceRequest | Optional linked refresh ticket |

### Expected outcome (v0.3)

Read-only APIs return:

- Client identity and status
- The pending transfer with status and delay reason code
- KYC profile showing expiry / invalid document state
- Related interactions and service requests if present

An operator can demonstrate the case **without an LLM** by calling the client APIs.

### Out of scope (v0.3)

- Drafting or sending a KYC refresh email
- Approving communication
- Mutating transfer or KYC state via API

---

## UC-2 — Account restriction / unusual transaction

### Actor

Relationship manager or compliance viewer (read).

### Trigger

Investigation of a blocked action or flagged high-value / unusual cash movement.

### Required entities

| Entity | Why |
| ------ | --- |
| Client | Subject of the investigation |
| Account | Restricted or source account |
| Restriction | Active restriction type, reason, effective dates |
| Transaction | Unusual or high-value movement (flagged) |
| Portfolio / Holding | Optional context for account wealth |
| AuditEvent | Record that the case was inspected (seeded structure) |

### Expected outcome (v0.3)

APIs expose account restrictions and the flagged transaction so an operator can see why an action is blocked.

### Out of scope (v0.3)

- Lifting restrictions
- AML case management systems
- Real-time payment blocking engines

---

## UC-3 — Unresolved complaint / SLA breach

### Actor

Client-service employee or relationship manager.

### Trigger

Open complaint or service request past its SLA due date.

### Required entities

| Entity | Why |
| ------ | --- |
| Client | Complainant |
| ServiceRequest | Type, status, opened_at, sla_due_at, priority |
| Interaction | Prior calls/emails about the complaint |
| CommunicationPreference | Channel constraints that may affect follow-up |
| ClientAssignment | Owning RM / coverage |

### Expected outcome (v0.3)

APIs return the open service request with SLA breach indicators and prior interaction history.

### Out of scope (v0.3)

- Closing or reassigning tickets via API
- Automated SLA escalation workflows
- Client-facing complaint portals

---

## Cross-cutting requirements

| Requirement | Detail |
| ----------- | ------ |
| Deterministic seed | Same seed → same clients and scenario fixtures |
| Scenario overrides | Named scenarios pin specific clients/accounts for demos |
| No real PII | All names and identifiers are synthetic |
| Demo without LLM | Curl / Swagger against read-only APIs is sufficient |

## Next

The relational model in [data-model.md](data-model.md) will list only entities and fields justified by these use cases (plus the fifteen curated scenario variants documented later).
