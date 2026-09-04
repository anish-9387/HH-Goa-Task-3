import json
import hashlib
import time
from pathlib import Path
from datetime import datetime, timezone
from typing import Optional, List

from app.config import CHAIN_FILE, BLOCKCHAIN_DIFFICULTY

class BlockchainEngine:
    def __init__(self, chain_file: Path = CHAIN_FILE, difficulty: int = BLOCKCHAIN_DIFFICULTY):
        self.chain_file = Path(chain_file)
        self.difficulty = difficulty
        self.chain: List[dict] = []
        self._load_or_create()

    def _load_or_create(self):
        if self.chain_file.exists():
            try:
                data = json.loads(self.chain_file.read_text())
                self.chain = data if isinstance(data, list) else []
                if self.chain and self.is_valid():
                    return
            except Exception:
                pass
        genesis = self._create_genesis()
        self.chain = [genesis]
        self._persist()

    def _create_genesis(self) -> dict:
        data = {
            "post_url": "genesis",
            "post_title": "Genesis Block",
            "image_hash": "0"*64,
            "text_hash": "0"*64,
            "fingerprint": "0"*64,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "source": "genesis"
        }
        data_hash = self._hash_data(data)
        block = {
            "index": 0,
            "timestamp": data["timestamp"],
            "data": data,
            "data_hash": data_hash,
            "previous_hash": "0"*64,
            "nonce": 0,
            "hash": ""
        }
        block["hash"] = self._mine(block)
        return block

    @staticmethod
    def _hash_data(data: dict) -> str:
        return hashlib.sha256(json.dumps(data, sort_keys=True).encode()).hexdigest()

    def _hash_block(self, block: dict) -> str:
        content = f"{block['index']}{block['timestamp']}{block['data_hash']}{block['previous_hash']}{block['nonce']}"
        return hashlib.sha256(content.encode()).hexdigest()

    def _mine(self, block: dict) -> str:
        prefix = "0" * self.difficulty
        nonce = 0
        while True:
            block["nonce"] = nonce
            h = self._hash_block(block)
            if h.startswith(prefix):
                return h
            nonce += 1

    def _persist(self):
        self.chain_file.parent.mkdir(parents=True, exist_ok=True)
        self.chain_file.write_text(json.dumps(self.chain, indent=2))

    def add_post(self, post_url: str, post_title: str, image_hash: str, text_hash: str, fingerprint: str, source: str) -> dict:
        data = {
            "post_url": post_url,
            "post_title": post_title,
            "image_hash": image_hash,
            "text_hash": text_hash,
            "fingerprint": fingerprint,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "source": source
        }
        data_hash = self._hash_data(data)
        prev = self.chain[-1]
        block = {
            "index": len(self.chain),
            "timestamp": data["timestamp"],
            "data": data,
            "data_hash": data_hash,
            "previous_hash": prev["hash"],
            "nonce": 0,
            "hash": ""
        }
        block["hash"] = self._mine(block)
        self.chain.append(block)
        self._persist()
        return block

    def verify(self, fingerprint: Optional[str] = None, data_hash: Optional[str] = None, block_hash: Optional[str] = None) -> dict:
        target = fingerprint or data_hash or block_hash
        if not target:
            return {"verified": False, "block": None, "message": "No hash provided"}
        for b in self.chain:
            if b["data"]["fingerprint"] == target or b["data_hash"] == target or b["hash"] == target:
                if not self.is_valid():
                    return {"verified": False, "block": b, "message": "Chain tampered - invalid integrity"}
                recomputed = self._hash_data(b["data"])
                if recomputed != b["data_hash"]:
                    return {"verified": False, "block": b, "message": "Data hash mismatch - tampered"}
                if self._hash_block(b) != b["hash"]:
                    return {"verified": False, "block": b, "message": "Block hash mismatch"}
                return {"verified": True, "block": b, "message": "Verified on-chain - tamper-evident record intact"}
        return {"verified": False, "block": None, "message": "Not found on chain"}

    def is_valid(self) -> bool:
        prefix = "0" * self.difficulty
        for i, b in enumerate(self.chain):
            if self._hash_block(b) != b["hash"]:
                return False
            if not b["hash"].startswith(prefix):
                return False
            if i > 0 and b["previous_hash"] != self.chain[i-1]["hash"]:
                return False
            if self._hash_data(b["data"]) != b["data_hash"]:
                return False
        return True

    def get_chain(self) -> List[dict]:
        return self.chain

    def get_by_hash(self, h: str) -> Optional[dict]:
        for b in self.chain:
            if b["hash"] == h or b["data_hash"] == h or b["data"]["fingerprint"] == h:
                return b
        return None
