# Project Structure

This file explains the repository layout and the role of major folders.

## Top-level folders

- `agent/`
  - Contains the AI agent graph and node functions that orchestrate planning, retrieval, compression, tool running, and response generation.
  - `graph.py` builds the workflow using `langgraph`.
  - `checkpointer.py` contains persistence logic for checkpoints.
  - `nodes/` holds individual agent tasks such as `planner`, `retriever`, `compressor`, `tool_runner`, and `responder`.
  - `state/` defines `AgentState` used by the graph.

- `apps/api/`
  - FastAPI application and route definitions.
  - `main.py` configures the app, middleware, static UI, and startup events.
  - `routes/` contains endpoints for chat, documents, memory, feedback, tools, and auth.
  - `schemas/` defines the request and response models.
  - `services/` contains helper services like queue handling.

- `memory/`
  - Implements long-term and short-term memory management.
  - Handles extraction, scoring, correction, and persistence of memories.

- `agent/retrieval/`
  - Manages document ingestion, chunking, Qdrant client, and hybrid search logic.

- `worker/`
  - Background worker processes and task pipelines.
  - `main.py` runs continuous reflection or other background jobs.
  - `pipelines/` defines processing pipelines such as reflection jobs.

- `storage/`
  - Database integration layer for Postgres.
  - `postgres.py` exposes a simple query interface.

- `deploy/`
  - Docker Compose files for local deployment.
  - `docker-compose.yml` defines API, worker, rq worker, Postgres, Redis, and Qdrant.

- `scripts/`
  - Helper scripts for container startup and migration initialization.

## Important files

- `README.md` — high-level project introduction and feature summary.
- `requirements.txt` — Python dependencies used by the app.
- `Dockerfile` — container build instructions.
- `migrations/0001_initial_schema.sql` — initial database schema.

## How components connect

- `apps/api/routes/chat.py` invokes `agent.create_graph()` and runs the agent graph for every chat request.
- `agent/graph.py` composes the agent workflow using nodes from `agent/nodes/`.
- The backend uses `storage/postgres.py` for relational persistence and `agent/retrieval/qdrant_client.py` for vector retrieval.
- Background jobs in `worker/` process reflection tasks and use the same DB connection.
- The frontend static page in `apps/api/static/index.html` submits user chat requests to `POST /chat`.
