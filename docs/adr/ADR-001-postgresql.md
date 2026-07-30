# ADR-001: PostgreSQL as Domain System of Record

## Status

Accepted

## Context

The application now serves structured client, account, compliance, and operations data through read-only APIs. This data must support deterministic seed runs, relational integrity, and repeatable scenario-based verification.

File-based storage and vector-only persistence do not provide the relational model needed for client-to-account coverage, KYC profiles, restrictions, transactions, interactions, and service requests.

## Decision

Use PostgreSQL as the authoritative data store for structured banking domain data.

- Access is handled through SQLAlchemy ORM models
- Schema evolution is handled through Alembic migrations
- Synthetic data is generated through deterministic seed scripts
- Local development runs PostgreSQL in Docker Compose

## Consequences

### Positive

- Strong relational consistency across domain entities
- Deterministic seeded datasets for repeatable API and demo flows
- Clear migration path for schema evolution in versioned releases
- Shared local setup through Compose for environment parity

### Trade-offs

- Added operational dependency on a database service
- Migration discipline is required for every schema change

## Implementation Notes

- Core configuration lives in `app/config.py` (`DATABASE_URL`)
- Engine/session setup lives in `app/database/session.py`
- Models are under `app/database/models/`
- Initial schema is created by `alembic/versions/0001_initial_helvetia_schema.py`
- Seed entrypoint is `scripts/seed_db.py`
