from typing import List, Dict, Any, Optional
import uuid
from agent.retrieval.qdrant_client import qdrant_client
from agent.retrieval.chunking import chunker
from storage.postgres import db
from qdrant_client.models import PointStruct

class DocumentIngester:
    def __init__(self, collection_name: str = "documents"):
        self.collection_name = collection_name
        self.qdrant = qdrant_client.get_client()
        # Assume vector size for now - create collection lazily
        # qdrant_client.create_collection(collection_name, vector_size=768)  # Placeholder size

    def ingest_document(self, document_id: str, text: str, metadata: Dict[str, Any] = None) -> List[str]:
        """Ingest a document: chunk, embed, store in DB and Qdrant."""
        if metadata is None:
            metadata = {}

        # Ensure collection exists
        qdrant_client.create_collection(self.collection_name, vector_size=768)

        # Chunk the text
        chunks = chunker.chunk_text(text, metadata)

        chunk_ids = []
        points = []

        for i, chunk in enumerate(chunks):
            chunk_id = str(uuid.uuid4())
            chunk_ids.append(chunk_id)

            # Mock embedding - replace with real embedding later
            embedding = self._mock_embedding(chunk["text"])

            # Store chunk in DB
            self._store_chunk_in_db(document_id, i, chunk, chunk_id)

            # Prepare point for Qdrant
            point = PointStruct(
                id=chunk_id,
                vector=embedding,
                payload={
                    "document_id": document_id,
                    "chunk_index": i,
                    "text": chunk["text"],
                    "metadata": chunk["metadata"]
                }
            )
            points.append(point)

        # Upsert to Qdrant
        if points:
            self.qdrant.upsert(collection_name=self.collection_name, points=points)

        return chunk_ids

    def _mock_embedding(self, text: str) -> List[float]:
        """Mock embedding function - replace with real embedding model."""
        # Simple hash-based mock embedding
        import hashlib
        hash_obj = hashlib.md5(text.encode())
        hash_bytes = hash_obj.digest()
        # Convert to list of floats (placeholder 768-dim)
        embedding = [float(b) / 255.0 for b in hash_bytes] * 32  # 16*32=512, wait adjust
        # Actually, make it 768
        embedding = (embedding * 3)[:768]  # Repeat and truncate
        return embedding

    def _store_chunk_in_db(self, document_id: str, chunk_index: int, chunk: Dict[str, Any], chunk_id: str):
        """Store chunk metadata in PostgreSQL."""
        query = """
        INSERT INTO document_chunks (id, document_id, chunk_index, text, token_count, metadata)
        VALUES (%s, %s, %s, %s, %s, %s)
        """
        params = (
            chunk_id,
            document_id,
            chunk_index,
            chunk["text"],
            chunk["token_count"],
            chunk["metadata"]
        )
        db.execute(query, params)

# Global instance
ingester = DocumentIngester()