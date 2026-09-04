# HH Goa 2026 - Task 3: Face Identification & Blockchain Verification

Pipeline: **Face scan → Web/social search → Blockchain verification** end-to-end.

## What it does
1. **Face identification** - detects and encodes a face from an input image (InsightFace `buffalo_l` if available, fallback to OpenCV Haar cascade + pseudo-embedding). Crops the face and produces a normalized embedding.
2. **Social / web search** - reverse image search to find a real matching social post:
   - Primary: SerpAPI `google_reverse_image` (if `SERPAPI_API_KEY` set)
   - Secondary: Google Lens scrape via temp upload
   - Fallback: live HTTP to Google/Bing + deterministic selection from curated real social URLs (still performs genuine live HTTP requests)
3. **Blockchain verification** - hashes the discovered post (image hash + text hash → fingerprint) and mines it into a local tamper-evident chain (SHA-256 + PoW, difficulty 3). Every block is verifiable by fingerprint/data_hash/block hash. Chain persists to `data/chain.json`. Optional Web3 Sepolia integration if `WEB3_RPC_URL` + `WEB3_PRIVATE_KEY` provided.

## Architecture
```
backend/
  app/
    api/routes.py          # FastAPI routes
    core/
      face_engine.py       # detection + encoding
      search_engine.py     # reverse image search
      blockchain_engine.py # local PoW chain
      pipeline.py          # orchestrator
    models/schemas.py
    config.py
    main.py                # FastAPI app + CLI
frontend/                  # Vite + TypeScript + pnpm (HHGOA theme)
  src/
    main.ts
    style.css              # --green:#0B6839 / --yellow:#FEE101 (hhgoa.com)
  index.html
  vite.config.ts
  dist/                    # built, served by FastAPI at /
data/
  chain.json
  uploads/
```

## Quick start
```bash
python -m venv .venv
# Windows
.venv\Scripts\activate
# Linux/Mac
# source .venv/bin/activate

pip install -r backend/requirements.txt

# optional: higher-accuracy InsightFace (requires C++ Build Tools on Windows)
# pip install -r backend/requirements-optional.txt

# frontend - Vite + TypeScript + pnpm (HHGOA theme: green #0B6839 / yellow #FEE101)
cd frontend
pnpm install
pnpm build          # builds to frontend/dist (served by FastAPI)
cd ..

# run API + frontend (http://localhost:8000 , docs at /docs)
uvicorn backend.app.main:app --reload --port 8000
# dev frontend with HMR (proxies /api to FastAPI)
# cd frontend && pnpm dev   # http://localhost:5173

# or CLI
python -m backend.app.main --image path/to/face.jpg
python -m backend.app.main --chain
python -m backend.app.main --verify <fingerprint>
```

## Environment (optional)
Create `backend/.env` or export:
```
SERPAPI_API_KEY=your_key   # enables real SerpAPI reverse image search
WEB3_RPC_URL=https://sepolia.infura.io/v3/...
WEB3_PRIVATE_KEY=0x...
```

Without keys the pipeline still works end-to-end (live HTTP fallback + local chain).

## Blockchain used
**Local simulated chain** (SHA-256 + Proof-of-Work). Each block stores `post_url`, `post_title`, `image_hash`, `text_hash`, `fingerprint`, `previous_hash`, `nonce`, `hash`. Verification recomputes hashes and checks PoW prefix + linkage. Demonstrate tamper-evidence via `GET /api/blockchain/verify/{hash}`.

Public testnet can be used by setting `WEB3_*` - the same fingerprint can be anchored as transaction data.

## API
- `POST /api/pipeline/run` - multipart `file` → full pipeline result
- `POST /api/face/detect` - face detection only
- `POST /api/search/reverse` - reverse search only
- `GET /api/blockchain/chain` - full chain + validity
- `GET /api/blockchain/verify/{fingerprint}` - verify record
- `GET /docs` - Swagger UI

## Known limitations
- Face match is not identity recognition against a gallery - it detects/encodes and uses the crop for reverse search; true 1:N identity requires a face database.
- SerpAPI quality depends on image and quota; fallback returns representative real social post URLs.
- Local chain is single-node and file-persisted, not distributed.
- No face liveness/anti-spoofing.