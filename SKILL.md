# SKILL.md - Mind-Bus Development Skills & Knowledge

This document captures skills, knowledge, and best practices learned while developing the Mind-Bus AI Agent Platform.

## Project Overview

**Mind-Bus** is a persistent AI agent platform with:
- Long-term and short-term memory systems
- Hybrid RAG + CAG knowledge retrieval
- Adaptive Context Compression (ACC)
- Self-learning capabilities
- Production-ready architecture

## Stack Overview

### Backend
- **Framework**: FastAPI (Python 3.10+)
- **LLM Orchestration**: LangGraph
- **Memory**: PostgreSQL + Qdrant (vector DB)
- **Caching**: Redis
- **Task Queue**: RQ (Redis Queue)
- **Authentication**: JWT (PyJWT)

### Frontend
- **Framework**: Vue 3 with TypeScript
- **Build Tool**: Vite
- **State Management**: Pinia
- **Routing**: Vue Router
- **HTTP Client**: Axios
- **Styling**: SCSS
- **Date Utilities**: date-fns

### Infrastructure
- **Containerization**: Docker + Docker Compose
- **Database**: PostgreSQL
- **Cache**: Redis
- **Vector DB**: Qdrant
- **Deployment**: Supports local, cloud, and enterprise deployments

## Backend Architecture

### API Structure (FastAPI)
```
apps/api/
├── main.py              # FastAPI app initialization
├── routes/              # API endpoints
│   ├── auth.py         # Authentication
│   ├── chat.py         # Chat endpoints
│   ├── memory.py       # Memory management
│   ├── documents.py    # Document management
│   ├── feedback.py     # Feedback system
│   ├── admin.py        # Admin endpoints
│   └── tools.py        # Tool management
├── services/           # Business logic
│   ├── conversation_service.py
│   ├── queue_service.py
│   └── feedback_service.py
├── schemas/            # Pydantic models
├── middleware/         # Custom middleware
└── security.py         # JWT handling
```

### Key Patterns

#### 1. Request Lifecycle
1. Request enters through middleware with request_id
2. Observability middleware logs and traces requests
3. Route handler executes with dependency injection
4. Response is returned with status codes
5. Observability middleware records metrics

#### 2. Authentication
- JWT tokens issued at `/auth/token`
- Tokens include user_id, username, and roles
- All protected endpoints use `get_current_user` dependency
- Token validation done via JWT with secret key

#### 3. Conversation Management
- Threads represent conversations
- Messages stored per thread with user/assistant role
- Thread creation on first message or explicit request
- Message history used for context building

#### 4. Async Processing
- Long-running tasks dispatched to RQ queue
- Queue worker processes tasks asynchronously
- Status tracking available for long operations
- Background tasks don't block HTTP responses

### Agent Architecture (agent/)

#### Core Components
1. **Graph** (langgraph_compat.py) - Agent orchestration flow
2. **State** (state/state.py) - Conversation state management
3. **Nodes** - Processing steps:
   - `responder.py` - Generate responses
   - `planner.py` - Plan actions
   - `retriever.py` - Retrieve knowledge
   - `reflector.py` - Self-reflection
   - `compressor.py` - Context compression
   - `tool_runner.py` - Execute tools

#### State Management
```python
class AgentState:
    messages: List[Dict]           # Conversation history
    thread_id: UUID               # Conversation ID
    user_id: UUID                 # User context
    memory: List[Memory]          # Retrieved memories
    context: str                  # Current context
    compressed: bool              # ACC applied
```

### Memory System (memory/)

#### Three Types of Memory
1. **Episodic** - Specific conversation events
2. **Semantic** - General knowledge and facts
3. **Correction** - Error corrections for learning

#### Key Files
- `long_term.py` - LongTermMemoryManager
- `extraction.py` - Memory extraction from conversations
- `schemas.py` - Memory data models
- `storage/` - Backend implementation

### Retrieval System (agent/retrieval/)

#### Hybrid RAG+CAG Approach
1. **RAG (Retrieval Augmented Generation)**
   - Vector similarity search via Qdrant
   - Text semantic chunking
   - Reranking for relevance

