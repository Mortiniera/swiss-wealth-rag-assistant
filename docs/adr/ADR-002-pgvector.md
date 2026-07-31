# ADR-002: pgvector for Knowledge Embeddings

## Status

Accepted

## Context

Helvetia internal policies need versioned metadata, role filters, and vector similarity search alongside the existing structured banking domain in PostgreSQL. The application still uses ChromaDB on the filesystem for the public-bank `/ask` path, but that store cannot share transactional metadata or filters with Postgres.

## Decision

Store knowledge document metadata and chunk embeddings in PostgreSQL using the **pgvector** extension.

- Local Compose uses the `pgvector/pgvector:pg16` image
- Schema lives in `knowledge_documents` and `knowledge_chunks`
- Embedding dimensionality is **1536** (`text-embedding-3-small`)
- Chroma remains temporarily for the existing `/ask` path until the retrieval cutover completes

## Alternatives considered

| Option | Why not chosen |
| ------ | -------------- |
| Keep Chroma only | Splits metadata/filters from the domain database; harder to enforce active/role filters in one place |
| Dual-write Chroma + Postgres permanently | Extra operational surface without a clear long-term benefit |
| External managed vector DB | Unnecessary complexity for this project’s local/demo scope |

## Consequences

### Positive

- One operational database for structured domain data and knowledge vectors
- Document status, roles, jurisdiction, and confidentiality stay queryable with SQL
- Migrations version the knowledge schema with Alembic

### Trade-offs

- Requires a pgvector-capable Postgres image (existing volumes must be recreated or upgraded)
- Ingest and `/ask` cutover are separate follow-up work; tables start empty

## Validation

- Alembic revision `0002_pgvector_knowledge` enables `vector` and creates the knowledge tables
- ORM models: `app.database.models.knowledge`
- Policy load: `app.rag.policy_registry`
- Policy ingest into Postgres: `scripts/ingest_policies.py` (`app.rag.policy_ingest`)
