import time
import logging
import uuid
from fastapi import APIRouter, BackgroundTasks
from ..schemas.base import BaseResponse, ChatRequest
from agent import create_graph
from observability.logging import set_request_context, clear_request_context
from observability.tracing import trace_span
from observability.metrics import record_tool_call_latency, record_request_latency
from apps.api.services.queue_service import enqueue_request


router = APIRouter()
logger = logging.getLogger(__name__)


@router.post("/chat")
async def chat_endpoint(request: ChatRequest, background_tasks: BackgroundTasks) -> BaseResponse:
    request_id = str(uuid.uuid4())
    set_request_context(request_id=request_id)

    with trace_span("chat_endpoint"):
        start = time.perf_counter()

        # Initialize state
        state = {
            "messages": [{"role": "user", "content": request.message}],
            "current_task": None,
            "tool_calls": [],
            "tool_results": [],
            "retry_count": 0,
            "final_response": None,
        }

        # Create and run graph
        app = create_graph()
        thread_id = str(uuid.uuid4())
        result = app.invoke(state, config={"configurable": {"thread_id": thread_id}})

        # Enqueue for future processing (scaling): store history+state for analytics and memory ingestion
        background_tasks.add_task(
            enqueue_request,
            {
                "type": "chat_analysis",
                "request_id": request_id,
                "message": request.message,
                "state": state,
            },
        )

        latency_ms = (time.perf_counter() - start) * 1000.0
        record_request_latency(latency_ms)

        logger.info(
            "chat_endpoint completed (request_id=%s, latency_ms=%.2f)",
            request_id,
            latency_ms,
        )

    clear_request_context()
    return BaseResponse(message=result.get("final_response", "No response"))


@router.post("/chat/stream")
async def chat_stream_endpoint() -> BaseResponse:
    return BaseResponse(message="Chat stream endpoint placeholder")


@router.get("/threads/{thread_id}")
async def get_thread(thread_id: str) -> BaseResponse:
    return BaseResponse(message=f"Thread {thread_id} placeholder")