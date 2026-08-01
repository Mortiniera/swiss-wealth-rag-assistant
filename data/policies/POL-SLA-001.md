---
document_id: POL-SLA-001
title: Service Request and SLA Policy
department: Operations
type: policy
category: service_requests_sla
jurisdiction: CH
allowed_roles:
  - relationship_manager
  - client_service
  - compliance_viewer
effective_date: 2025-02-15
version: "1.0"
status: active
confidentiality: internal
---

# Service Request and SLA Policy

## Purpose

Defines intake categories and service-level targets for operational tickets at Helvetia Private Bank AG.

## Categories and targets

| Type | Initial response | Target resolution |
| ---- | ---------------- | ----------------- |
| `document_request` | 1 business day | 5 business days |
| `complaint` | 2 business days | 10 business days |
| `kyc_refresh` | 1 business day | 15 business days |
| `transfer_query` | same business day | 3 business days |
| `aml_review` | same business day | Compliance-owned |
| `general` | 2 business days | 10 business days |

## SLA breach

If a ticket exceeds the target resolution time without an approved extension, status becomes **sla_breach**. Owners must escalate per **POL-ESC-001** and inform the RM.

## Ownership

Client service owns most operational tickets. AML and formal compliance reviews are owned by Compliance even when the RM opens the ticket.
