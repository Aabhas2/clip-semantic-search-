import numpy as np 
import pandas as pd 
from qdrant_client import QdrantClient
from qdrant_client.models import VectorParams, Distance 

class VectorStore: 
    def __init__(self, storage_path: str, collection_name: str, vector_size: int):
        self.storage_path = storage_path 
        self.collection_name = collection_name 
        self.vector_size = vector_size
        self.client = QdrantClient(path=storage_path) 

    def create_collection(self) -> None: 
        self.client.create_collection(
            collection_name=self.collection_name, 
            vectors_config=VectorParams(
                size=self.vector_size, 
                distance=Distance.COSINE, 
            ), 
        )

    def count(self) -> int: 
        count_results = self.client.count(
            collection_name=self.collection_name, 
            exact=True, 
        )
        return count_results.count

    def index_embeddings(self, embeddings: np.ndarray, metadata: pd.DataFrame) -> None: 
        if len(embeddings) != len(metadata): 
            raise ValueError("Embeddings and metadata must contain the same number of rows.")

        if embeddings.ndim != 2 or embeddings.shape[1] != self.vector_size:
            raise ValueError(
                f"Expected embeddings with shape (n, {self.vector_size}), "
                f"received {embeddings.shape}"
            )
        ids = list(range(len(metadata)))

        payloads = [
            {
                "item_id": row["item_id"], 
                "image_id": row["image_id"], 
                "product_type": row["product_type"], 
                "title": row["title"], 
                "image_path": row["image_path"], 
            }
            for _, row in metadata.iterrows()
        ]

        self.client.upload_collection(
            collection_name=self.collection_name, 
            vectors=embeddings.tolist(), 
            payload=payloads,
            ids=ids, 
        )

    def search(self, query_embedding: np.ndarray, limit: int = 5) -> list[dict]: 
        if query_embedding.ndim != 1: 
            raise ValueError("Query embedding must be one-dimensional.") 

        if query_embedding.shape[0] != self.vector_size: 
            raise ValueError(
                f"Expected query vector size {self.vector_size}, " 
                f"received {query_embedding.shape[0]}"
            )

        if limit < 1: 
            raise ValueError("limit must be at least 1.")
        
        search_result = self.client.query_points(
            collection_name=self.collection_name, 
            query=query_embedding.tolist(), 
            limit=limit, 
            with_payload=True, 
        )
        return search_result.points

    def close(self) -> None: 
        self.client.close() 