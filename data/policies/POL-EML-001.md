---
document_id: POL-EML-001
title: Email Draft and Approval Procedure
department: Client Service
type: procedure
category: email_approval
jurisdiction: CH
allowed_roles:
  - relationship_manager
  - client_service
  - compliance_viewer
effective_date: 2025-05-01
version: "1.0"
status: active
confidentiality: internal
---

# Email Draft and Approval Procedure

## Purpose

Defines the controlled path for drafting and approving client emails at Helvetia Private Bank AG. Sending to an external mail system is governed separately and is not enabled in the current product release.

## Draft creation

An employee may draft an email that:

- References facts available from authorised client records and active policies
- Matches the client’s language and communication preferences
- Avoids investment advice that contradicts the suitability profile

## Policy check before approval

Before approval, verify:

- Recipient matches the client record
- No tip-off language related to AML investigations
- Cross-border communication restrictions are respected
- Required operational disclaimers are present when discussing delays or document requests

## Approval states

```text
draft_created -> policy_checked -> awaiting_approval -> approved | rejected
```

Any edit after approval invalidates the approval and returns the draft to `draft_created`.

## Send

Outbound send requires a valid approval record. Without approval, send is prohibited.
