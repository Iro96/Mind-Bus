from typing import List, Dict, Any, Tuple
import uuid
from agent.retrieval.qdrant_client import qdrant_client
from qdrant_client.models import Filter, SearchRequest, Fusion

class HybridSearcher:
    def __init__(self, collection_name: str = "documents"):
        self.collection_name = collection_name
        self.qdrant = qdrant_client.get_client()

    def hybrid_search(self, query: str, limit: int = 10, filter: Filter = None) -> List[Dict[str, Any]]:
        """Perform hybrid search using dense and sparse vectors."""
        # Mock dense embedding
        dense_embedding = self._mock_dense_embedding(query)

        # Mock sparse embedding (BM25-like)
        sparse_embedding = self._mock_sparse_embedding(query)

        # Perform hybrid search
        search_results = self.qdrant.search_batch(
            collection_name=self.collection_name,
            requests=[
                SearchRequest(
                    vector=dense_embedding,
                    filter=filter,
                    limit=limit,
                    with_payload=True,
                    with_vectors=False
                ),
                SearchRequest(
                    vector=sparse_embedding,
                    filter=filter,
                    limit=limit,
                    with_payload=True,
                    with_vectors=False
                )
            ]
        )

        # Merge results using Reciprocal Rank Fusion (simple implementation)
        merged_results = self._reciprocal_rank_fusion(search_results, limit)

        return merged_results

    def _mock_dense_embedding(self, text: str) -> List[float]:
        """Mock dense embedding."""
        import hashlib
        hash_obj = hashlib.md5(text.encode())
        hash_bytes = hash_obj.digest()
        embedding = [float(b) / 255.0 for b in hash_bytes] * 48  # 16*48=768
        return embedding

    def _mock_sparse_embedding(self, text: str) -> Dict[int, float]:
        """Mock sparse embedding (BM25-like)."""
        # Simple term frequency
        words = text.lower().split()
        vocab = {word: i for i, word in enumerate(set(words))}
        sparse = {}
        for word in words:
            idx = vocab[word]
            sparse[idx] = sparse.get(idx, 0) + 1.0
        return sparse

    def _reciprocal_rank_fusion(self, search_results: List[List], k: int = 60) -> List[Dict[str, Any]]:
        """Simple Reciprocal Rank Fusion."""
        scores = {}
        payloads = {}

        for result_list in search_results:
            for rank, result in enumerate(result_list):
                doc_id = result.id
                score = 1.0 / (k + rank + 1)
                scores[doc_id] = scores.get(doc_id, 0) + score
                if doc_id not in payloads:
                    payloads[doc_id] = result.payload

        # Sort by fused score
        sorted_docs = sorted(scores.items(), key=lambda x: x[1], reverse=True)[:k]

        results = []
        for doc_id, score in sorted_docs:
            result = payloads[doc_id]
            result["score"] = score
            results.append(result)

        return results

# Global instance
searcher = HybridSearcher()