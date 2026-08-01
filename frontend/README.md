# Helvetia Operations — Frontend

React UI for the Helvetia operations workspace. Structured client/policy surfaces are the primary work area; the policy assistant is a docked panel that calls `POST /ask`.

**Live app:** [swiss-wealth-rag-assistant.vercel.app](https://swiss-wealth-rag-assistant.vercel.app)

## Stack

- React 19 + TypeScript
- Vite
- Tailwind CSS v4
- Fetch API (no extra HTTP client)

## Features

- Operations shell: brand chrome, left nav rail, persona control
- Client directory from seeded clients with profile/KYC, accounts, transactions, service requests, and interactions
- Work canvas placeholder for Policies (catalog next)
- Collapsible assistant dock with conversation thread and source cards
- Error handling for API failures

## Project structure

```
src/
  api/
    banking.ts                # /clients list + detail endpoints
    ask.ts                    # POST /ask
    types.ts                  # Shared API types
  components/
    ui/                       # Reusable primitives (Button, Modal, DataTable…)
    shell/                    # App chrome (AppShell, TopBar, NavRail…)
    workspace/                # Clients / Policies work surface
    assistant/                # Dock, chat, rich text, sources
  hooks/
    useChat.ts                # Conversation state + /ask calls
    useClients.ts             # Directory list + filter
    useClientDetail.ts        # Profile + activity panels
  types/
    workspace.ts              # Persona / nav ids
    chat.ts                   # Message model
  utils/
    cn.ts                     # className helper
    clientDisplay.ts          # Labels, money, status tones
    paths.ts                  # path display helpers
    richText.ts               # Pure markdown-lite parser
    sourceDisplay.ts          # Source headings / relevance
  App.tsx
  main.tsx
```

## Local setup

**Option A — full stack via Compose** (from repo root):

```bash
docker compose up --build
```

Open `http://localhost:5173`. The Compose `frontend` service runs Vite dev and sets `VITE_API_URL=http://localhost:8000` (browser → host-mapped API). Production UI remains on Vercel.

**Option B — frontend only** (API already running):

```bash
npm install
cp .env.example .env.local
npm run dev
```

From the repo root, start the backend first if needed:

```bash
uvicorn app.main:app --reload
# or: docker compose up api postgres
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
