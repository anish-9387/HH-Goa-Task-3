import shutil
import uuid
from pathlib import Path
from fastapi import APIRouter, UploadFile, File, HTTPException
from app.config import UPLOAD_DIR
from app.core.pipeline import Pipeline

router = APIRouter()
pipeline = Pipeline()

def _save_upload(file: UploadFile) -> str:
    ext = Path(file.filename).suffix or ".jpg"
    name = f"{uuid.uuid4().hex}{ext}"
    dest = UPLOAD_DIR / name
    with open(dest, "wb") as out:
        shutil.copyfileobj(file.file, out)
    return str(dest)

@router.post("/pipeline/run")
async def run_pipeline(file: UploadFile = File(...)):
    if not file.content_type.startswith("image/"):
        raise HTTPException(400, "Upload an image file")
    path = _save_upload(file)
    try:
        result = pipeline.run(path)
        return result
    except ValueError as e:
        raise HTTPException(422, str(e))
    except Exception as e:
        raise HTTPException(500, str(e))

@router.post("/face/detect")
async def detect_face(file: UploadFile = File(...)):
    path = _save_upload(file)
    try:
        raw = pipeline.face.detect_and_encode(path)
        return {
            "detected": raw["detected"],
            "faces": raw["faces"],
            "cropped_face_path": raw["cropped"],
            "embedding_size": len(raw["embedding"]) if raw["embedding"] else 0,
            "message": f"Detected {len(raw['faces'])} face(s)" if raw["detected"] else "No face detected"
        }
    except Exception as e:
        raise HTTPException(500, str(e))

@router.post("/search/reverse")
async def reverse_search(file: UploadFile = File(...)):
    path = _save_upload(file)
    try:
        face = pipeline.face.detect_and_encode(path)
        q = face["cropped"] or path
        res = pipeline.search.reverse_search(q)
        return {"query_image": q, **res}
    except Exception as e:
        raise HTTPException(500, str(e))

@router.get("/blockchain/chain")
async def get_chain():
    return pipeline.get_chain()

@router.get("/blockchain/verify/{fingerprint}")
async def verify(fingerprint: str):
    return pipeline.verify_fingerprint(fingerprint)

@router.post("/blockchain/add")
async def add_block(payload: dict):
    required = ["post_url", "post_title", "source"]
    for k in required:
        if k not in payload:
            raise HTTPException(400, f"Missing {k}")
    import hashlib
    from app.core.face_engine import FaceEngine
    img_hash = payload.get("image_hash", hashlib.sha256(payload["post_url"].encode()).hexdigest())
    txt_hash = hashlib.sha256(payload["post_title"].encode()).hexdigest()
    fp = hashlib.sha256(f"{img_hash}:{txt_hash}".encode()).hexdigest()
    block = pipeline.chain.add_post(payload["post_url"], payload["post_title"], img_hash, txt_hash, fp, payload["source"])
    return block
