# Data Model

Minimum relational model for Helvetia Private Bank. Only fields required by the flagship use cases ([use-cases.md](use-cases.md)) and the curated scenarios are included. This is not a full core-banking schema.

See also: [domain.md](domain.md).

## Conventions

| Topic | Rule |
| ----- | ---- |
| Primary keys | UUID (`id`) |
| External codes | Stable string codes for demos (e.g. `CLI-000123`, `ACC-000045`) |
| Money | `Numeric(18, 2)` + ISO currency code |
| Timestamps | Timezone-aware UTC (`DateTime(timezone=True)`) |
| Soft deletes | Not used — rows are replaced by reseed |
| Naming | `snake_case` tables and columns |

## Entity relationship overview

```text
Role 1──* Employee
Employee *──* Client          (via ClientAssignment)
Household 1──* Client
Client 1──* Account
Account 1──1 Portfolio
Portfolio 1──* Holding
Account 1──* Transaction
Client 1──1 KYCProfile
Client 1──1 SuitabilityProfile
Client 1──1 CommunicationPreference
Client 1──* ServiceRequest
Client 1──* Interaction
Account 1──* Restriction
Client 1──* Restriction       (optional client-level)
* AuditEvent                  (polymorphic refs by entity_type + entity_id)
```

## Entities and fields

### Role

| Column | Type | Notes |
| ------ | ---- | ----- |
| id | UUID PK | |
| code | String unique | `relationship_manager`, `client_service`, `compliance_viewer` |
| name | String | Display name |

### Employee

| Column | Type | Notes |
| ------ | ---- | ----- |
| id | UUID PK | |
| employee_code | String unique | e.g. `EMP-0001` |
| full_name | String | Synthetic |
| email | String unique | Synthetic |
| role_id | FK → Role | |
| is_active | Boolean | |

### Household

| Column | Type | Notes |
| ------ | ---- | ----- |
| id | UUID PK | |
| household_code | String unique | e.g. `HH-0001` |
| display_name | String | Family / household label |

### Client

| Column | Type | Notes |
| ------ | ---- | ----- |
| id | UUID PK | |
| client_code | String unique | e.g. `CLI-000123` |
| full_name | String | Synthetic |
| email | String | Synthetic |
| residency_country | String | ISO 3166-1 alpha-2 |
| status | String | `active`, `dormant`, `onboarding`, `closed` |
| household_id | FK → Household nullable | |
| segment | String | e.g. `hnwi`, `uhnw` |
| created_at | DateTime TZ | |

### ClientAssignment

| Column | Type | Notes |
| ------ | ---- | ----- |
| id | UUID PK | |
| client_id | FK → Client | |
| employee_id | FK → Employee | |
| is_primary | Boolean | Primary RM |
| assigned_at | DateTime TZ | |

### Account

| Column | Type | Notes |
| ------ | ---- | ----- |
| id | UUID PK | |
| account_code | String unique | e.g. `ACC-000045` |
| client_id | FK → Client | |
| account_type | String | `current`, `custody`, `loan` |
| currency | String | ISO 4217 |
| status | String | `open`, `restricted`, `closed` |
| iban_synthetic | String | Fictional IBAN-like id |
| opened_at | DateTime TZ | |

### Portfolio

| Column | Type | Notes |
| ------ | ---- | ----- |
| id | UUID PK | |
| account_id | FK → Account unique | One portfolio per account |
| name | String | |
| base_currency | String | |
| as_of | DateTime TZ | Valuation date |

### Holding

| Column | Type | Notes |
| ------ | ---- | ----- |
| id | UUID PK | |
| portfolio_id | FK → Portfolio | |
| asset_symbol | String | e.g. `CHF`, `NESN.SW` |
| asset_name | String | |
| quantity | Numeric | |
| market_value | Numeric(18,2) | |
| currency | String | |

### Transaction

