import argparse
import json
from pathlib import Path
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from .api.routes import router
from .config import BASE_DIR

app = FastAPI(title="HH Goa - Face Identification & Blockchain Verification", version="1.0.0")

app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_credentials=True, allow_methods=["*"], allow_headers=["*"])
app.include_router(router, prefix="/api")

frontend_dist = BASE_DIR / "frontend" / "dist"
frontend_dir = BASE_DIR / "frontend"
serve_dir = frontend_dist if frontend_dist.exists() else frontend_dir

if (serve_dir / "assets").exists():
    app.mount("/assets", StaticFiles(directory=str(serve_dir / "assets")), name="assets")
if serve_dir.exists():
    app.mount("/static", StaticFiles(directory=str(serve_dir)), name="static")

@app.get("/")
async def serve_frontend():
    for p in [frontend_dist / "index.html", frontend_dir / "index.html"]:
        if p.exists():
            return FileResponse(str(p))
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

    from .core.pipeline import Pipeline
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
