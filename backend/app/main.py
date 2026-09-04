import argparse
import json
from pathlib import Path
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from app.api.routes import router
from app.config import BASE_DIR

app = FastAPI(title="HH Goa - Face Identification & Blockchain Verification", version="1.0.0")

app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_credentials=True, allow_methods=["*"], allow_headers=["*"])
app.include_router(router, prefix="/api")

frontend_dir = BASE_DIR / "frontend"
if frontend_dir.exists():
    app.mount("/static", StaticFiles(directory=str(frontend_dir)), name="static")

@app.get("/")
async def serve_frontend():
    idx = frontend_dir / "index.html"
    if idx.exists():
        return FileResponse(str(idx))
    return {"status": "ok", "docs": "/docs"}

@app.get("/health")
async def health():
    return {"status": "ok"}

def cli():
    parser = argparse.ArgumentParser(description="Face -> Search -> Blockchain pipeline")
    parser.add_argument("--image", required=True, help="Path to face image")
    parser.add_argument("--verify", help="Fingerprint to verify (instead of running pipeline)")
    parser.add_argument("--chain", action="store_true", help="Print blockchain")
    args = parser.parse_args()

    from app.core.pipeline import Pipeline
    p = Pipeline()

    if args.verify:
        print(json.dumps(p.verify_fingerprint(args.verify), indent=2))
        return
    if args.chain:
        print(json.dumps(p.get_chain(), indent=2))
        return

    result = p.run(args.image)
    print(json.dumps(result, indent=2))
    print(f"\nVerified: {result['verify']['verified']} | Block hash: {result['blockchain']['hash'][:16]}...")

if __name__ == "__main__":
    cli()
