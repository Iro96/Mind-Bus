# Developer Tutorial

This tutorial shows how to set up the project locally, run the API, and understand the main frontend/backend flow.

## Prerequisites

- Docker and Docker Compose
- Python 3.12 (for local development outside Docker)
- Git

## Local development with Docker

From the repository root:

```bash
git clone https://github.com/Iro96/Mind-Bus.git
cd Mind-Bus
docker compose up --build
```

Then open the app in a browser:

```text
http://localhost:8000
```

## What starts in Docker

- `api` — FastAPI app on port 8000
- `postgres` — Postgres database
- `redis` — Redis queue backend
- `qdrant` — semantic vector search engine
- `worker` — reflection and background processing
- `rq_worker` — Redis queue worker for async jobs

## Running the API directly

If you want to run the API without Docker, install dependencies and start Uvicorn:

```bash
pip install -r requirements.txt
uvicorn apps.api.main:app --host 0.0.0.0 --port 8000
```

## Frontend / backend connection

- The UI is served by `apps/api/main.py` from `apps/api/static/index.html`.
- The client sends chat requests to `/chat`.
- `apps/api/routes/chat.py` receives the request, builds `state`, and calls `agent.create_graph()`.
- The agent graph runs through nodes in `agent/nodes/` to produce `final_response`.
- The response is returned as JSON and rendered in the browser.

## Simple test

Open the browser and send a message in the chat UI.

If you want to verify the backend without the UI, send a POST to `/chat`:

```bash
curl -X POST http://localhost:8000/chat \
  -H "Content-Type: application/json" \
  -d '{"message":"Hello"}'
```

## Common troubleshooting

- If `python-multipart` is missing, install it via `pip install python-multipart` or rebuild the Docker image after updating `requirements.txt`.
- If the worker fails due to missing tables, ensure database initialization runs successfully.
- Ensure `OPENAI_API_KEY` is set to enable real LLM calls; otherwise the app uses mock responses.
