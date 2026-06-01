---
name: "Mind-Bus Skills Hub"
description: "Central guide to all Mind-Bus development skills. Reference for agent orchestration, memory systems, retrieval, backend API, and frontend development."
---

# Mind-Bus Skills Hub

Complete guide to reusable skills for the Mind-Bus persistent AI agent platform.

## 📚 Available Skills

### 1. **mindbus-expert** (Master Skill)
**When to use**: General Mind-Bus development, architecture questions, feature planning

**Covers**:
- Project architecture overview
- Stack and technologies
- Module structure and roles
- Common development workflows
- Debugging and deployment tips

**Key Topics**:
- Backend: FastAPI, LangGraph, PostgreSQL, Qdrant, Redis
- Frontend: Vue 3, TypeScript, Pinia
- Infrastructure: Docker, deployment strategies
- Security and performance

---

### 2. **agent-orchestration**
**When to use**: Building LangGraph nodes, designing agent flows, managing state, routing logic

**Covers**:
- Node implementation patterns (retriever, planner, responder, tool runner, reflector)
- Graph design patterns (sequential, conditional, loops)
- State management and message history
- Error handling in async nodes
- Testing patterns for nodes

**Key Code Locations**:
- `agent/graph.py` - Graph orchestration
- `agent/nodes/` - Node implementations
- `agent/state/state.py` - AgentState definition
- `agent/langgraph_compat.py` - LangGraph compatibility

**Example Use Cases**:
- ✅ Add a new processing node
- ✅ Implement tool execution flow
- ✅ Create conditional routing between nodes
- ✅ Add reflection/feedback loop

---

### 3. **memory-system**
**When to use**: Working with episodic/semantic/correction memory, extracting memories, retrieval

**Covers**:
- Three memory types (episodic, semantic, correction)
- Memory extraction pipeline from conversations
- Storage in PostgreSQL and vector DB
- Short-term working memory patterns
- Semantic search and scoring
- Context building from memories

**Key Code Locations**:
- `memory/long_term.py` - LongTermMemoryManager
- `memory/short_term.py` - ShortTermMemory
- `memory/extraction.py` - Memory extraction
- `memory/schemas.py` - Memory models
- `memory/scoring.py` - Memory importance scoring
- `storage/postgres.py` - DB backend

**Example Use Cases**:
- ✅ Extract memories from user messages
- ✅ Store episodic/semantic/correction memories
- ✅ Retrieve relevant memories for context
- ✅ Implement memory scoring and filtering
- ✅ Build context from multiple memory types

---

### 4. **rag-retrieval**
**When to use**: Implementing RAG/CAG retrieval, semantic search, chunking, reranking

**Covers**:
- RAG (semantic vector search) vs CAG (cached retrieval)
- Hybrid search combining both approaches
- Document chunking strategies
- Vector database operations (Qdrant)
- Semantic search implementation
- Cache-based retrieval (Redis)
- Result reranking

**Key Code Locations**:
- `agent/retrieval/hybrid_search.py` - Hybrid search
- `agent/retrieval/qdrant_client.py` - Vector DB client
- `agent/retrieval/chunking.py` - Document segmentation
- `agent/retrieval/rerank.py` - Result ranking

**Example Use Cases**:
- ✅ Chunk documents for vector storage
- ✅ Implement semantic search
- ✅ Create cache-based retrieval
- ✅ Combine RAG + CAG for optimal results
- ✅ Rerank results by relevance
- ✅ Manage Qdrant collections

---

### 5. **backend-api**
**When to use**: Adding FastAPI routes, creating schemas, implementing services, authentication

**Covers**:
- Route and endpoint creation
- Pydantic schema definition
- Service layer patterns
- Dependency injection
- Error handling and validation
- Authentication and authorization (JWT)
- Pagination and filtering
- Middleware and logging
- Background tasks
- Testing patterns

**Key Code Locations**:
- `apps/api/main.py` - FastAPI app
- `apps/api/routes/` - Endpoint definitions
- `apps/api/services/` - Business logic
- `apps/api/schemas/` - Pydantic models
- `apps/api/security.py` - JWT handling
- `apps/api/middleware/` - Custom middleware

**Example Use Cases**:
- ✅ Create new API endpoint
- ✅ Add authentication to endpoint
- ✅ Implement pagination
- ✅ Add error handling
- ✅ Create service for business logic
- ✅ Queue background tasks
- ✅ Add request/response logging

---

### 6. **frontend-components**
**When to use**: Building Vue 3 components, Pinia stores, routes, forms, API integration

**Covers**:
- Vue 3 component structure (Composition API)
- Pinia store patterns and state management
- Router and navigation guards
- Form handling and validation
- API service integration with interceptors
- Component props, emits, and composition
- SCSS styling with Tailwind colors
- Testing patterns with Vitest
- Performance optimization

**Key Code Locations**:
- `frontend/src/views/` - Page components
- `frontend/src/components/` - Reusable components
- `frontend/src/stores/` - Pinia stores
- `frontend/src/services/api.ts` - API integration
- `frontend/src/router/index.ts` - Route config
- `frontend/src/style.scss` - Global styles

**Example Use Cases**:
- ✅ Create new Vue component
- ✅ Add Pinia store for state management
- ✅ Implement form with validation
- ✅ Add new route and navigation
- ✅ Integrate API calls with Pinia
- ✅ Create reusable component library
- ✅ Style with SCSS and Tailwind

---

