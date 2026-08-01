---
document_id: POL-DAT-001
title: Internal Data Access Policy
department: Information Security
type: policy
category: data_access
jurisdiction: CH
allowed_roles:
  - relationship_manager
  - client_service
  - compliance_viewer
effective_date: 2025-03-15
version: "1.0"
status: active
confidentiality: confidential
---

# Internal Data Access Policy

## Purpose

Controls employee access to client and account information inside Helvetia Private Bank AG systems and assistants.

## Need-to-know

Employees may access client data only for assigned relationships or when their role grants a documented broader scope (for example Compliance review). Curiosity browsing is prohibited.

## Assistant and tool use

When using internal assistants:

- Provide only the client context required for the task
- Do not paste unrestricted exports of other clients into prompts
- Do not attempt to bypass assignment checks by rephrasing requests

## Logging

Material data access through verification APIs and future tool calls is expected to leave an audit trail. Employees must not disable logging or share credentials.

## Confidentiality

Client data and this policy are handled as **confidential**. External disclosure requires legal approval.
