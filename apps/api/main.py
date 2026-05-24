import asyncio
import logging
import time
import uuid
from contextlib import asynccontextmanager

from apps.api.fastapi_compat import FastAPI, Request
from .routes import chat, memory, documents, feedback, admin, tools, auth
from observability.logging import init_logging, set_request_context, clear_request_context
from observability.tracing import trace_request
from observability.metrics import record_request_latency
from observability.alerts import check_all_alerts
from apps.api.services.queue_service import process_queue_worker

logger = logging.getLogger(__name__)

init_logging()


@asynccontextmanager
async def lifespan(_app: FastAPI):
    queue_worker_task = asyncio.create_task(process_queue_worker())
    try:
        yield
    finally:
        if not queue_worker_task.done():
            queue_worker_task.cancel()
            try:
                await queue_worker_task
            except asyncio.CancelledError:
                pass


app = FastAPI(title="AI Agent Platform API", version="1.0.0", lifespan=lifespan)


@app.middleware("http")
async def observability_middleware(request: Request, call_next):
    request_id = str(uuid.uuid4())
    set_request_context(request_id=request_id)

    try:
        with trace_request(request_id):
            start = time.perf_counter()
            response = await call_next(request)
            latency_ms = (time.perf_counter() - start) * 1000.0
            record_request_latency(latency_ms)

            logger.info(
                "HTTP %s %s finished (request_id=%s, status=%s, latency_ms=%.2f)",
                request.method,
                request.url.path,
                request_id,
                response.status_code,
                latency_ms,
            )

            check_all_alerts()
            return response
    finally:
        clear_request_context()


app.include_router(auth.router)
app.include_router(chat.router)
app.include_router(memory.router)
app.include_router(documents.router)
app.include_router(feedback.router)
app.include_router(admin.router)
app.include_router(tools.router)


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000, workers=4)
