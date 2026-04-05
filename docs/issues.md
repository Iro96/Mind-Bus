# Current Issues and Contribution Opportunities

This document outlines known issues, missing pieces, and places where frontend and backend work are needed.

## Current issues

### 1. Database initialization and missing schemas

- The project now includes an SQL migration file, but startup may still fail if the database schema is incomplete or not applied before the API/worker starts.
- The reflection worker depends on `reflection_jobs`, and the API depends on many other tables.

### 2. Queue and worker compatibility

- The Docker deployment includes `rq_worker`, but local Windows environments can fail because `rq` uses a `fork` process context.
- The API code currently falls back to a no-op queue on unsupported platforms.

### 3. Checkpoint persistence

- `agent/graph.py` previously tried to use a custom Postgres checkpointer, but it was not complete.
- The graph is currently compiled without persistence to prevent runtime crashes.
- Future work should restore safe checkpoint storage and resume support.

### 4. Frontend UI and feature completion

- The current static UI is minimal and does not show chat history or advanced controls.
- There is no route to persist sessions or thread history in the UI yet.
- `POST /chat/stream` and `GET /threads/{thread_id}` are placeholders.

## Help needed — frontend

### UI improvements

- Build a richer chat interface with message history, thread selection, and persisted chat state.
- Add support for streaming responses if the backend supports streaming.
- Improve the sidebar and navigation for `Home`, `History`, and `Settings`.

### Form and upload support

- Add document upload and retrieval UI for the `/documents/upload` endpoint.
- Add a proper tools page to run backend tools via `/tools/run`.
- Add auth/login UI if authentication is required in the future.

## Help needed — backend

### Backend stability

- Harden `apps/api/main.py` and `apps/api/services/queue_service.py` for queue failures and optional service dependencies.
- Add a startup health check for Postgres, Redis, and Qdrant.
- Ensure database migrations run before the API or worker processes start.

### API expansion

- Implement the placeholder endpoints in `apps/api/routes/chat.py`:
  - `POST /chat/stream`
  - `GET /threads/{thread_id}`
- Add additional API routes for session management, thread history, memory inspection, and tools.

### Persistence and memory

- Complete the `agent/checkpointer.py` persistence integration and ensure `agent/graph.py` can safely use it.
- Expand the memory system to connect `memory/` features with actual conversation state and retrieval.
- Add support for saving messages, threads, and tool calls to the database.

## Frontend/backend connection notes

### Current request flow

- Browser -> `GET /` serves the static frontend page.
- UI sends chat data to `POST /chat`.
- `chat_endpoint` builds an `AgentState` and invokes the agent graph.
- The graph performs planning, retrieval, compression, optional tool execution, and response generation.
- Final response is returned as a JSON object and displayed in the UI.

### Future connection opportunities

- Use WebSocket or server-sent events for chat streaming.
- Connect frontend history UI with backend `threads` and persistent conversation state.
- Enable frontend-driven tool execution and response playback.
- Add authenticated API access so users can manage their own chats and memory.

## Recommended next tasks

- Add a `docs/` entry in the repository root for discoverability.
- Implement a simple endpoint for `threads` and thread history.
- Improve `Dockerfile`/`docker-compose.yml` healthchecks and service readiness.
- Build a small React or vanilla frontend around the existing static UI for better UX.
