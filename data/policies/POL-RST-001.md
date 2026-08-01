---
document_id: POL-RST-001
title: Account Restrictions Policy
department: Operations
type: policy
category: account_restrictions
jurisdiction: CH
allowed_roles:
  - relationship_manager
  - client_service
  - compliance_viewer
effective_date: 2024-11-01
version: "1.3"
status: active
confidentiality: internal
---

# Account Restrictions Policy

## Purpose

Defines how Helvetia Private Bank AG places, communicates, and lifts restrictions on client accounts.

## Restriction types

| Code | Meaning |
| ---- | ------- |
| `debit_block` | Outbound payments blocked |
| `trading_block` | Investment orders blocked |
| `full_freeze` | All debit and trading activity blocked |
| `manual_review` | Activity allowed only after operations review |

## Placement

Restrictions may be placed by Operations or Compliance when:

- KYC is overdue or identity documents are expired
- An AML review is open
- A court or regulatory freeze instruction is received (simulated in demo data)
- Client-requested temporary hold is documented

## Communication

RMs may explain that an account is restricted and the operational next step. They must not invent legal grounds. Sensitive AML rationale follows **POL-AML-001** and must not be disclosed to the client as a tip-off.

## Lifting

Only the placing function (or Compliance for AML-linked holds) may lift a restriction after documented remediation. Client service may request a lift review but cannot self-approve.
