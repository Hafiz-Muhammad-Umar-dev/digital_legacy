# Digital Legacy – Next.js Frontend

Next.js 14 (App Router) + TypeScript + Tailwind frontend for the Digital Legacy API.

## Setup

```bash
npm install
cp .env.local.example .env.local   # NEXT_PUBLIC_API_URL set karein
npm run dev                        # http://localhost:3000
```

## Backend requirement: CORS
FastAPI me frontend origin allow karna zaroori hai:

```python
from fastapi.middleware.cors import CORSMiddleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

## Structure
- `src/lib/api.ts` – saare endpoints ka typed client (auto token refresh on 401)
- `src/lib/types.ts` – schema types
- `src/lib/auth-context.tsx` – login / register / logout / me
- `src/app/login`, `register` – auth pages
- `src/app/(app)/personas` – list/create, `[id]` – Chat, Memories, Videos, History tabs
- `src/components/*` – panels

## Assumptions (Swagger ke schemas check kar ke adjust karein)
- Login form-encoded hai (`username` = email, `password`)
- Refresh/logout body: `{ "refresh_token": "..." }`
- Chat request: `{ persona_id, message, conversation_id }`, reply field: `reply` / `response` / `message`
- Video upload multipart field name: `file`
- TTS response me `audio_url` / `url` / `filename`
- `VoiceChatRequest` ka UI abhi nahi bana (`chat.voice` client me ready hai)

Fields alag hon to sirf `types.ts` aur `api.ts` badalna kaafi hoga.
