import os
from qdrant_client import QdrantClient
from qdrant_client.models import Distance, VectorParams

class QdrantClientManager:
    def __init__(self):
        self.url = os.getenv("QDRANT_URL", "http://localhost:6333")
        self.api_key = os.getenv("QDRANT_API_KEY")
        self._client = None

    @property
    def client(self):
        if self._client is None:
            try:
                self._client = QdrantClient(url=self.url, api_key=self.api_key)
            except Exception as e:
                print(f"Warning: Could not connect to Qdrant: {e}")
                self._client = None
        return self._client

    def create_collection(self, collection_name: str, vector_size: int, distance: Distance = Distance.COSINE):
        """Create a Qdrant collection if it doesn't exist."""
        client = self.client
        if client and not client.collection_exists(collection_name):
            client.create_collection(
                collection_name=collection_name,
                vectors_config=VectorParams(size=vector_size, distance=distance),
            )

    def get_client(self):
        return self.client

# Global instance
qdrant_client = QdrantClientManager()