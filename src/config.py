import os 
from pathlib import Path 

PROJECT_ROOT = Path(__file__).resolve().parents[1]

QDRANT_STORAGE_PATH = Path(
    os.getenv(
        "QDRANT_STORAGE_PATH", 
        str(PROJECT_ROOT / "qdrant_storage_4500")
    )
)

QDRANT_URL = os.getenv("QDRANT_URL", "")

QDRANT_COLLECTION_NAME = os.getenv(
    "QDRANT_COLLECTION_NAME", 
    "abo_products_4500", 
)

IMAGE_ROOT = Path(
    os.getenv(
        "IMAGE_ROOT", 
        str(PROJECT_ROOT / "data/ABO/abo-images-small/images/small"), 
    )
)

API_PUBLIC_URL = os.getenv(
    "API_PUBLIC_URL", 
    "http://127.0.0.1:8000", 
)