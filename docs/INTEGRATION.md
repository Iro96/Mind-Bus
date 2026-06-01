# INTEGRATION.md - Frontend & Backend Integration Guide

This document describes how the Mind-Bus frontend and backend communicate and work together.

## Architecture Overview

```js
┌─────────────────────────────────────────────────────────────┐
│                    USER BROWSER                             │
│  ┌─────────────────────────────────────────────────────┐   │
│  │          Vue 3 + TypeScript Frontend                │   │
│  │  (Port 5173 / served from build)                    │   │
│  └──────────┬──────────────────────────────────────────┘   │
└─────────────┼──────────────────────────────────────────────┘
              │ HTTP Requests (JSON)
              │
┌─────────────▼──────────────────────────────────────────────┐
│              FASTAPI BACKEND (Port 8000)                   │
│  ┌────────────────────────────────────────────────────┐   │
│  │ API Endpoints                                       │   │
│  │ • /auth/token          - Authentication            │   │
│  │ • /chat                - Send messages              │   │
│  │ • /chat/threads        - List conversations         │   │
│  │ • /memory              - Retrieve memories          │   │
│  │ • /documents           - Upload & manage docs       │   │
│  │ • /tools               - List & control tools       │   │
│  └────────────────────────────────────────────────────┘   │
│  ┌────────────────────────────────────────────────────┐   │
│  │ Services                                            │   │
│  │ • ConversationService  - Thread management          │   │
│  │ • LongTermMemoryManager - Memory operations         │   │
│  │ • Agent Graph          - LLM orchestration          │   │
│  └────────────────────────────────────────────────────┘   │
└──────────────────────────────────────────────────────────────┘
              │
              ├─→ PostgreSQL (Port 5432)
              ├─→ Qdrant Vector DB (Port 6333)
              ├─→ Redis Cache (Port 6379)
              └─→ LLM APIs (OpenAI, etc.)
```

## Communication Flow

### 1. Authentication Flow

```js
Frontend                           Backend
   │                                 │
   ├─ POST /auth/token              │
   │  {username, password}           │
   │─────────────────────────────────>
   │                                 ├─ Validate credentials
   │                                 ├─ Create user if demo
   │                                 ├─ Generate JWT token
   │  <─ {access_token, token_type}─│
   │                                 │
   ├─ Store token in localStorage   │
   ├─ Set Authorization header      │
```

### 2. Chat Flow

```js
Frontend (ChatView)                Backend
   │                                 │
   ├─ POST /chat                    │
   │  {message, thread_id?}          │
   │─────────────────────────────────>
   │                                 ├─ Get or create thread
   │                                 ├─ Add user message
   │                                 ├─ Retrieve memories (RAG)
   │                                 ├─ Plan actions
   │                                 ├─ Execute tools
   │                                 ├─ Generate response
   │                                 ├─ Extract memories
   │                                 ├─ Store message
   │  <─ {thread, messages, ...}────│
   │                                 │
   ├─ Update message list           │
   ├─ Scroll to latest message      │
```

### 3. Memory Retrieval Flow

```js
Frontend (MemoryView)              Backend
   │                                 │
   ├─ GET /memory?memory_type=X    │
   │─────────────────────────────────>
   │                                 ├─ Validate user_id
   │                                 ├─ Query memory database
   │                                 ├─ Filter by type
   │                                 ├─ Format response
   │  <─ {memories: [...]}──────────│
   │                                 │
   ├─ Display memories              │
   ├─ Filter by type                │
```

### 4. Document Upload Flow

```js
Frontend (DocumentsView)           Backend
   │                                 │
   ├─ POST /documents/upload         │
   │  FormData(file)                 │
   │─────────────────────────────────>
   │                                 ├─ Validate file
   │                                 ├─ Store file
   │                                 ├─ Generate embeddings
   │                                 ├─ Index in Qdrant
   │  <─ {document: {...}}───────────│
   │                                 │
   ├─ Show upload progress          │
   ├─ Add to documents list         │
```

## API Endpoints

### Authentication

```js
POST /auth/token
Request:
  {
    "username": "admin",
    "password": "password"
  }
Response:
  {
    "access_token": "eyJ0eXAiOiJKV1QiLCJhbGc...",
    "token_type": "bearer"
  }
```

### Chat

