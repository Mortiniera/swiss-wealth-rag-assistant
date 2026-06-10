# Swiss Wealth RAG Assistant

A lightweight Retrieval-Augmented Generation API over public Swiss wealth management content. Answers questions using indexed documents only, with source citations and relevance scores.

Built to demonstrate practical AI engineering: ingestion, embeddings, vector search, grounded generation and FastAPI deployment.

## Stack

- **Python** / **FastAPI** / **Pydantic**
- **LlamaIndex** - document loading, chunking, retrieval
- **ChromaDB** - local vector store
- **OpenAI** - `text-embedding-3-small` (embeddings), configurable LLM for answers

## Data sources

Public summaries from four Swiss private banks (Lombard Odier, UBS, Pictet, Julius Baer), stored as `.txt` files in `data/documents/`.

## API


| Method | Endpoint  | Description               |
| ------ | --------- | ------------------------- |
| GET    | `/health` | Health check              |
| POST   | `/ingest` | Index documents           |
| POST   | `/ask`    | Grounded Q&A with sources |


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

If retrieval confidence is too low, the API returns:

> I could not find enough information in the indexed sources to answer this confidently.

## Local setup

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

cp .env.example .env
# Add your OPENAI_API_KEY to .env

uvicorn app.main:app --reload

```

Then call `POST /ingest` before `POST /ask`.

## Docker

```bash
docker build -t swiss-wealth-rag .
docker run -p 8000:8000 --env-file .env swiss-wealth-rag
```

## Deploy

1. Connect the GitHub repo
2. Set environment variables from .env.example (at minimum OPENAI_API_KEY)
3. Start command: uvicorn app.main:app --host 0.0.0.0 --port $PORT
4. After deploy, call POST /ingest to index documents

Note: The vector store is local filesystem storage. On ephemeral hosts, re-run /ingest after each redeploy unless you add persistent disk.

## Project structure

```bash
app/
  api/routes.py      # FastAPI endpoints
  rag/
    ingest.py        # Load, chunk, embed, store
    retriever.py     # Vector search
    generator.py     # Grounded LLM answers
    common.py        # Shared config helpers
  config.py          # Settings from .env
  models/schemas.py  # Request/response models
data/documents/      # Source corpus
vector_store/        # ChromaDB (generated, gitignored)
```

Limitations (MVP)

- No authentication
- No UI
- Single-node ChromaDB (no hosted vector DB)
- English only


## Live demo

**API:** https://swiss-wealth-rag-assistant.onrender.com  
**Docs:** https://swiss-wealth-rag-assistant.onrender.com/docs
**Health:** https://swiss-wealth-rag-assistant.onrender.com/health

> On the free tier, the service may sleep after inactivity (cold start ~30–60s).
> Run `POST /ingest` after each redeploy to rebuild the vector index.