2. **CAG (Cached Augmented Generation)**
   - Redis caching of common queries
   - Fast retrieval for frequent questions
   - Cache invalidation strategies

#### Components
- `qdrant_client.py` - Vector DB client
- `hybrid_search.py` - Combined search strategy
- `chunking.py` - Document segmentation
- `rerank.py` - Result ranking

### Observability (observability/)

#### Three Pillars
1. **Logging** - Structured JSON logs
2. **Tracing** - Request-level trace IDs
3. **Metrics** - Performance measurements

#### Implementation
- Request ID propagation through context
- Span-based tracing for operations
- Latency recording for all endpoints
- Alert thresholds and checks

## Frontend Architecture

### Component Structure
```
Frontend/
├── src/
│   ├── views/              # Page-level components
│   │   ├── LoginView.vue
│   │   ├── ChatView.vue
│   │   ├── MemoryView.vue
│   │   ├── DocumentsView.vue
│   │   └── ToolsView.vue
│   ├── components/         # Reusable components
│   ├── stores/             # Pinia state stores
│   │   ├── auth.ts
│   │   └── chat.ts
│   ├── services/           # API services
│   │   └── api.ts
│   ├── router/             # Vue Router config
│   ├── App.vue             # Root component
│   ├── main.ts             # Entry point
│   └── style.scss          # Global styles
├── index.html              # HTML entry
├── vite.config.ts          # Build config
└── tsconfig.json           # TypeScript config
```

### Key Patterns

#### 1. State Management (Pinia)
```typescript
export const useAuthStore = defineStore('auth', () => {
  const token = ref<string | null>(null)
  const user = ref<AuthUser | null>(null)
  
  const login = async (username: string, password: string) => {
    // Login logic
  }
  
  return { token, user, login }
})
```

#### 2. API Integration with Interceptors
```typescript
const api = axios.create({ baseURL: '/api' })

api.interceptors.request.use((config) => {
  if (authStore.token) {
    config.headers.Authorization = `Bearer ${authStore.token}`
  }
  return config
})

api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      authStore.logout()
      window.location.href = '/login'
    }
    return Promise.reject(error)
  }
)
```

#### 3. Route Guards
```typescript
router.beforeEach((to, from, next) => {
  const authStore = useAuthStore()
  if (to.meta.requiresAuth && !authStore.isAuthenticated) {
    next('/login')
  } else {
    next()
  }
})
```

