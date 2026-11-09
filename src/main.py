# Imports 
import time 
import numpy as np 
from fastapi import FastAPI, File, HTTPException, UploadFile
from pydantic import BaseModel, Field 
from pathlib import Path

from io import BytesIO 
from PIL import Image, UnidentifiedImageError

from src.embedder import Embedder 
from src.vector_store import VectorStore 

PROJECT_ROOT = Path(__file__).resolve().parents[1] 

embedder = Embedder() 

vector_store = VectorStore(
    storage_path=str(PROJECT_ROOT / "qdrant_storage") , 
    collection_name="abo_products", 
    vector_size=512, 
)

app = FastAPI(
    title="CLIP Semantic Search API", 
    version="0.1.0", 
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
        results=results, 
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