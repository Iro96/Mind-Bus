---
name: mindbus-expert
description: "Expert agent for Mind-Bus AI Agent project development. Use when: building agent features, implementing memory systems, adding RAG/retrieval capabilities, creating API endpoints, developing frontend components, debugging issues, or understanding architecture"
keywords: ["mindbus", "agent", "memory", "rag", "retrieval", "api", "frontend", "deployment", "architecture", "langgraph", "fastapi", "vue3"]
---

# Mind-Bus Expert Agent

Expert knowledge and skills for developing the Mind-Bus persistent AI agent platform.

## About Mind-Bus

**Mind-Bus** is a production-ready persistent AI agent platform featuring:
- Long-term and short-term memory systems (episodic, semantic, correction)
- Hybrid RAG + CAG knowledge retrieval using Qdrant vector database
- Adaptive Context Compression (ACC) for extended conversations
- LangGraph-based agent orchestration with modular nodes
- FastAPI backend with PostgreSQL, Redis, and Qdrant
- Vue 3 TypeScript frontend with Pinia state management
- Self-correcting learning from user feedback
- Enterprise-ready deployment infrastructure

## Core Architecture

### Backend Stack
- **Framework**: FastAPI (Python 3.10+)
- **Agent Orchestration**: LangGraph
- **Database**: PostgreSQL (primary storage)
- **Vector DB**: Qdrant (semantic search)
- **Cache**: Redis (caching, queuing)
- **Task Queue**: RQ (async processing)
- **LLM Integration**: Multi-model support

### Frontend Stack
- **Framework**: Vue 3 with TypeScript
- **State Management**: Pinia
- **Build**: Vite
- **Styling**: SCSS with Tailwind colors
- **HTTP Client**: Axios with interceptors

## Module Overview

