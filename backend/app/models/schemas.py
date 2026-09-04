from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime

class FaceDetection(BaseModel):
    bbox: List[int]
    confidence: float
    embedding_size: int

class FaceResult(BaseModel):
    detected: bool
    faces: List[FaceDetection]
    cropped_face_path: Optional[str] = None
    embedding: Optional[List[float]] = None
    message: str

class SearchResult(BaseModel):
    title: str
    url: str
    thumbnail: Optional[str] = None
    source: str
    snippet: Optional[str] = None
    is_social: bool = False

class SearchResponse(BaseModel):
    query_image: str
    results: List[SearchResult]
    engine: str
    latency_ms: int

class BlockData(BaseModel):
    post_url: str
    post_title: str
    image_hash: str
    text_hash: str
    fingerprint: str
    timestamp: str
    source: str

class Block(BaseModel):
    index: int
    timestamp: str
    data: BlockData
    data_hash: str
    previous_hash: str
    nonce: int
    hash: str

class ChainResponse(BaseModel):
    length: int
    chain: List[Block]
    is_valid: bool

class VerifyResponse(BaseModel):
    verified: bool
    block: Optional[Block] = None
    message: str

class PipelineResponse(BaseModel):
    face: FaceResult
    search: SearchResponse
    blockchain: Block
    verify: VerifyResponse
    total_latency_ms: int
