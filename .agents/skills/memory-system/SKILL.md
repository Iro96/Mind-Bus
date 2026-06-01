---
name: memory-system
description: "Use when: implementing episodic/semantic/correction memory, extracting memories from conversations, managing memory storage, retrieving memories for context, or designing memory architecture"
keywords: ["memory", "episodic", "semantic", "correction", "extraction", "retrieval", "long-term", "short-term", "embedding", "vector db"]
---

# Memory System Skills

Patterns for implementing and extending the three-tier memory architecture.

## Memory Types Overview

### 1. Episodic Memory
Specific events and conversations tied to timestamps.

```python
{
    "id": "ep-123",
    "type": "episodic",
    "user_id": "user-abc",
    "content": "User asked about project architecture",
    "timestamp": "2024-01-15T10:30:00Z",
    "context": {
        "thread_id": "thread-xyz",
        "topic": "architecture",
        "confidence": 0.95
    }
}
```

### 2. Semantic Memory
General knowledge and patterns learned over time.

```python
{
    "id": "sem-456",
    "type": "semantic",
    "user_id": "user-abc",
    "content": "User prefers RAG over CAG",
    "learned_from": ["ep-123", "ep-124"],
    "confidence": 0.87,
    "category": "user_preference"
}
```

### 3. Correction Memory
System errors and learned corrections.

```python
{
    "id": "corr-789",
    "type": "correction",
    "original_response": "Incorrect fact",
    "correction": "Correct fact",
    "source": "user_feedback",
    "learned_at": "2024-01-15T11:00:00Z"
}
```

## Quick Start: Memory Workflow

### 1. Extract Memory from Conversation
```python
from memory.extraction import MemoryExtractor

extractor = MemoryExtractor(llm_client)

episodic = await extractor.extract_episodic(
    user_message="I prefer Python",
    user_id=user_id,
    thread_id=thread_id,
    conversation_turn=turn
)

semantic = await extractor.extract_semantic(
    conversation_history=messages,
    user_id=user_id
)
```

### 2. Store Memory
```python
from memory.long_term import LongTermMemoryManager

memory_manager = LongTermMemoryManager(db, vector_db)

await memory_manager.store_episodic(
    user_id=user_id,
    content=episodic.content,
    context=episodic.context
)

await memory_manager.store_semantic(
    user_id=user_id,
    content=semantic.content,
    category=semantic.category,
    confidence=semantic.confidence
)
```

### 3. Retrieve Memory
```python
# Semantic search
memories = await memory_manager.retrieve(
    query="Python preferences",
    user_id=user_id,
    memory_type="semantic",
    limit=5,
    similarity_threshold=0.75
)

# Recent episodic
recent = await memory_manager.get_recent(
    user_id=user_id,
    memory_type="episodic",
    days=7
)
```

## Implementation Patterns

### Memory Extraction Pipeline
```python
class MemoryExtractionPipeline:
    """Full extraction workflow."""
    
    async def process_message(self, message: str, context: Dict):
        """Extract all memory types from a message."""
        
        results = await asyncio.gather(
            self.extractor.extract_episodic(message, context),
            self.extractor.extract_semantic(message, context),
            self.extractor.extract_corrections(message, context)
        )
        
        episodic, semantic, corrections = results
        
        # Store only high-confidence memories
        stored = []
        if episodic.confidence > 0.7:
            stored.append(await self.store(episodic))
        if semantic.confidence > 0.7:
            stored.append(await self.store(semantic))
        
        return stored
```

### Short-term Working Memory
```python
from memory.short_term import ShortTermMemory

working_memory = ShortTermMemory(max_size=50)

# Add to working memory (current conversation)
await working_memory.add(
    content=message,
    user_id=user_id,
    ttl_seconds=3600
)

# Retrieve recent (faster than semantic search)
recent_context = await working_memory.get_recent(
    user_id=user_id,
    limit=20
)
```

