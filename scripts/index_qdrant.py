from pathlib import Path 
import os 
import time 

import numpy as np 
import pandas as pd 
from qdrant_client import QdrantClient 
from qdrant_client.models import Distance, PointStruct, VectorParams 

PROJECT_ROOT = Path(__file__).resolve().parents[1] 

qdrant_url = os.getenv("QDRANT_URL", "http://qdrant:6333") 
collection_name = os.getenv(
    "QDRANT_COLLECTION_NAME", 
    "abo_products_4500", 
)

embeddings = np.load(
    PROJECT_ROOT / "data/embeddings/abo_image_embeddings_4500.npy" 
)

metadata = pd.read_csv(
    PROJECT_ROOT / "data/embeddings/abo_image_metadata_4500.csv"
)

if len(embeddings) != len(metadata): 
    raise ValueError("Embeddings and metadata must have equal length.")

client = None 

for attempt in range(30): 
    try: 
        client = QdrantClient(url=qdrant_url) 
        client.get_collections() 
        break 
    except Exception: 
        if attempt == 29: 
            raise 
        print("Waiting for Qdrant...") 
        time.sleep(2) 

if client.collection_exists(collection_name):
    client.delete_collection(collection_name)

client.create_collection(
    collection_name=collection_name, 
    vectors_config=VectorParams(
        size=embeddings.shape[1], 
        distance=Distance.COSINE
    ),
)

points = [
    PointStruct(
        id=index,
        vector=embedding.tolist(), 
        payload={
            "item_id": row["item_id"],
            "image_id": row["image_id"], 
            "product_type": row["product_type"], 
            "title": row["title"], 
            "image_path": row["image_path"], 
        }, 
    )
    for index, (embedding, (_, row)) in enumerate(
        zip(embeddings, metadata.iterrows())
    )
]

client.upload_points(
    collection_name=collection_name, 
    points=points, 
)

print(f"Indexed {len(points)} points into {collection_name}")