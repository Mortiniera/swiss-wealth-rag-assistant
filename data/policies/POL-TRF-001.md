---
document_id: POL-TRF-001
title: Transfer Review Procedure
department: Operations
type: procedure
category: transfer_review
jurisdiction: CH
allowed_roles:
  - relationship_manager
  - client_service
  - compliance_viewer
effective_date: 2025-01-10
version: "2.1"
status: active
confidentiality: internal
---

# Transfer Review Procedure

## Purpose

Describes when outbound client transfers enter enhanced review and how delays are handled at Helvetia Private Bank AG.

## Standard processing

Routine transfers within the client’s established pattern and below the enhanced-review threshold are processed on the next banking day if cut-off times are met.

## Enhanced review triggers

A transfer enters **pending_review** when any apply:

- Amount exceeds the client’s rolling 90-day average by a material factor, or is above the internal high-value threshold
- Beneficiary is new or in a heightened-monitoring jurisdiction
- Account has an active restriction (`debit_block`, `full_freeze`, or `manual_review`)
- KYC status is `refresh_due` or identity documents are expired
- Open AML service request linked to the client

## RM responsibilities during delay

1. Check account restrictions and KYC status before promising value dates.
2. Inform the client that the transfer is under operational review without disclosing AML tip-off details.
3. Collect missing documents if KYC expiry is the blocker.
4. Log each client contact as an interaction.

## Completion

Operations clears or rejects the transfer after checks. Rejected transfers require a recorded reason code visible to the RM.
