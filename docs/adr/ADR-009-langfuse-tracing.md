# ADR-009: Langfuse Observability and Trace Correlation

## Status

Accepted

## Context

v0.7 shipped a bounded ReAct agent with read-only tools and policy search, but `/ask` decisions were only visible in application logs. Observable, auditable and quality workflows need end-to-end traces: intent, tool rounds, retrieval, LLM calls, latency and token cost, without making Langfuse mandatory for local or production cold start.

## Decision

Add **opt-in Langfuse** behind `app/observability/`:

1. **Init at API startup** — `LANGFUSE_PUBLIC_KEY` + `LANGFUSE_SECRET_KEY` (+ optional `LANGFUSE_BASE_URL`). Missing keys → no-op; API behaviour unchanged.
2. **One trace per `POST /ask`** — root `ask` chain with child spans for workflow steps (`classify`, `agent_turn`, `run_tools`, `search_policies`, `rewrite`, `generate`).
3. **Per-tool and generation spans** — tool children record `ok` / `error_code`; LLM calls record model, latency, token usage when available.
4. **PII hygiene** — span attributes use codes (`CLI-SCEN-01`, `EMP-*`, role) and lengths — not full question text, emails, or tool payloads.
5. **Log ↔ trace correlation** — the workflow completion log line includes `trace_id`, the same identifier Langfuse uses for that `/ask` run. Use it to jump from server logs to the matching trace.
6. **Dev trace link** — optional `trace_url` on `/ask` when `APP_ENV=dev` only (never in production responses): a UI shortcut to open that trace in Langfuse without copying the id from logs.
7. **Flush after each ask** — traces appear promptly in Langfuse Cloud.

## Alternatives considered

| Option | Why not chosen |
| ------ | -------------- |
| Mandatory Langfuse in Compose | Breaks zero-config local demo; violates clean-add rule |
| Log-only observability | No trace UI; per-request token/cost not surfaced; slow to debug multi-step agent runs or compare behaviour across requests |
| Embed Langfuse UI in React | Auth/CORS friction; duplicates Langfuse product |
| Public traces by default | Leaks internal agent decisions; demo data still sensitive |

## Consequences

### Positive

- Every important `/ask` is inspectable when keys are set
- Engineers can correlate logs with Langfuse via `trace_id`, or use the dev-only trace link in the assistant UI
- Governance can later attach auth decisions to existing spans

### Trade-offs

- Extra SDK dependency and OpenTelemetry pin alignment
- Langfuse Cloud account required for hosted traces (free tier sufficient for demo)
- `trace_url` requires Langfuse project membership (private traces)

## Validation

- Unit tests: no-op without keys; mocked client for span/generation helpers; `APP_ENV=prod` never returns `trace_url`
- Manual: one `/ask` visible end-to-end in Langfuse with tools + generations
