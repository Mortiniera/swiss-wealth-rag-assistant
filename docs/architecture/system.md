# System Architecture

**As of:** v0.7 (bounded ReAct agent + evidence chips; Compose includes local frontend)

How the running application is wired: HTTP entrypoints, services, and data stores.

## Runtime overview

```mermaid
flowchart TB
  subgraph clients [Clients]
    Postman[Postman / curl]
    UI[React chat UI]
  end

  subgraph compose [Docker Compose — local]
    API[swiss-wealth-api<br/>uvicorn :8000]
    FE[swiss-wealth-frontend<br/>vite :5173]
    PG[(postgres:5432<br/>helvetia_bank + pgvector)]
    PgAdmin[pgadmin:5050]
  end

  subgraph api_app [FastAPI — app.main]
    CoreRouter[app.api.routes<br/>/, /health, /ingest, /ask]
    ClientsRouter[app.api.clients<br/>/clients/*]
  end

  subgraph ask_path [Policy Q&A]
    Orchestrator[app.agent.orchestrator]
    Routing[app.agent.routing + nodes]
    Tools[app.tools]
    Generator[app.rag.generator]
    Hybrid[app.retrieval<br/>vector + FTS + RRF]
    Policies[data/policies/]
    PolicyIngest[POST /ingest<br/>policy_ingest]
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
  Orchestrator --> Routing
  Routing --> Tools
  Routing --> Generator
  Tools --> PG
  Generator --> Hybrid
  Hybrid --> PG
  CoreRouter --> PolicyIngest
  Policies --> PolicyIngest
  PolicyIngest --> PG

  ClientsRouter --> ClientRead
  ClientRead --> Session
  Session --> Models
  Models --> PG

  Seed --> PG
  PgAdmin --> PG
```

## Request paths

| Path | Router | Backend | Data store |
| ---- | ------ | ------- | ---------- |
| `GET /`, `GET /health` | `app.api.routes` | — | — |
| `POST /ingest` | `app.api.routes` | `app.rag.policy_ingest` | PostgreSQL + pgvector |
| Policy ingest (CLI) | — | `scripts/ingest_policies.py` | PostgreSQL + pgvector |
| `POST /ask` | `app.api.routes` | `app.agent.orchestrator` → hybrid retrieval → LLM | PostgreSQL + LLM |
| `GET /actors` | `app.api.actors` | `app.services.actor_read` | PostgreSQL |
| `GET /actors/{code}/workspace` | `app.api.actors` | `app.services.actor_read` | PostgreSQL |
| `GET /clients` | `app.api.clients` | `app.services.client_read` / `actor_read` | PostgreSQL |
| `GET /clients/{ref}` | `app.api.clients` | `app.services.client_read` | PostgreSQL |
| `GET /clients/{ref}/accounts` | `app.api.clients` | `app.services.client_read` | PostgreSQL |
| `GET /clients/{ref}/transactions` | `app.api.clients` | `app.services.client_read` | PostgreSQL |
| `GET /clients/{ref}/interactions` | `app.api.clients` | `app.services.client_read` | PostgreSQL |
| `GET /clients/{ref}/service-requests` | `app.api.clients` | `app.services.client_read` | PostgreSQL |
| `GET /policies` | `app.api.policies` | `app.services.policy_read` | PostgreSQL |
| `GET /policies/{document_id}` | `app.api.policies` | `app.services.policy_read` | PostgreSQL |

Optional header ``X-Helvetia-Actor: EMP-####`` selects a demo employee identity (not login). Relationship managers see assigned clients only; policies and `/ask` retrieval respect ``allowed_roles``. Full RBAC is out of scope for this release.

`{ref}` is a client UUID or stable `client_code` (e.g. `CLI-SCEN-01`).
`{document_id}` is a stable policy code (e.g. `POL-KYC-001`).
`{code}` is a stable `employee_code` (e.g. `EMP-0001`).

## Layering (structured domain)

```text
HTTP request
  → app/api/clients.py
  → app/services/client_read.py
  → app/schemas/clients.py
  → app/database/models/
  → PostgreSQL
```

## Layering (policy `/ask`)

```text
HTTP POST /ask
  → app/agent/orchestrator.py (bounded runner)
  → app/agent/routing.py + nodes/ (classify → agent_turn loop: call_tool | search_policies | finish → rewrite → generate)
  → app/tools (selected read-only client tools when client_ref present)
  → app/rag/generator.py
  → app/retrieval (vector + FTS + RRF, active filters)
  → PostgreSQL knowledge_* tables
  → LLM grounded answer + sources
```

## Local stack

| Service | Image / build | Port | Role |
| ------- | ------------- | ---- | ---- |
| `api` | `Dockerfile` (migrate on start) | 8000 | FastAPI + uvicorn |
| `frontend` | `frontend/Dockerfile` (Vite dev) | 5173 | Chat UI (local DX; prod on Vercel) |
| `postgres` | `pgvector/pgvector:pg16` | 5432 | Domain + knowledge (pgvector) |
| `pgadmin` | `dpage/pgadmin4:8` | 5050 | DB inspection UI |

API connects to Postgres via `DATABASE_URL` host `postgres` inside Compose.  
Browser calls the API at `http://localhost:8000` (`VITE_API_URL`), not the Compose hostname `api`.  
Ingest policies: `POST /ingest` or `docker compose exec api python scripts/ingest_policies.py`.  
Seed clients: `docker compose exec api python scripts/seed_db.py`.

## Related docs

- Business domain: [domain.md](domain.md)
- Table and column detail: [data-model.md](data-model.md)
- Current DB tables and relationships: [database-schema.md](database-schema.md)
- PostgreSQL decision record: [../adr/ADR-001-postgresql.md](../adr/ADR-001-postgresql.md)
- pgvector decision record: [../adr/ADR-002-pgvector.md](../adr/ADR-002-pgvector.md)
- Hybrid retrieval decision record: [../adr/ADR-003-hybrid-retrieval.md](../adr/ADR-003-hybrid-retrieval.md)
