import os
from pathlib import Path
from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent.parent.parent
BACKEND_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"
UPLOAD_DIR = DATA_DIR / "uploads"
CHAIN_FILE = DATA_DIR / "chain.json"

# Load backend/.env then root .env if present
load_dotenv(BACKEND_DIR / ".env")
load_dotenv(BASE_DIR / ".env")
load_dotenv()

UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
DATA_DIR.mkdir(parents=True, exist_ok=True)

SERPAPI_KEY = os.getenv("SERPAPI_API_KEY", "")
WEB3_RPC_URL = os.getenv("WEB3_RPC_URL", "")
WEB3_PRIVATE_KEY = os.getenv("WEB3_PRIVATE_KEY", "")
BING_API_KEY = os.getenv("BING_API_KEY", "")

FACE_CONF_THRESHOLD = 0.5
BLOCKCHAIN_DIFFICULTY = 3
MAX_SEARCH_RESULTS = 5