### Vector Database Integration (Qdrant)
```python
from qdrant_client.http import models

async def store_in_vector_db(memory: Memory, embedding: List[float]):
    """Store memory vector and metadata."""
    
    await qdrant_client.upsert(
        collection_name="memories",
        points=[
            models.PointStruct(
                id=hash(memory.id),
                vector=embedding,
                payload={
                    "memory_id": str(memory.id),
                    "user_id": str(memory.user_id),
                    "type": memory.type,
                    "content": memory.content,
                    "confidence": memory.confidence
                }
            )
        ]
    )

async def semantic_search(query: str, user_id: UUID):
    """Search memories by similarity."""
    
    query_embedding = await embedding_model.embed(query)
    
    results = await qdrant_client.search(
        collection_name="memories",
        query_vector=query_embedding,
        query_filter=models.Filter(
            must=[models.HasIdCondition(has_id=[str(user_id)])]
        ),
        limit=10,
        score_threshold=0.7
    )
    
    return [Memory.from_payload(r.payload) for r in results]
```

### Memory Scoring and Ranking
```python
from memory.scoring import MemoryScorer

scorer = MemoryScorer()

# Score memory importance
score = await scorer.score_memory(
    memory=memory_obj,
    recency_weight=0.3,
    relevance_weight=0.5,
    frequency_weight=0.2
)

# Filter important memories
important = [m for m in memories if score(m) > 0.7]
```

### Context Building from Memory
```python
async def retrieve_context(user_id: UUID, query: str) -> str:
    """Retrieve context from all memory types."""
    
    episodic, semantic, short_term = await asyncio.gather(
        memory_manager.retrieve_episodic(query, user_id, limit=3),
        memory_manager.retrieve_semantic(query, user_id, limit=5),
        short_term_memory.get_recent(user_id, limit=10)
    )
    
    context_parts = []
    
    if short_term:
        context_parts.append("Recent context:")
        context_parts.extend([m["content"] for m in short_term])
    
    if episodic:
        context_parts.append("\nRecent events:")
        context_parts.extend([m["content"] for m in episodic])
    
    if semantic:
        context_parts.append("\nRelevant knowledge:")
        context_parts.extend([m["content"] for m in semantic])
    
    return "\n".join(context_parts)
```

## Testing Patterns

```python
import pytest

@pytest.mark.asyncio
async def test_store_episodic_memory():
    """Test memory storage."""
    memory_manager = LongTermMemoryManager(mock_db, mock_vector_db)
    
    await memory_manager.store_episodic(
        user_id=user_id,
        content="Test content",
        context={"source": "test"}
    )
    
    stored = await memory_manager.get_by_id(memory_id)
    assert stored.type == "episodic"

@pytest.mark.asyncio
async def test_semantic_search():
    """Test memory retrieval."""
    memories = await memory_manager.retrieve(
        query="Python",
        user_id=user_id,
        limit=5
    )
    
    assert len(memories) > 0
    assert all(m.type == "semantic" for m in memories)
```

## Common Mistakes

1. **Not Filtering by User**: Always include `user_id` in queries
   ```python
   # ✅ CORRECT
   memories = await db.query(Memory).filter(user_id=user_id)
   ```

2. **Over-storing**: Extract only meaningful information
   ```python
   # ✅ Use confidence threshold
   if extracted.confidence > 0.7:
       await memory_manager.store(extracted)
   ```

3. **Ignoring Confidence Scores**: Always validate quality
   ```python
   # ✅ Filter by confidence
   memories = [m for m in all_memories if m.confidence > 0.7]
   ```

## Performance Tips

1. **Batch Operations**: Store multiple memories together
   ```python
   await memory_manager.store_batch([mem1, mem2, mem3])
   ```

2. **Cache Hot Data**: Use short-term memory for current conversation
3. **Lazy Indexing**: Let vector DB handle indexing
4. **Connection Pooling**: Reuse DB connections

## References

- **Memory Module**: `memory/`
- **Extraction**: `memory/extraction.py`
- **Long-term Manager**: `memory/long_term.py`
- **Schemas**: `memory/schemas.py`
- **Short-term**: `memory/short_term.py`
- **Qdrant Docs**: https://qdrant.tech