### Agent System (`agent/`)
- **graph.py** - LangGraph orchestration and control flow
- **langgraph_compat.py** - Compatibility layer for graph execution
- **nodes/** - Processing nodes (responder, planner, retriever, etc)
- **state/state.py** - Conversation state management
- **retrieval/** - RAG/CAG retrieval implementation
- **policies/** - Agent behavior policies
- **prompts/** - System and node-specific prompts
- **checkpointer.py** - State persistence

### Memory System (`memory/`)
- **long_term.py** - LongTermMemoryManager for all memory types
- **short_term.py** - ShortTermMemory for working context
- **extraction.py** - Extract memories from conversations
- **schemas.py** - Memory data models (Episodic, Semantic, Correction)
- **scoring.py** - Memory importance and relevance scoring
- **storage/postgres.py** - PostgreSQL backend
- **correction.py** - Correction memory handling

### Retrieval System (`agent/retrieval/`)
- **qdrant_client.py** - Vector database interface
- **hybrid_search.py** - Combined RAG + CAG strategy
- **chunking.py** - Document segmentation strategies
- **rerank.py** - Result relevance ranking

### API (`apps/api/`)
- **main.py** - FastAPI initialization
- **routes/** - Endpoint definitions (auth, chat, memory, documents, feedback)
- **services/** - Business logic layer
- **schemas/** - Pydantic request/response models
- **middleware/** - Request logging, observability, auth
- **security.py** - JWT token handling

### Frontend (`frontend/`)
- **src/views/** - Page components (Login, Chat, Memory, Documents, Tools)
- **src/components/** - Reusable Vue components
- **src/stores/** - Pinia stores (auth, chat, memory)
- **src/services/** - API client services
- **src/router/** - Route configuration with guards

### Infrastructure
- **Docker** - Containerization
- **docker-compose.yml** - Multi-service orchestration
- **deploy/** - Deployment configurations
- **migrations/** - Database schema versioning

## Common Development Workflows

### Adding an Agent Node

1. **Create node file** in `agent/nodes/`:
   ```python
   async def my_node(state: AgentState) -> Dict[str, Any]:
       # Process state
       return {"field": new_value}
   ```

2. **Register in graph** in `agent/graph.py`:
   ```python
   from agent.nodes.my_node import my_node
   graph.add_node("my_node", my_node)
   graph.add_edge("previous", "my_node")
   ```

3. **Add tests** in `tests/agent/`:
   ```python
   @pytest.mark.asyncio
   async def test_my_node():
       state = AgentState(...)
       result = await my_node(state)
       assert result["field"] == expected
   ```

### Adding API Endpoint

1. **Create schema** in `apps/api/schemas/`:
   ```python
   class MyRequest(BaseModel):
       param: str
   ```

2. **Create route** in `apps/api/routes/`:
   ```python
   @router.post("/my-endpoint")
   async def my_endpoint(req: MyRequest, current_user: User = Depends(get_current_user)):
       result = await service.process(req.param)
       return {"result": result}
   ```

3. **Test with curl/Postman**

### Adding Frontend Component

1. **Create view** in `frontend/src/views/`:
   ```vue
   <template>
     <div class="my-view">
       <!-- content -->
     </div>
   </template>
   
   <script setup lang="ts">
   import { useStore } from '@/stores/myStore'
   const store = useStore()
   </script>
   ```

2. **Add route** in `frontend/src/router/`:
   ```typescript
   { path: '/my-route', component: MyView, meta: { requiresAuth: true } }
   ```

3. **Add navigation link** in layout

### Extracting and Storing Memory

```python
from memory.extraction import MemoryExtractor
from memory.long_term import LongTermMemoryManager

# Extract from conversation
extractor = MemoryExtractor(llm_client)
memories = await extractor.extract_episodic(message, user_id, thread_id)

# Store in database and vector DB
memory_manager = LongTermMemoryManager(db, vector_db)
await memory_manager.store_episodic(user_id, memories.content, memories.context)
```

### Implementing RAG Retrieval

```python
from agent.retrieval.hybrid_search import HybridSearch

searcher = HybridSearch(qdrant_client, memory_manager)

# Retrieve relevant context
results = await searcher.search(
    query=user_message,
    user_id=user_id,
    semantic_weight=0.6,  # RAG weight
    cached_weight=0.4,     # CAG weight
    limit=5
)
```

## Key Patterns

### 1. Async State Management
```python
# Messages always accumulated (immutable pattern)
new_messages = state.messages + [new_message]

# Return partial state updates
return {"messages": new_messages, "field": value}
```

### 2. Error Handling
```python
try:
    result = await operation()
except Exception as e:
    logger.error(f"Failed: {e}")
    return {
        "response": f"Error: {e}",
        "messages": state.messages + [{"role": "system", "content": str(e)}]
    }
```

### 3. API Response Format
```python
@router.get("/endpoint")
async def endpoint():
    return {
        "success": True,
        "data": {...},
        "message": "Success"
    }
```

### 4. Frontend State Store
```typescript
export const useMyStore = defineStore('my', () => {
  const data = ref<Data[]>([])
  const isLoading = ref(false)
  
  const fetchData = async () => {
    isLoading.value = true
    try {
      data.value = await api.get('/endpoint')
    } finally {
      isLoading.value = false
    }
  }
  
  return { data, isLoading, fetchData }
})
```

## Testing Strategy

### Backend (pytest)
```bash
# Run all tests
pytest tests/

# Run with coverage
pytest --cov=.

# Run specific test
pytest tests/agent/test_my_node.py
```

### Frontend (Vitest + Cypress)
```bash
# Unit tests
npm run test

# E2E tests
npm run test:e2e
```

## Debugging Tips

1. **Check Logs**:
   ```bash
   docker-compose logs -f api
   docker-compose logs -f worker
   ```

2. **Database Access**:
   ```bash
   docker-compose exec postgres psql -U postgres -d mindbus
   ```

3. **Redis CLI**:
   ```bash
   docker-compose exec redis redis-cli
   ```

4. **Vector DB Admin**:
   Visit http://localhost:6333/swagger (Qdrant)

5. **Frontend DevTools**:
   - Vue DevTools extension
   - Network tab for API calls
   - Console for JS errors

## Performance Considerations

### Backend
- Cache frequent queries in Redis
- Use vector DB indexing for semantic search
- Batch memory operations
- Async processing for long tasks via RQ

### Frontend
- Lazy load routes
- Code splitting by view
- Cache API responses
- Optimize images and assets

## Security

- JWT tokens with expiration
- RBAC role-based access control
- Input validation via Pydantic
- SQL injection prevention via ORM
- XSS prevention via Vue templating
- CORS properly configured
- Secrets via environment variables

## Deployment

### Local Development
```bash
docker-compose up --build
```

### Production
- Build Docker images
- Push to registry
- Deploy with Kubernetes or similar
- Configure environment variables
- Enable HTTPS/TLS
- Set up monitoring

## References

- **Repo**: https://github.com/Iro96/Mind-Bus
- **FastAPI**: https://fastapi.tiangolo.com
- **Vue 3**: https://vuejs.org
- **LangGraph**: https://langgraph.js.org
- **Qdrant**: https://qdrant.tech
- **PostgreSQL**: https://postgresql.org

## Next Steps

When working on Mind-Bus:
1. Understand the current state and message history
2. Use appropriate module patterns (nodes for agents, routes for APIs, components for UI)
3. Write tests alongside code
4. Follow async/await patterns throughout
5. Document complex logic with comments
6. Test integration with real components
7. Consider memory and performance impacts