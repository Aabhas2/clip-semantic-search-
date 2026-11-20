# Imports 
import time 
import numpy as np 
from fastapi import FastAPI, File, HTTPException, UploadFile
from pydantic import BaseModel, Field 
from pathlib import Path

from copy import deepcopy 

from fastapi.middleware.cors import CORSMiddleware 
from fastapi.staticfiles import StaticFiles

from src.config import (
    API_PUBLIC_URL, 
    IMAGE_ROOT, 
    QDRANT_COLLECTION_NAME, 
    QDRANT_STORAGE_PATH, 
    QDRANT_URL, 
)

from io import BytesIO 
from PIL import Image, UnidentifiedImageError

from src.embedder import Embedder 
from src.vector_store import VectorStore 

embedder = Embedder() 

vector_store = VectorStore(
    storage_path=str(QDRANT_STORAGE_PATH) if not QDRANT_URL else None, 
    qdrant_url=QDRANT_URL or None, 
    collection_name=QDRANT_COLLECTION_NAME, 
    vector_size=512, 
)


app = FastAPI(
    title="CLIP Semantic Search API", 
    version="0.1.0", 
)

app.add_middleware(
    CORSMiddleware, 
    allow_origins=["*"], 
    allow_credentials=False, 
    allow_methods=["*"], 
    allow_headers=["*"], 
)

app.mount(
    "/images", 
    StaticFiles(directory=str(IMAGE_ROOT)), 
    name="images", 
)

class TextEmbeddingRequest(BaseModel): 
    text: str = Field(min_length=1) 

class SearchRequest(BaseModel): 
    query: str = Field(min_length=1)
    limit: int = Field(default=5, ge=1, le=50) 

class SearchResponse(BaseModel): 
    query: str 
    results: list[dict]

# Health endpoint 
@app.get("/health") 
def health() -> dict[str, str]: 
    return {"status": "ok"}

def add_image_url(result: dict) -> dict: 
    stored_path = Path(result["image_path"]) 

    marker = Path("data/ABO/abo-images-small/images/small") 

    try: 
        relative_path = stored_path.relative_to(marker) 
    except ValueError as error: 
        raise HTTPException(
            status_code=500, 
            detail="Search result contains an unexpected image path.", 
        ) from error 

    updated_result = deepcopy(result)  
    updated_result["image_url"] = (
        f"{API_PUBLIC_URL.rstrip('/')}/images/{relative_path.as_posix()}" 
    )

    return updated_result

# Search endpoint 
@app.post("/search", response_model=SearchResponse) 
def search(request: SearchRequest) -> SearchResponse: 
    total_start = time.perf_counter() 

    embedding_start = time.perf_counter() 
    query_embedding = embedder.embed_text(request.query) 
    embedding_time = time.perf_counter() - embedding_start

    search_start = time.perf_counter() 
    results = vector_store.search(
        query_embedding=query_embedding, 
        limit=request.limit, 
    )
    search_time = time.perf_counter() - search_start 

    total_time = time.perf_counter() - total_start 

    print(
        f"embedding={embedding_time:.4f}s, "
        f"qdrant={search_time:.4f}s, "
        f"total={total_time:.4f}s"
    )

    return SearchResponse(
        query=request.query, 
        results=[add_image_url(result) for result in results], 
    )

# /embed/text endpoint 
@app.post("/embed/text") 
def embed_text(request: TextEmbeddingRequest) -> dict: 
    embedding = embedder.embed_text(request.text) 

    return {
        "text": request.text, 
        "dimension": int(embedding.shape[0]), 
        "norm": float(np.linalg.norm(embedding)), 
        "embedding": embedding.tolist(), 
    }

# /embed/image endpoint 
@app.post("/embed/image") 
def embed_image(file: UploadFile = File(...)) -> dict: 
    try: 
        image_bytes = file.file.read() # read bytes of an image 
        image = Image.open(BytesIO(image_bytes)).convert("RGB")  # BytesIO(...) - lets Pillow treat those bytes like a file & Image.open(...) decodes the iamge
    except (OSError, UnidentifiedImageError) as error: 
        raise HTTPException(
            status_code=400, 
            detail="The uploaded file is not a valid image."
        ) from error 

    embedding = embedder.embed_image(image)  # returns a normalized vector of shape (512,)

    return {
        "filename": file.filename, 
        "dimension": int(embedding.shape[0]), 
        "norm": float(np.linalg.norm(embedding)), 
        "embedding": embedding.tolist(), 
    }