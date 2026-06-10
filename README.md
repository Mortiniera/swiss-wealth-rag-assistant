# Swiss Wealth RAG Assistant

A lightweight Retrieval-Augmented Generation API over synthetic Swiss wealth management content. Answers questions using indexed documents only, with structured source citations and relevance scores.

Built to demonstrate practical AI engineering: ingestion, embeddings, vector search, grounded generation, and FastAPI deployment.

## Stack

- **Python** / **FastAPI** / **Pydantic**
- **LlamaIndex** — document loading, chunking, retrieval
- **ChromaDB** — local vector store
- **OpenAI** — `text-embedding-3-small` (embeddings), configurable LLM for answers

## Data sources

The corpus contains **17 synthetic `.txt` files** in `data/documents/`, covering four Swiss private banks (Lombard Odier, UBS, Pictet, Julius Baer) plus institution-specific topic documents (sustainability, family governance, digital banking, private markets, and more).

Each file is mapped to an institution and document title via `app/rag/metadata.py` at ingest time.

> **Disclaimer:** These documents are synthetic demonstration content. They are paraphrased and inspired by public themes from major Swiss wealth management institutions, but they are **not official publications** and must not be presented as official bank content.

## API


| Method | Endpoint  | Description                           |
| ------ | --------- | ------------------------------------- |
| GET    | `/`       | Service metadata (name, docs, health) |
| GET    | `/health` | Health check                          |
| POST   | `/ingest` | Index documents                       |
| POST   | `/ask`    | Grounded Q&A with sources             |


Interactive docs: `http://localhost:8000/docs`

---

## Architecture

```
┌─────────────┐     ┌──────────────┐     ┌─────────────┐     ┌──────────────┐
│   Client    │────▶│  FastAPI     │────▶│  Retriever  │────▶│   ChromaDB   │
│  (curl/UI)  │     │  /ask        │     │  (top-k)    │     │ vector_store │
└─────────────┘     └──────┬───────┘     └─────────────┘     └──────────────┘
                           │
                           ▼
                    ┌──────────────┐     ┌─────────────┐
                    │  Generator   │────▶│   OpenAI    │
                    │  (prompt)    │     │     LLM     │
                    └──────────────┘     └─────────────┘

Startup (lifespan):
  ensure_index() → ingest if vector store is empty
```

### Example

```bash
# Index documents
curl -X POST http://localhost:8000/ingest \
  -H "Content-Type: application/json" \
  -d '{"source_dir": "data/documents"}'

# Ask a question
curl -X POST http://localhost:8000/ask \
  -H "Content-Type: application/json" \
  -d '{"question": "How do Swiss private banks approach sustainable investing?"}'
```

Example `POST /ask` response:

```json
{
  "answer": "Swiss private banks increasingly integrate sustainability into long-term investment frameworks...",
  "sources": [
    {
      "institution": "Lombard Odier",
      "document_title": "Sustainability Transition and Long-Term Investing",
      "source_file": "lombard_odier_sustainability_transition.txt",
      "chunk_id": "abc123",
      "score": 0.82
    }
  ]
}
```

If retrieval confidence is too low, the API returns:

> I could not find enough information in the indexed sources to answer this confidently.

## Architecture

Architecture

On startup, `ensure_index()` runs when `AUTO_INGEST_ON_STARTUP=true` (default): it ingests documents if the vector store is empty.

## API docs

Swagger UI (`/docs`):

Swagger UI

Example `POST /ask` response in the interactive docs:

Ask response

## Local setup

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

cp .env.example .env
# Add your OPENAI_API_KEY to .env

uvicorn app.main:app --reload
```

With `AUTO_INGEST_ON_STARTUP=true` (default), the index is built on first startup. Otherwise, call `POST /ingest` before `POST /ask`.

### Tests

```bash
pip install -r requirements.txt -r requirements-dev.txt
pytest
```

Tests cover health and root endpoints, request validation, and the `/ask` response schema (including source attribution fields).

## Docker

```bash
docker build -t swiss-wealth-rag .
docker run -p 8000:8000 --env-file .env swiss-wealth-rag
```

## Deploy

Deployed on Render from the `**main**` branch.

1. Connect the GitHub repo and set the deploy branch to `main`
2. Set environment variables from `.env.example` (at minimum `OPENAI_API_KEY`)
3. Start command: `uvicorn app.main:app --host 0.0.0.0 --port $PORT`
4. After each redeploy, re-run `POST /ingest` to rebuild the vector index

The vector store is local filesystem storage. On ephemeral hosts, the index is wiped on redeploy — `AUTO_INGEST_ON_STARTUP=true` handles a fresh ingest when the store is empty, but calling `POST /ingest` explicitly is still recommended after deploy.

## Project structure

```
app/
  api/routes.py      # FastAPI endpoints
  rag/
    ingest.py        # Load, chunk, embed, store
    retriever.py     # Vector search
    generator.py     # Grounded LLM answers
    metadata.py      # Filename → institution, document title
    common.py        # Shared config helpers
  config.py          # Settings from .env
  models/schemas.py  # Request/response models
  main.py            # App + startup lifespan (auto-ingest)
data/documents/      # Synthetic source corpus (17 .txt files)
docs/assets/         # README screenshots
tests/               # pytest suite
vector_store/        # ChromaDB (generated, gitignored)
```

## Limitations

- No authentication
- No UI (API only)
- Single-node ChromaDB (no hosted vector DB)
- English only

## Live demo

**API:** [https://swiss-wealth-rag-assistant.onrender.com](https://swiss-wealth-rag-assistant.onrender.com)  
**Docs:** [https://swiss-wealth-rag-assistant.onrender.com/docs](https://swiss-wealth-rag-assistant.onrender.com/docs)  
**Health:** [https://swiss-wealth-rag-assistant.onrender.com/health](https://swiss-wealth-rag-assistant.onrender.com/health)

> On the free tier, the service may sleep after inactivity (cold start ~30–60s).  
> Run `POST /ingest` after each redeploy to rebuild the vector index.