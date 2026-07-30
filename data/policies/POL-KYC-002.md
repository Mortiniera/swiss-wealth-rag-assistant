---
document_id: POL-KYC-002
title: KYC Refresh Policy
department: Compliance
type: policy
category: kyc_refresh
jurisdiction: CH
allowed_roles:
  - relationship_manager
  - client_service
  - compliance_viewer
effective_date: 2025-01-15
version: "2.0"
status: active
confidentiality: internal
supersedes: POL-KYC-001
---

# KYC Refresh Policy

## Purpose

Defines when and how Helvetia Private Bank AG refreshes know-your-customer (KYC) information for existing clients.

## Refresh cycles

| Client risk tier | Maximum interval |
| ---------------- | ---------------- |
| Standard | 24 months |
| Elevated | 12 months |
| High | 6 months or event-driven |

Risk tier is recorded on the KYC profile. When the interval elapses, status becomes **refresh_due**.

## Event-driven refresh

Refresh immediately when any of the following occur:

- Material change in beneficial ownership or control
- Change of tax residency or primary domicile
- New high-risk jurisdiction exposure
- Adverse media or internal AML alert linked to the client
- Expired identity document on file

## Expired documents

If a passport, national ID, or equivalent identity document is past its expiry date, account activity that increases risk (including outbound transfers above the client’s routine pattern) must be held pending refresh, unless Compliance grants a time-limited exception.

## Responsibilities

- **RM / client service:** request updated documents and record interaction notes
- **Compliance viewer:** review incomplete or overdue cases and decide escalation

## Related procedures

Transfer holds linked to expired KYC follow **POL-TRF-001**. Account restrictions may be applied under **POL-RST-001**.
