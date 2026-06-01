---
name: rag-retrieval
description: "Use when: implementing RAG (Retrieval Augmented Generation), CAG (Cached Augmented Generation), hybrid search, document chunking, semantic search, or retrieval optimization"
keywords: ["rag", "cag", "retrieval", "semantic search", "chunking", "embedding", "reranking", "context augmentation", "hybrid search"]
---

# RAG/Retrieval Skills

Patterns for implementing RAG and CAG retrieval systems in Mind-Bus.

## RAG vs CAG Overview

### RAG (Retrieval Augmented Generation)
Vector similarity search for semantic relevance.

```python
# Vector similarity search
results = await vector_db.search(
    query_vector=embedding,
    limit=5,
    score_threshold=0.7
)
```

**Use when**: Deep knowledge retrieval, semantic matching, one-off queries

### CAG (Cached Augmented Generation)
Fast retrieval from cached results.

```python
# Cache-based retrieval
cached = await redis_cache.get(query_hash)
if cached:
    return cached  # Fast
```

**Use when**: Frequent similar queries, performance-critical

### Hybrid Approach
Combine both for optimal results.

```python
# Weighted combination
results = combine(
    rag_results=vector_search(query),
    cag_results=cache_lookup(query),
    rag_weight=0.6,
    cag_weight=0.4
)
```

## Quick Start: Hybrid Search

### 1. Chunk Documents
```python
from agent.retrieval.chunking import DocumentChunker

chunker = DocumentChunker(
    chunk_size=512,
    overlap=128,
    strategy="semantic"
)

chunks = await chunker.chunk_document(
    content=document_text,
    metadata={"source": "file.pdf", "type": "knowledge"}
)
```

### 2. Embed and Store
```python
from agent.retrieval.qdrant_client import QdrantVectorClient

qdrant = QdrantVectorClient(host="localhost", port=6333)

for chunk in chunks:
    embedding = await embedding_model.embed(chunk.text)
    
    await qdrant.upsert(
        collection="documents",
        point_id=chunk.id,
        vector=embedding,
        metadata=chunk.metadata
    )
```

### 3. Search with RAG
```python
from agent.retrieval.hybrid_search import HybridSearch

searcher = HybridSearch(qdrant_client, redis_cache, memory_manager)

results = await searcher.search(
    query=user_query,
    user_id=user_id,
    semantic_weight=0.6,  # RAG weight
    cached_weight=0.4,     # CAG weight
    limit=5,
    rerank=True
)
```

## Implementation Patterns

### Document Chunking Strategy
```python
class DocumentChunker:
    """Chunk documents for vector storage."""
    
    def __init__(self, chunk_size=512, overlap=128):
        self.chunk_size = chunk_size
        self.overlap = overlap
    
    async def chunk_document(self, content: str, metadata: Dict):
        """Split document into semantic chunks."""
        
        # Use semantic boundaries (paragraphs, sentences)
        sentences = content.split('. ')
        
        chunks = []
        current_chunk = ""
        
        for sentence in sentences:
            if len(current_chunk) + len(sentence) > self.chunk_size:
                chunks.append({
                    "text": current_chunk,
                    "metadata": metadata,
                    "id": f"{metadata['source']}_{len(chunks)}"
                })
                
                # Overlap: keep last part
                current_chunk = sentence[:self.overlap] + sentence
            else:
                current_chunk += sentence + ". "
        
        if current_chunk:
            chunks.append({
                "text": current_chunk,
                "metadata": metadata,
                "id": f"{metadata['source']}_{len(chunks)}"
            })
        
        return chunks
```

### Semantic Search (RAG)
```python
async def semantic_search(
    query: str,
    user_id: UUID,
    qdrant_client,
    embedding_model,
    limit: int = 5
) -> List[Dict]:
    """Retrieve semantically similar documents."""
    
    # Embed query
    query_embedding = await embedding_model.embed(query)
    
    # Search vector database
    results = await qdrant_client.search(
        collection_name="documents",
        query_vector=query_embedding,
        limit=limit,
        score_threshold=0.7
    )
    
    # Convert to document format
    documents = []
    for result in results:
        documents.append({
            "id": result.id,
            "content": result.payload["text"],
            "score": result.score,
            "metadata": result.payload.get("metadata", {})
        })
    
    return documents
```

### Cache-based Retrieval (CAG)
```python
import hashlib

async def cached_search(
    query: str,
    user_id: UUID,
    redis_client,
    ttl: int = 3600
) -> Optional[List[Dict]]:
    """Retrieve from cache if available."""
    
    # Generate cache key
    cache_key = f"search:{user_id}:{hashlib.md5(query.encode()).hexdigest()}"
    
    # Try cache
    cached = await redis_client.get(cache_key)
    if cached:
        return json.loads(cached)
    
    return None

async def cache_results(
    query: str,
    user_id: UUID,
    results: List[Dict],
    redis_client,
    ttl: int = 3600
):
    """Store search results in cache."""
    
    cache_key = f"search:{user_id}:{hashlib.md5(query.encode()).hexdigest()}"
    
    await redis_client.setex(
        cache_key,
        ttl,
        json.dumps(results)
    )
```