```js
POST /chat
Headers: Authorization: Bearer {token}
Request:
  {
    "message": "What is the weather?",
    "thread_id": "550e8400-e29b-41d4-a716-446655440000" (optional)
  }
Response:
  {
    "message": "The weather is...",
    "thread_id": "550e8400-e29b-41d4-a716-446655440000",
    "timestamp": "2026-05-31T20:17:53Z"
  }

GET /chat/threads
Headers: Authorization: Bearer {token}
Response:
  {
    "threads": [
      {
        "id": "550e8400-e29b-41d4-a716-446655440000",
        "title": "Weather Discussion",
        "created_at": "2026-05-31T20:17:53Z",
        "updated_at": "2026-05-31T20:30:00Z"
      }
    ],
    "count": 1
  }

GET /chat/threads/{thread_id}
Headers: Authorization: Bearer {token}
Response:
  {
    "thread": {...},
    "messages": [
      {
        "id": "msg_1",
        "role": "user",
        "content": "What is the weather?",
        "created_at": "2026-05-31T20:17:53Z"
      },
      {
        "id": "msg_2",
        "role": "assistant",
        "content": "The weather is...",
        "created_at": "2026-05-31T20:18:00Z"
      }
    ]
  }
```

### Memory

```js
GET /memory?memory_type=episodic&limit=50
Headers: Authorization: Bearer {token}
Response:
  {
    "memories": [
      {
        "id": "mem_1",
        "title": "User is a developer",
        "content": "User mentioned they work as a software engineer",
        "memory_type": "semantic",
        "created_at": "2026-05-31T20:17:53Z",
        "relevance_score": 0.95
      }
    ],
    "count": 1
  }

DELETE /memory/{memory_id}
Headers: Authorization: Bearer {token}
Response:
  {
    "message": "Memory deleted"
  }
```

### Documents

```js
POST /documents/upload
Headers: 
  - Authorization: Bearer {token}
  - Content-Type: multipart/form-data
Body: file (binary)
Response:
  {
    "document": {
      "id": "doc_1",
      "filename": "resume.pdf",
      "size": 245680,
      "content_type": "application/pdf",
      "created_at": "2026-05-31T20:17:53Z"
    }
  }

GET /documents
Headers: Authorization: Bearer {token}
Response:
  {
    "documents": [
      {
        "id": "doc_1",
        "filename": "resume.pdf",
        "size": 245680,
        "created_at": "2026-05-31T20:17:53Z"
      }
    ]
  }

GET /documents/{doc_id}/download
Headers: Authorization: Bearer {token}
Response: File (binary)

DELETE /documents/{doc_id}
Headers: Authorization: Bearer {token}
Response:
  {
    "message": "Document deleted"
  }
```

### Tools

```js
GET /tools
Headers: Authorization: Bearer {token}
Response:
  {
    "tools": [
      {
        "id": "web_search",
        "name": "Web Search",
        "description": "Search the web for information",
        "category": "information",
        "enabled": true,
        "version": "1.0",
        "parameters": ["query", "max_results"]
      }
    ]
  }

PATCH /tools/{tool_id}
Headers: Authorization: Bearer {token}
Request:
  {
    "enabled": false
  }
Response:
  {
    "tool_id": "web_search",
    "enabled": false,
    "message": "Tool disabled"
  }
```

## Frontend State Management

### Auth Store (Pinia)

```typescript
const authStore = useAuthStore()

// Properties
authStore.token          // JWT token
authStore.user           // User object {username, user_id, roles}
authStore.isAuthenticated // Boolean

// Methods
await authStore.login(username, password)
authStore.logout()
```

### Chat Store (Pinia)

```typescript
const chatStore = useChatStore()

// Properties
chatStore.threads           // Array of thread objects
chatStore.currentThread     // Currently selected thread
chatStore.messages          // Messages in current thread
chatStore.loading           // Loading state
chatStore.error             // Error message

// Methods
await chatStore.fetchThreads()
await chatStore.fetchMessages(threadId)
await chatStore.sendMessage(message, threadId?)
```

## Error Handling

### HTTP Status Codes

| Code | Meaning | Frontend Handling |
| ------ | --------- | ------------------- |
| 200 | Success | Process response |
| 400 | Bad Request | Show validation errors |
| 401 | Unauthorized | Redirect to login |
| 403 | Forbidden | Show access denied |
| 404 | Not Found | Show not found message |
| 500 | Server Error | Show error alert |
| 503 | Service Unavailable | Show retry prompt |

