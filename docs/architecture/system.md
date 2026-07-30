# System Architecture

**As of:** v0.3 (incremental through v0.36)

How the running application is wired: HTTP entrypoints, services, and data stores.

## Runtime overview

![System architecture — v0.3](assets/system-v0.3.png)

<details>
<summary>Mermaid source (editable)</summary>

```mermaid
flowchart TB
  subgraph clients [Clients]
    Postman[Postman / curl]
    UI[React chat UI]
  end

  subgraph compose [Docker Compose — local]
    API[swiss-wealth-api<br/>uvicorn :8000]
    PG[(postgres:5432<br/>helvetia_bank)]
    PgAdmin[pgadmin:5050]
  end

  subgraph api_app [FastAPI — app.main]
    CoreRouter[app.api.routes<br/>/, /health, /ingest, /ask]
    ClientsRouter[app.api.clients<br/>/clients/*]
  end

  subgraph rag [Document RAG — parallel path]
    Orchestrator[app.assistant.orchestrator]
    Retriever[app.rag.retriever]
    Chroma[(ChromaDB<br/>vector_store/)]
    Docs[data/documents/]
  end

  subgraph domain [Structured domain]
    ClientRead[app.services.client_read]
    Session[app.database.session]
    Models[app.database.models]
    Seed[scripts/seed_db.py]
  end

  Postman --> API
  UI --> API
  API --> CoreRouter
  API --> ClientsRouter

  CoreRouter --> Orchestrator
  Orchestrator --> Retriever
  Retriever --> Chroma
  Docs -. ingest .-> Chroma

  ClientsRouter --> ClientRead
  ClientRead --> Session
  Session --> Models
  Models --> PG

  Seed --> PG
  PgAdmin --> PG
```

</details>

## Request paths

| Path | Router | Backend | Data store |
| ---- | ------ | ------- | ---------- |
| `GET /`, `GET /health` | `app.api.routes` | — | — |
| `POST /ingest` | `app.api.routes` | `app.rag.ingest` | ChromaDB |
| `POST /ask` | `app.api.routes` | `app.assistant.orchestrator` → RAG | ChromaDB + LLM |
| `GET /clients/{ref}` | `app.api.clients` | `app.services.client_read` | PostgreSQL |
| `GET /clients/{ref}/accounts` | `app.api.clients` | `app.services.client_read` | PostgreSQL |
| `GET /clients/{ref}/transactions` | `app.api.clients` | `app.services.client_read` | PostgreSQL |
| `GET /clients/{ref}/interactions` | `app.api.clients` | `app.services.client_read` | PostgreSQL |
| `GET /clients/{ref}/service-requests` | `app.api.clients` | `app.services.client_read` | PostgreSQL |

`{ref}` is a client UUID or stable `client_code` (e.g. `CLI-SCEN-01`).

## Layering (structured domain)

```text
HTTP request
  → app/api/clients.py          (routing, 404)
  → app/services/client_read.py (queries, mapping)
  → app/schemas/clients.py      (Pydantic response shapes)
  → app/database/models/        (SQLAlchemy ORM)
  → PostgreSQL
```

## Local stack

| Service | Image / build | Port | Role |
| ------- | ------------- | ---- | ---- |
| `api` | `Dockerfile` | 8000 | FastAPI + uvicorn |
| `postgres` | `pgvector/pgvector:pg16` | 5432 | Domain + knowledge (pgvector) |
| `pgadmin` | `dpage/pgadmin4:8` | 5050 | DB inspection UI |

API connects to Postgres via `DATABASE_URL` host `postgres` inside Compose.

## Related docs

- Business domain: [domain.md](domain.md)
- Table and column detail: [data-model.md](data-model.md)
- Current DB tables and relationships: [database-schema.md](database-schema.md)
- PostgreSQL decision record: [../adr/ADR-001-postgresql.md](../adr/ADR-001-postgresql.md)
- pgvector decision record: [../adr/ADR-002-pgvector.md](../adr/ADR-002-pgvector.md)
