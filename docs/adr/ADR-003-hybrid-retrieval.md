# ADR-003: Hybrid Retrieval (pgvector + Postgres FTS)

## Status

Accepted

## Context

Policy answers need both semantic matches (paraphrases) and lexical matches (stable IDs, exact phrases). A vector-only path misses rare tokens; FTS-only misses wording variation. Ranking scores from the two channels are not on the same scale.

## Decision

Implement a hybrid baseline in `app/retrieval/`:

1. Filter documents in SQL (default `status = active`, optional role/jurisdiction/category)
2. Run pgvector cosine nearest-neighbor search over chunk embeddings
3. Run Postgres full-text search over chunk text (`content_tsv` + GIN)
4. Merge candidate lists with **Reciprocal Rank Fusion (RRF)** — rank-based, no score calibration
5. Establish this baseline before adding a reranker

`/ask` uses hybrid retrieval against active Helvetia policies in PostgreSQL. ChromaDB has been removed from the operational path.

## Alternatives considered

| Option | Why not chosen now |
| ------ | ------------------ |
| Vector only | Weak on exact policy IDs and rare terms |
| FTS only | Weak on paraphrases |
| Weighted score sum | Requires complex tuning across incompatible score ranges |
| Reranker first | Extra cost/complexity before a measurable baseline |

## Consequences

### Positive

- One Postgres store for filters, vectors and lexical search
- RRF is simple to implement and test
- Clear place to test/compare a reranker later against this baseline

### Trade-offs

- Two queries per retrieve (vector + FTS)
- HNSW search is approximate at large scale (acceptable; exact scan fine for small corpora)

## Validation

- Unit tests for RRF merge
- Integration retrieve prefers active KYC policy over superseded when data is ingested