### Hybrid Search Implementation
```python
class HybridSearch:
    """Combine RAG and CAG for optimal retrieval."""
    
    def __init__(self, qdrant, redis, embedding_model):
        self.qdrant = qdrant
        self.redis = redis
        self.embedding = embedding_model
    
    async def search(
        self,
        query: str,
        user_id: UUID,
        rag_weight: float = 0.6,
        cag_weight: float = 0.4,
        limit: int = 5
    ) -> List[Dict]:
        """Hybrid search with RAG and CAG."""
        
        # Try cache first (CAG)
        cached = await self.redis.get(
            f"search:{user_id}:{query}"
        )
        if cached:
            cag_results = json.loads(cached)
        else:
            cag_results = []
        
        # Semantic search (RAG)
        query_embedding = await self.embedding.embed(query)
        rag_results = await self.qdrant.search(
            collection="documents",
            query_vector=query_embedding,
            limit=limit
        )
        
        # Combine and rank
        combined = self._combine_results(
            rag_results=rag_results,
            cag_results=cag_results,
            rag_weight=rag_weight,
            cag_weight=cag_weight,
            limit=limit
        )
        
        # Cache for future queries
        await self.redis.setex(
            f"search:{user_id}:{query}",
            3600,
            json.dumps(combined)
        )
        
        return combined
    
    def _combine_results(self, rag_results, cag_results, 
                        rag_weight, cag_weight, limit):
        """Combine RAG and CAG results with weighting."""
        
        # Score RAG results
        rag_scored = [
            {**r, "combined_score": r["score"] * rag_weight}
            for r in rag_results
        ]
        
        # Score CAG results
        cag_scored = [
            {**r, "combined_score": r.get("score", 0.5) * cag_weight}
            for r in cag_results
        ]
        
        # Merge and deduplicate
        all_results = {}
        for r in rag_scored + cag_scored:
            if r["id"] in all_results:
                all_results[r["id"]]["combined_score"] += r["combined_score"]
            else:
                all_results[r["id"]] = r
        
        # Sort by combined score
        sorted_results = sorted(
            all_results.values(),
            key=lambda x: x["combined_score"],
            reverse=True
        )
        
        return sorted_results[:limit]
```

### Result Reranking
```python
class ResultReranker:
    """Rerank results by relevance."""
    
    def __init__(self, llm_client):
        self.llm = llm_client
    
    async def rerank(
        self,
        query: str,
        results: List[Dict],
        limit: int = 5
    ) -> List[Dict]:
        """Use LLM to rerank results."""
        
        # Create ranking prompt
        ranking_prompt = f"""
        Query: {query}
        
        Documents:
        {json.dumps([r['content'][:200] for r in results], indent=2)}
        
        Rank by relevance. Return JSON array of indices.
        """
        
        # Get LLM ranking
        ranking = await self.llm.generate(ranking_prompt)
        
        # Parse and reorder
        try:
            indices = json.loads(ranking)
            reranked = [results[i] for i in indices[:limit] if i < len(results)]
            return reranked
        except:
            return results[:limit]
```

## Vector Database Operations

### Create Collection
```python
from qdrant_client.http import models

async def create_collection(qdrant_client):
    """Create vector collection."""
    
    await qdrant_client.recreate_collection(
        collection_name="documents",
        vectors_config=models.VectorParams(
            size=384,  # Embedding dimension
            distance=models.Distance.COSINE
        )
    )
```

### Add Documents
```python
async def add_documents(
    qdrant_client,
    documents: List[Dict]
):
    """Add documents to vector DB."""
    
    points = [
        models.PointStruct(
            id=hash(doc["id"]),
            vector=doc["embedding"],
            payload={
                "text": doc["content"],
                "source": doc["source"]
            }
        )
        for doc in documents
    ]
    
    await qdrant_client.upsert(
        collection_name="documents",
        points=points
    )
```

## Testing Patterns

```python
import pytest

@pytest.mark.asyncio
async def test_semantic_search():
    """Test RAG retrieval."""
    results = await semantic_search(
        query="Python agent",
        user_id=user_id,
        qdrant_client=mock_qdrant,
        embedding_model=mock_embedding
    )
    
    assert len(results) > 0
    assert all(r["score"] > 0.7 for r in results)

@pytest.mark.asyncio
async def test_hybrid_search():
    """Test hybrid RAG+CAG search."""
    searcher = HybridSearch(mock_qdrant, mock_redis, mock_embedding)
    
    results = await searcher.search(
        query="test query",
        user_id=user_id,
        limit=5
    )
    
    assert len(results) <= 5
```

## Performance Tips

1. **Pre-embedding**: Embed documents at upload time
2. **Batch Indexing**: Index documents in batches
3. **Caching**: Cache frequent queries in Redis
4. **Chunking**: Balance chunk size for performance/quality
5. **Indexing Strategy**: Use Qdrant's built-in indexing

## References

- **RAG Guide**: `agent/retrieval/`
- **Qdrant**: https://qdrant.tech
- **Embedding Models**: OpenAI, Hugging Face
- **Chunking**: `agent/retrieval/chunking.py`
- **Hybrid Search**: `agent/retrieval/hybrid_search.py`
