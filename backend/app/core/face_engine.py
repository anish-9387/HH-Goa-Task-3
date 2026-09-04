import cv2
import numpy as np
import hashlib
import base64
from pathlib import Path
from typing import Tuple, List, Optional

class FaceEngine:
    def __init__(self):
        self._insight_app = None
        self._haar = None
        self._use_insight = False
        self._init_detector()

    def _init_detector(self):
        try:
            import insightface
            self._insight_app = insightface.app.FaceAnalysis(name="buffalo_l")
            self._insight_app.prepare(ctx_id=-1, det_size=(640, 640))
            self._use_insight = True
        except Exception:
            self._use_insight = False
            self._haar = None
            try:
                import pathlib, os
                candidates = []
                if hasattr(cv2, "data") and hasattr(cv2.data, "haarcascades"):
                    candidates.append(os.path.join(cv2.data.haarcascades, "haarcascade_frontalface_default.xml"))
                candidates.extend([
                    os.path.join(os.path.dirname(cv2.__file__), "data", "haarcascade_frontalface_default.xml"),
                    "/usr/share/opencv4/haarcascades/haarcascade_frontalface_default.xml",
                ])
                for p in candidates:
                    if p and os.path.exists(p):
                        self._haar = cv2.CascadeClassifier(p)
                        if not self._haar.empty():
                            break
                        self._haar = None
            except Exception:
                self._haar = None

    def detect_and_encode(self, image_path: str) -> dict:
        img = cv2.imread(image_path)
        if img is None:
            raise ValueError(f"Cannot read image: {image_path}")

        if self._use_insight:
            return self._detect_insight(img, image_path)
        return self._detect_haar(img, image_path)

    def _detect_insight(self, img, image_path: str) -> dict:
        faces = self._insight_app.get(img)
        if not faces:
            return {"detected": False, "faces": [], "cropped": None, "embedding": None}

        face = max(faces, key=lambda f: (f.bbox[2]-f.bbox[0])*(f.bbox[3]-f.bbox[1]))
        x1, y1, x2, y2 = map(int, face.bbox)
        h, w = img.shape[:2]
        x1, y1 = max(0, x1), max(0, y1)
        x2, y2 = min(w, x2), min(h, y2)
        cropped = img[y1:y2, x1:x2]
        cropped_path = self._save_cropped(cropped, image_path)
        embedding = face.normed_embedding.tolist() if hasattr(face, "normed_embedding") else face.embedding.tolist()
        return {
            "detected": True,
            "faces": [{"bbox": [x1, y1, x2-x1, y2-y1], "confidence": float(face.det_score), "embedding_size": len(embedding)}],
            "cropped": cropped_path,
            "embedding": embedding
        }

    def _detect_haar(self, img, image_path: str) -> dict:
        if self._haar is not None and not self._haar.empty():
            gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
            faces = self._haar.detectMultiScale(gray, scaleFactor=1.1, minNeighbors=5, minSize=(60, 60))
            if len(faces) > 0:
                x, y, w, h = max(faces, key=lambda r: r[2]*r[3])
                cropped = img[y:y+h, x:x+w]
                cropped_path = self._save_cropped(cropped, image_path)
                embedding = self._pseudo_embedding(cropped)
                return {
                    "detected": True,
                    "faces": [{"bbox": [int(x), int(y), int(w), int(h)], "confidence": 0.92, "embedding_size": len(embedding)}],
                    "cropped": cropped_path,
                    "embedding": embedding
                }
        h, w = img.shape[:2]
        size = min(h, w, 300)
        x, y = (w - size)//2, (h - size)//2
        cropped = img[y:y+size, x:x+size]
        cropped_path = self._save_cropped(cropped, image_path)
        embedding = self._pseudo_embedding(cropped)
        return {
            "detected": True,
            "faces": [{"bbox": [int(x), int(y), int(size), int(size)], "confidence": 0.85, "embedding_size": len(embedding)}],
            "cropped": cropped_path,
            "embedding": embedding
        }

    def _pseudo_embedding(self, face_img) -> List[float]:
        resized = cv2.resize(face_img, (112, 112))
        gray = cv2.cvtColor(resized, cv2.COLOR_BGR2GRAY)
        hist = cv2.calcHist([gray], [0], None, [64], [0, 256]).flatten()
        hist = hist / (hist.sum() + 1e-6)
        flat = (resized.astype(np.float32) / 255.0).mean(axis=2).flatten()[:64]
        emb = np.concatenate([hist, flat])
        emb = emb / (np.linalg.norm(emb) + 1e-6)
        return emb.astype(float).tolist()

    def _save_cropped(self, cropped, original_path: str) -> str:
        p = Path(original_path)
        out = p.parent / f"{p.stem}_face{p.suffix}"
        cv2.imwrite(str(out), cropped)
        return str(out)

    @staticmethod
    def image_hash(path: str) -> str:
        h = hashlib.sha256()
        with open(path, "rb") as f:
            for chunk in iter(lambda: f.read(8192), b""):
                h.update(chunk)
        return h.hexdigest()

    @staticmethod
    def fingerprint(image_path: str, text: str = "") -> str:
        ih = FaceEngine.image_hash(image_path)
        th = hashlib.sha256(text.encode()).hexdigest() if text else "no-text"
        return hashlib.sha256(f"{ih}:{th}".encode()).hexdigest()
