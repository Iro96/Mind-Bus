import time
import logging
import uuid
from uuid import UUID

import agent
from apps.api.fastapi_compat import APIRouter, BackgroundTasks, Depends, HTTPException, status
from apps.api.security import get_current_user
from apps.api.services.conversation_service import ConversationService
from apps.api.services.queue_service import dispatch_request
from apps.api.schemas.base import BaseResponse, ChatRequest, ChatResponse, ThreadMessageResponse, ThreadResponse
from observability.logging import get_request_id
from observability.tracing import trace_span
from observability.metrics import record_request_latency


router = APIRouter()
logger = logging.getLogger(__name__)
conversation_service = ConversationService()


@router.post("/chat", response_model=ChatResponse)
async def chat_endpoint(
    request: ChatRequest,
    background_tasks: BackgroundTasks,
    user: dict = Depends(get_current_user),
) -> ChatResponse:
    request_id = get_request_id() or str(uuid.uuid4())
    user_id = user.get("user_id")
    if not user_id:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Missing user identity")

    with trace_span("chat_endpoint"):
        start = time.perf_counter()
        try:
            thread = conversation_service.get_or_create_thread(
                user_id=UUID(str(user_id)),
                requested_thread_id=request.thread_id,
                title_hint=request.message,
            )
        except KeyError as exc:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Thread not found",
            ) from exc

        thread_id = thread["id"]
        conversation_service.add_message(UUID(thread_id), "user", request.message)
        messages = conversation_service.build_state_messages(UUID(str(user_id)), UUID(thread_id))

        state = {
            "messages": messages,
            "current_task": None,
            "current_user_message": request.message,
            "tool_calls": [],
            "tool_results": [],
            "retry_count": 0,
            "final_response": None,
        }

        graph_app = agent.create_graph()
        result = graph_app.invoke(
            state,
            config={"configurable": {"thread_id": thread_id}},
        )
        final_response = result.get("final_response", "No response")
        conversation_service.add_message(UUID(thread_id), "assistant", final_response)

        background_tasks.add_task(
            dispatch_request,
            {
                "type": "chat_analysis",
                "request_id": request_id,
                "user_id": str(user_id),
                "thread_id": thread_id,
                "message": request.message,
                "state": state,
            },
        )

        latency_ms = (time.perf_counter() - start) * 1000.0
        record_request_latency(latency_ms)

        logger.info(
            "chat_endpoint completed (request_id=%s, thread_id=%s, latency_ms=%.2f)",
            request_id,
            thread_id,
            latency_ms,
        )

    return ChatResponse(message=final_response, thread_id=UUID(thread_id))


@router.post("/chat/stream")
async def chat_stream_endpoint() -> BaseResponse:
    raise HTTPException(
        status_code=status.HTTP_501_NOT_IMPLEMENTED,
        detail="Streaming chat is not implemented in this beta",
    )


@router.get("/chat/threads", response_model=dict)
async def list_threads(user: dict = Depends(get_current_user)):
    try:
        threads = conversation_service.list_user_threads(UUID(str(user["user_id"])))
    except Exception as exc:
        logger.error("Error listing threads: %s", exc)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to list threads",
        ) from exc

    return {
        "threads": threads,
        "count": len(threads)
    }


@router.get("/chat/threads/{thread_id}", response_model=dict)
async def get_thread(thread_id: UUID, user: dict = Depends(get_current_user)):
    try:
        thread = conversation_service.get_thread(UUID(str(user["user_id"])), thread_id)
        messages = conversation_service.list_thread_messages(UUID(str(user["user_id"])), thread_id)
    except KeyError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Thread not found",
        ) from exc

    return {
        "thread": thread,
        "messages": messages
    }