## 🔄 Development Workflows

### Add a Chat Feature

**Skill Order**: `agent-orchestration` → `memory-system` → `rag-retrieval` → `backend-api` → `frontend-components`

1. Design agent flow in **agent-orchestration**
2. Extract and store memories in **memory-system**
3. Implement RAG retrieval in **rag-retrieval**
4. Create `/chat` endpoint in **backend-api**
5. Build ChatView component in **frontend-components**

### Implement Memory Management

**Skill Order**: `memory-system` → `backend-api` → `frontend-components`

1. Define memory types in **memory-system**
2. Create memory endpoints in **backend-api**
3. Build memory UI in **frontend-components**

### Add a Tool Integration

**Skill Order**: `agent-orchestration` → `backend-api`

1. Create tool node in **agent-orchestration**
2. Add tool endpoint in **backend-api**
3. Integrate with agent graph

### Build API Feature

**Skill Order**: `backend-api` → `frontend-components`

1. Create endpoint in **backend-api**
2. Add store and component in **frontend-components**

---

## 🎯 Quick Reference

| Task | Primary Skill | Secondary Skills |
|------|---------------|------------------|
| Add agent node | agent-orchestration | - |
| Implement memory extraction | memory-system | agent-orchestration |
| Build semantic search | rag-retrieval | memory-system |
| Create API endpoint | backend-api | agent-orchestration |
| Build UI component | frontend-components | backend-api |
| Full feature (end-to-end) | all | - |

---

## 📂 Project Structure

```
Mind-Bus/
├── agent/                      # LangGraph orchestration
│   ├── graph.py               # Main graph (see: agent-orchestration)
│   ├── nodes/                 # Processing nodes
│   ├── state/                 # State definition
│   ├── retrieval/             # RAG/CAG (see: rag-retrieval)
│   └── policies/              # Agent behaviors
├── memory/                     # Memory system (see: memory-system)
│   ├── long_term.py
│   ├── short_term.py
│   ├── extraction.py
│   └── schemas.py
├── apps/api/                  # FastAPI (see: backend-api)
│   ├── main.py
│   ├── routes/
│   ├── services/
│   ├── schemas/
│   └── security.py
├── frontend/                  # Vue 3 (see: frontend-components)
│   ├── src/
│   │   ├── views/
│   │   ├── components/
│   │   ├── stores/
│   │   ├── services/
│   │   └── router/
│   └── vite.config.ts
├── storage/                   # Database backends
├── observability/             # Logging and monitoring
├── deploy/                    # Deployment configs
└── docker-compose.yml         # Local development
```

---

## 🛠️ Common Patterns

### State Management
- Use immutable patterns (accumulate state changes)
- Return only changed fields from nodes/endpoints
- Always preserve message history

### Error Handling
- Async try/catch in all operations
- Log errors with context
- Return user-friendly error messages
- Include error details in response

### Testing
- Unit tests for individual components
- Integration tests for workflows
- Mock external dependencies
- Test both success and error paths

### Performance
- Batch operations where possible
- Use caching (Redis for frequent queries, short-term memory)
- Async/await throughout (no blocking)
- Connection pooling for databases

---

## 🔗 Stack Technologies

### Backend
- **FastAPI** - Web framework
- **LangGraph** - Agent orchestration
- **PostgreSQL** - Relational database
- **Qdrant** - Vector database
- **Redis** - Caching and queuing
- **RQ** - Task queue
- **Pydantic** - Data validation

### Frontend
- **Vue 3** - UI framework
- **TypeScript** - Type safety
- **Pinia** - State management
- **Vite** - Build tool
- **Axios** - HTTP client
- **Vue Router** - Routing

### Infrastructure
- **Docker** - Containerization
- **PostgreSQL** - Main database
- **Qdrant** - Vector DB
- **Redis** - Cache/queue

---

## 📖 Documentation

- **FastAPI**: https://fastapi.tiangolo.com
- **Vue 3**: https://vuejs.org
- **LangGraph**: https://langgraph.js.org
- **Pinia**: https://pinia.vuejs.org
- **Qdrant**: https://qdrant.tech
- **PostgreSQL**: https://postgresql.org

---

## 🚀 Getting Started

1. **New to Mind-Bus?** Start with `mindbus-expert` for overview
2. **Working on agent logic?** Use `agent-orchestration` + `memory-system`
3. **Building features?** Use `backend-api` + `frontend-components`
4. **Optimizing retrieval?** Use `rag-retrieval`

---

## 💡 Best Practices

✅ **Do**:
- Use Pydantic for all API schemas
- Always validate input
- Write tests alongside code
- Use async/await consistently
- Document complex logic
- Preserve message history
- Filter by user_id in queries

❌ **Don't**:
- Use blocking operations in async code
- Skip input validation
- Store every message as memory
- Ignore confidence scores
- Log sensitive data
- Query all data without filtering

---

## 🤝 Contributing Skills

When adding new skills:

1. Create skill directory in `.agents/skills/<skill-name>/`
2. Create `SKILL.md` with YAML frontmatter and content
3. Include:
   - Clear description and keywords
   - Quick start examples
   - Implementation patterns
   - Testing patterns
   - Common mistakes
   - References to code locations
   - Performance tips

---

## 📞 Support

For questions about:
- **Architecture**: See `mindbus-expert`
- **Specific modules**: See relevant skill
- **Code patterns**: Check `SKILL.md` examples
- **Testing**: Check testing patterns in each skill
