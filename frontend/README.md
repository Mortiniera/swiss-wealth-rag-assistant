# Swiss Wealth RAG Assistant — Frontend

React chat UI for the [Swiss Wealth RAG Assistant](../README.md) backend. Sends questions to `POST /ask` and displays grounded answers with source cards.

**Live app:** [swiss-wealth-rag-assistant.vercel.app](https://swiss-wealth-rag-assistant.vercel.app)

## Stack

- React 19 + TypeScript
- Vite
- Fetch API (no extra HTTP client)

## Features

- Question input with loading state
- Conversation thread (client-side state only)
- Assistant messages with source cards (institution, document title, file, score)
- Error handling for API failures

## Project structure

```
src/
  api/
    client.ts           # askQuestion(), types matching backend schemas
  components/
    ChatWindow.tsx      # Thread state, API calls
    MessageBubble.tsx   # User / assistant message layout
    SourceCard.tsx      # Single source attribution card
    QueryInput.tsx      # Question form
  App.tsx
  main.tsx
```

## Local setup

From the repo root, start the backend first:

```bash
uvicorn app.main:app --reload
```

Then in `frontend/`:

```bash
npm install
cp .env.example .env.local
npm run dev
```

Open `http://localhost:5173`.

### Environment variables

| Variable | Description |
| -------- | ----------- |
| `VITE_API_URL` | Backend base URL (default: `http://localhost:8000`) |

Local example (`.env.local`):

```env
VITE_API_URL=http://localhost:8000
```

Do not commit `.env` or `.env.local`. Only variables prefixed with `VITE_` are exposed to the browser.

The backend must allow `http://localhost:5173` in CORS (`app/main.py`).

## Build

```bash
npm run build
npm run preview   # optional: preview production build locally
```

## Deploy (Vercel)

1. Import the GitHub repo on [Vercel](https://vercel.com)
2. Set **Root Directory** to `frontend`
3. Add environment variable:

   | Name | Value |
   | ---- | ----- |
   | `VITE_API_URL` | `https://swiss-wealth-rag-assistant.onrender.com` |

4. Deploy
5. Add the Vercel URL to `allow_origins` in `app/main.py` and redeploy the backend on Render

## API contract

The UI calls:

```http
POST {VITE_API_URL}/ask
Content-Type: application/json

{"question": "..."}
```

Response shape (see backend `app/models/schemas.py`):

```typescript
{
  answer: string;
  sources: {
    institution: string;
    document_title: string;
    source_file: string;
    chunk_id: string;
    score: number;
  }[];
}
```

For backend architecture, ingestion, and deployment details, see the [root README](../README.md).