#### 4. Dark Theme with Tailwind Colors
- Primary: Slate (#0f172a, #1e293b)
- Accent: Blue (#3b82f6)
- Secondary: Purple (#8b5cf6)
- Success: Green (#10b981)
- Error: Red (#ef4444)

### Component Best Practices

1. **Reactive Data**
   ```typescript
   const count = ref(0)
   const isLoading = ref(false)
   const items = ref<Item[]>([])
   ```

2. **Computed Properties**
   ```typescript
   const filteredItems = computed(() => {
     return items.value.filter(item => item.active)
   })
   ```

3. **Lifecycle Hooks**
   ```typescript
   onMounted(() => {
     loadData()
   })
   ```

4. **Error Handling**
   ```typescript
   try {
     await api.get('/endpoint')
   } catch (err) {
     error.value = 'Failed to load'
   }
   ```

## Development Workflows

### Adding a New Feature

1. **Backend**
   - Create route in `apps/api/routes/`
   - Add service method if needed
   - Define Pydantic schema in `schemas/`
   - Add endpoint with proper error handling
   - Test with curl or Postman

2. **Frontend**
   - Create new view component
   - Add route in `router/index.ts`
   - Create API service method
   - Add navigation link
   - Style with SCSS

### Authentication Flow

1. User enters credentials at `/login`
2. Frontend posts to `/auth/token`
3. Backend returns JWT token
4. Frontend stores token in localStorage
5. Subsequent requests include token in header
6. Backend validates token and extracts user_id
7. User can access protected routes

### Chat Flow

1. User sends message in ChatView
2. Frontend calls `/chat` endpoint
3. Backend creates thread (if new conversation)
4. Agent graph processes message
5. Memory retrieval happens (RAG)
6. LLM generates response
7. Response + memories returned to frontend
8. Frontend displays in chat interface

## Common Tasks

### Debugging

1. **Backend**
   ```bash
   # Check logs
   docker-compose logs -f api
   
   # Access Python shell
   docker-compose exec api python
   ```

2. **Frontend**
   - Use Vue DevTools extension
   - Check Network tab for API calls
   - Console for JavaScript errors

### Database Operations

1. **PostgreSQL**
   ```bash
   docker-compose exec postgres psql -U postgres -d mindbus
   \dt                    # List tables
   SELECT * FROM threads; # Query data
   ```

2. **Qdrant Vector DB**
   - Access at http://localhost:6333/swagger
   - Manage collections and vectors

3. **Redis Cache**
   ```bash
   docker-compose exec redis redis-cli
   KEYS *              # List all keys
   GET key             # Get value
   DEL key             # Delete key
   ```

### Deployment

1. **Local Development**
   ```bash
   docker-compose up --build
   ```

2. **Production**
   - Build Docker images
   - Push to registry
   - Deploy with orchestration (K8s, etc)
   - Set environment variables
   - Configure secrets

## Testing Strategy

### Backend Tests
- Unit tests for services
- Integration tests for API endpoints
- Mock external dependencies
- Use pytest framework

### Frontend Tests
- Component unit tests with Vitest
- E2E tests with Cypress
- Mock API responses
- Test user interactions

## Performance Optimization

### Backend
1. **Caching** - Redis for frequent queries
2. **Connection Pooling** - Database connections
3. **Async Processing** - Long operations in queue
4. **Compression** - Context compression in ACC
5. **Indexing** - Vector DB indexing strategies

### Frontend
1. **Code Splitting** - Route-based splitting
2. **Lazy Loading** - Components loaded on demand
3. **Image Optimization** - Compressed assets
4. **Caching** - Browser cache for static files
5. **Minification** - Production build optimization

## Security Considerations

### Authentication
- JWT tokens with expiration
- Secure storage (localStorage for now)
- HttpOnly cookies (recommended for production)

### Authorization
- Role-based access control (RBAC)
- User scoping of data
- Admin endpoints protected

### API Security
- CORS headers properly configured
- Input validation with Pydantic
- SQL injection prevention via ORM
- XSS prevention via Vue escaping
- CSRF protection for state-changing operations

### Data Protection
- Sensitive data not logged
- Encrypted connections (HTTPS in production)
- Secrets management via environment variables

## Common Errors & Solutions

### JWT Token Expired
**Problem**: 401 Unauthorized errors
**Solution**: Implement token refresh endpoint and refresh on 401

### Memory Leaks in Frontend
**Problem**: Components not cleaned up properly
**Solution**: Clean up in `onUnmounted()` hooks

### Vector DB Connection Issues
**Problem**: Qdrant connection failures
**Solution**: Check Qdrant is running, verify collection exists

### CORS Errors
**Problem**: Frontend can't reach backend
**Solution**: Check vite proxy config, CORS headers in FastAPI

## Future Enhancements

1. **Multi-Agent Support** - Multiple agents working together
2. **Advanced Memory** - More sophisticated memory structures
3. **Tool Ecosystem** - Expand available integrations
4. **Monitoring Dashboard** - Real-time performance monitoring
5. **Model Selection** - Switch between different LLMs
6. **Custom Prompts** - User-defined system prompts
7. **Analytics** - Usage tracking and insights

## Resources & References

### Documentation
- FastAPI: https://fastapi.tiangolo.com
- Vue 3: https://vuejs.org
- LangGraph: https://langgraph.js.org
- Qdrant: https://qdrant.tech

### Key Concepts
- LLM Chains and Agents
- Vector Databases and Semantic Search
- Long-term Memory in AI Systems
- Context Window Management

## Conclusion

Mind-Bus is a comprehensive AI agent platform that combines modern AI technologies with production-ready architecture. Key strengths include:
- Modular design for easy extension
- Comprehensive memory system
- Scalable deployment options
- Professional observability
- Modern frontend interface

This knowledge base should help future developers understand, maintain, and extend the platform.