| Column | Type | Notes |
| ------ | ---- | ----- |
| id | UUID PK | |
| account_id | FK → Account | |
| transaction_code | String unique | e.g. `TXN-000901` |
| txn_type | String | `transfer_out`, `transfer_in`, `fee`, `dividend`, `trade` |
| amount | Numeric(18,2) | |
| currency | String | |
| status | String | `booked`, `pending`, `delayed`, `failed`, `cancelled` |
| booked_at | DateTime TZ nullable | |
| value_date | DateTime TZ nullable | |
| counterparty_name | String nullable | Synthetic |
| description | String | |
| delay_reason_code | String nullable | e.g. `kyc_expired`, `account_restricted` |
| is_unusual | Boolean | Flag for unusual / high-value review |
| created_at | DateTime TZ | |

### KYCProfile

| Column | Type | Notes |
| ------ | ---- | ----- |
| id | UUID PK | |
| client_id | FK → Client unique | |
| status | String | `valid`, `expired`, `incomplete`, `under_review` |
| document_type | String | e.g. `passport`, `id_card` |
| document_expiry | Date | |
| last_reviewed_at | DateTime TZ nullable | |
| notes | String nullable | |

### SuitabilityProfile

| Column | Type | Notes |
| ------ | ---- | ----- |
| id | UUID PK | |
| client_id | FK → Client unique | |
| status | String | `complete`, `missing`, `outdated` |
| risk_profile | String nullable | e.g. `conservative`, `balanced`, `growth` |
| completed_at | DateTime TZ nullable | |

### CommunicationPreference

| Column | Type | Notes |
| ------ | ---- | ----- |
| id | UUID PK | |
| client_id | FK → Client unique | |
| preferred_channel | String | `email`, `phone`, `letter`, `secure_message` |
| marketing_opt_in | Boolean | |
| cross_border_ok | Boolean | False → cross-border communication restriction |
| language | String | e.g. `en`, `fr`, `de` |

### Restriction

| Column | Type | Notes |
| ------ | ---- | ----- |
| id | UUID PK | |
| client_id | FK → Client nullable | |
| account_id | FK → Account nullable | At least one of client/account set |
| restriction_type | String | e.g. `debit_block`, `transfer_hold`, `communication_block` |
| reason_code | String | e.g. `kyc_expired`, `compliance_review` |
| status | String | `active`, `lifted` |
| effective_from | DateTime TZ | |
| effective_to | DateTime TZ nullable | |
| notes | String nullable | |

### ServiceRequest

| Column | Type | Notes |
| ------ | ---- | ----- |
| id | UUID PK | |
| request_code | String unique | e.g. `SR-000201` |
| client_id | FK → Client | |
| request_type | String | `kyc_refresh`, `complaint`, `document_upload`, `onboarding`, `other` |
| status | String | `open`, `in_progress`, `resolved`, `cancelled` |
| priority | String | `low`, `medium`, `high` |
| subject | String | |
| opened_at | DateTime TZ | |
| sla_due_at | DateTime TZ nullable | |
| resolved_at | DateTime TZ nullable | |
| assigned_employee_id | FK → Employee nullable | |

### Interaction

| Column | Type | Notes |
| ------ | ---- | ----- |
| id | UUID PK | |
| client_id | FK → Client | |
| employee_id | FK → Employee nullable | |
| channel | String | `email`, `phone`, `meeting`, `note` |
| direction | String | `inbound`, `outbound`, `internal` |
| subject | String | |
| summary | String | |
| occurred_at | DateTime TZ | |
| related_service_request_id | FK → ServiceRequest nullable | |
| status | String | `logged`, `awaiting_reply`, `closed` |

### AuditEvent

| Column | Type | Notes |
| ------ | ---- | ----- |
| id | UUID PK | |
| event_type | String | e.g. `data_access`, `scenario_seed`, `status_note` |
| actor_employee_id | FK → Employee nullable | |
| entity_type | String | e.g. `client`, `account`, `transaction` |
| entity_id | UUID nullable | |
| payload_json | JSON | Small structured context |
| created_at | DateTime TZ | |

## Scenario registry (seed metadata)

Curated scenarios are not a separate runtime table. They are applied as **deterministic seed overrides**. Stable codes and case facts are listed in [../demo-scenarios/scenarios.md](../demo-scenarios/scenarios.md).

## Non-goals

- Full payment messaging (SWIFT/ISO 20022)
- Multi-portfolio per account complexity
- Historical slowly-changing dimensions
- Write APIs or transactional consistency beyond seed/reset
