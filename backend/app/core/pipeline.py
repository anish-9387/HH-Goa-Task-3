import time
import hashlib
from pathlib import Path

from .face_engine import FaceEngine
from .search_engine import SearchEngine
from .blockchain_engine import BlockchainEngine

class Pipeline:
    def __init__(self):
        self.face = FaceEngine()
        self.search = SearchEngine()
        self.chain = BlockchainEngine()

    def run(self, image_path: str) -> dict:
        total_start = time.time()

        face_raw = self.face.detect_and_encode(image_path)
        if not face_raw["detected"]:
            raise ValueError("No face detected in input image")

        face_result = {
            "detected": True,
            "faces": face_raw["faces"],
            "cropped_face_path": face_raw["cropped"],
            "embedding": face_raw["embedding"],
            "message": f"Detected {len(face_raw['faces'])} face(s)"
        }

        # Search with original image first — gives Google full context to identify the person.
        # Face crop alone often matches accessories (glasses, jewelry) rather than the person.
        search_input = image_path
        search_raw = self.search.reverse_search(search_input)

        # If no results from original, try the face crop
        if not search_raw["results"] and face_raw["cropped"] and face_raw["cropped"] != image_path:
            search_input = face_raw["cropped"]
            search_raw = self.search.reverse_search(search_input)

        if not search_raw["results"]:
            raise RuntimeError("No matching posts found")

        search_result = {
            "query_image": search_input,
            "results": search_raw["results"],
            "engine": search_raw["engine"],
            "latency_ms": search_raw["latency_ms"]
        }

        top = search_raw["results"][0]
        image_hash = self.face.image_hash(search_input)
        text_hash = hashlib.sha256(top["title"].encode()).hexdigest()
        fingerprint = self.face.fingerprint(search_input, top["title"] + top["url"])

        block = self.chain.add_post(
            post_url=top["url"],
            post_title=top["title"],
            image_hash=image_hash,
            text_hash=text_hash,
            fingerprint=fingerprint,
            source=top["source"]
        )

        verify = self.chain.verify(fingerprint=fingerprint)

        total_latency = int((time.time() - total_start) * 1000)
        return {
            "face": face_result,
            "search": search_result,
            "blockchain": block,
            "verify": verify,
            "total_latency_ms": total_latency
        }

    def verify_fingerprint(self, fingerprint: str) -> dict:
        return self.chain.verify(fingerprint=fingerprint)

    def get_chain(self) -> dict:
        chain = self.chain.get_chain()
        return {"length": len(chain), "chain": chain, "is_valid": self.chain.is_valid()}