### Error Response Format

```json
{
  "detail": "Error message"
}
```

### Frontend Error Handling

```typescript
try {
  const response = await api.get('/endpoint')
  // Handle success
} catch (error) {
  if (error.response?.status === 401) {
    authStore.logout()
    router.push('/login')
  } else if (error.response?.status === 404) {
    error.value = 'Resource not found'
  } else {
    error.value = 'An error occurred'
  }
}
```

## Authentication & Authorization

### JWT Token Structure

```js
Header: eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9

Payload:
{
  "sub": "username",
  "user_id": "550e8400-e29b-41d4-a716-446655440000",
  "roles": ["admin", "user"]
}

Signature: [cryptographic signature]
```

### Token Usage

1. Store in localStorage after login
2. Include in Authorization header: `Bearer {token}`
3. Frontend automatically includes in all requests via axios interceptor
4. Backend validates token on protected endpoints
5. If expired (401), frontend redirects to login

## Data Validation

### Frontend Validation

- Input fields validated before submission
- File type and size validation on upload
- Message content not empty check

### Backend Validation

- Pydantic models validate all inputs
- UUID format validation
- User ownership verification
- File type validation
- Request size limits

## Performance Considerations

### Frontend

1. **Lazy Loading** - Components loaded on demand
2. **Caching** - Messages cached in state
3. **Pagination** - Large lists paginated
4. **Debouncing** - Search queries debounced

### Backend

1. **Database Indexing** - User ID, thread ID indexed
2. **Vector DB Caching** - Qdrant caches embeddings
3. **Redis Caching** - Frequent responses cached
4. **Connection Pooling** - Database connections pooled
5. **Async Processing** - Long tasks queued

## Development Setup

### Run Both Services

```bash
# Terminal 1: Backend
cd <repo-root>
python -m apps.api.main

# Terminal 2: Frontend
cd frontend
npm install
npm run dev
```

### Via Docker

```bash
cd deploy
docker-compose up --build
```

Access:

- Frontend: <http://localhost:5173>
- API: <http://localhost:8000>
- API Docs: <http://localhost:8000/docs>

## Testing Integration

### Manual Testing Checklist

- [ ] Login works with demo credentials
- [ ] Can send chat message
- [ ] Thread list shows new conversation
- [ ] Can view message history
- [ ] Memory list loads
- [ ] Can upload document
- [ ] Tool list displays
- [ ] Can enable/disable tools
- [ ] Logout clears token
- [ ] Protected routes redirect to login

### API Testing

```bash
# Get token
curl -X POST http://localhost:8000/auth/token \
  -H "Content-Type: application/json" \
  -d '{"username":"admin","password":"password"}'

# Send message (use token from above)
curl -X POST http://localhost:8000/chat \
  -H "Authorization: Bearer {token}" \
  -H "Content-Type: application/json" \
  -d '{"message":"Hello!"}'
```

## Troubleshooting

### CORS Issues

**Problem**: Frontend requests blocked by CORS
**Solution**:

- Check FastAPI CORS middleware is enabled
- Verify frontend URL is in CORS origins
- Check proxy configuration in vite.config.ts

### Token Expiration

**Problem**: 401 errors after some time
**Solution**:

- Implement token refresh endpoint
- Auto-refresh tokens before expiration
- Add refresh logic to axios interceptor

### Memory Retrieval Slow

**Problem**: Memory queries take too long
**Solution**:

- Check Qdrant is running
- Verify collection exists and is indexed
- Monitor database query performance

### Document Upload Fails

**Problem**: Large files fail to upload
**Solution**:

- Check max upload size in backend
- Verify file type is allowed
- Check available disk space

## Future Enhancements

1. **Real-time Updates** - WebSocket for live messages
2. **File Preview** - In-browser document preview
3. **Streaming Responses** - Stream LLM responses
4. **Collaborative Features** - Multi-user conversations
5. **Export Functions** - Export memories and chats
6. **Advanced Analytics** - Usage statistics dashboard

## References

- FastAPI Docs: <https://fastapi.tiangolo.com>
- Vue 3 Docs: <https://vuejs.org>
- Pinia Docs: <https://pinia.vuejs.org>
- Axios Docs: <https://axios-http.com>
