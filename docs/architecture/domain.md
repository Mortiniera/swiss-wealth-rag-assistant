# Helvetia Private Bank — Domain Definition

## Purpose

This document defines the fictional institution used as the structured banking domain for the Swiss Wealth RAG Assistant. It is the business context for synthetic clients, accounts, KYC data, service requests, and operational scenarios.

## Institution

| Field | Value |
| ----- | ----- |
| **Legal name** | Helvetia Private Bank AG |
| **Short name** | Helvetia Private Bank |
| **Type** | Fictional Swiss private bank |
| **Headquarters** | Geneva, Switzerland |
| **Focus** | Discretionary and advisory wealth management for high-net-worth individuals and families |
| **Operating languages** | English (primary in this system), French, German |

Helvetia Private Bank is entirely fictional. It is not affiliated with any real bank, brand, or regulated entity.

## Business context

Relationship managers (RMs) and client-service employees handle day-to-day client operations: transfer reviews, KYC refresh, account restrictions, complaints, and communication preferences. Compliance staff may view cases for escalation review.

The product is an **internal operations assistant**, not a client-facing banking channel and not an autonomous adviser.

## User roles

| Role | Description | Typical access |
| ---- | ----------- | -------------- |
| **relationship_manager** | Owns client relationships; primary user of the assistant | Assigned clients, accounts, transactions, interactions, service requests |
| **client_service** | Handles operational tickets and escalations | Same operational reads as RM for covered clients |
| **compliance_viewer** | Reviews KYC, restrictions, and escalations | Read-only across KYC, restrictions, and audit-relevant fields |

Verification APIs are **read-only** and do not enforce product authentication. Role semantics describe how coverage and access are meant to be interpreted in the domain.

## Supported workflows

Structured data and APIs support inspection of:

1. Client profile and household membership
2. Accounts, portfolios, and holdings
3. Recent transactions (including pending / delayed transfers)
4. KYC and suitability status
5. Account restrictions
6. Service requests and SLA state
7. Prior interactions and communication preferences
8. Audit events recording data access or operational notes (seeded structure)

The existing Chroma-based `POST /ask` document Q&A path remains available in parallel. It is not the system of record for client data.

## Data boundaries

| In scope | Out of scope |
| -------- | ------------ |
| Synthetic clients, employees, households | Real personal data or real bank records |
| Accounts, portfolios, holdings, transactions | Trading, order management, market data feeds |
| KYC profiles, suitability profiles | Full core-banking ledger or payment rails |
| Service requests, interactions, restrictions | Email draft, approval, or send |
| Audit event table (seeded structure) | External observability platforms or agent orchestration |
| Read-only HTTP APIs for verification | Write APIs that mutate banking state |

## Synthetic-data disclaimer

All names, addresses, account numbers, IBAN-like identifiers, and narrative case details are **synthetic** and generated for demonstration and evaluation only.

- No real clients, employees, or personal data are used.
- Identifiers are fictional and must not be treated as valid banking credentials.
- Scenarios illustrate operational patterns (expired KYC, delayed transfer, etc.) without claiming regulatory completeness.
- The dataset must remain regenerable from a fixed seed for reproducibility.

## References

- Flagship use cases: [use-cases.md](use-cases.md)
- Relational model: [data-model.md](data-model.md)
