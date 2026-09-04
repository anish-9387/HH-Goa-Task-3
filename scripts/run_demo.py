import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "backend"))
from app.core.pipeline import Pipeline

img = Path(__file__).resolve().parents[1] / "data" / "uploads" / "test_face.jpg"
if not img.exists():
    print(f"Place a face image at {img} or pass path as arg")
    sys.exit(1)
import sys as _sys
if len(_sys.argv) > 1:
    img = _sys.argv[1]

p = Pipeline()
res = p.run(str(img))
import json
print(json.dumps(res, indent=2))
