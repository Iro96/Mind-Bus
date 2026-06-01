from typing import Iterable, Optional
from uuid import UUID

from apps.api.fastapi_compat import APIRouter, Depends, HTTPException, status
from apps.api.security import get_current_user
from apps.api.services.conversation_service import ConversationService
from memory.extraction import MemoryExtractor
from memory.long_term import LongTermMemoryManager
from memory.schemas import BaseMemory, MemoryExtractionRequest

from ..schemas.base import (
    MemoryListResponse,
    MemoryRefreshRequest,
    MemoryRefreshResponse,
    MemoryResponse,
)

router = APIRouter(prefix="/memory")
conversation_service = ConversationService()
memory_manager = LongTermMemoryManager()
memory_extractor = MemoryExtractor()
ALLOWED_MEMORY_TYPES = {"episodic", "semantic", "correction"}


def _require_user_id(user: dict) -> UUID:
    user_id = user.get("user_id")
    if not user_id:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Missing user identity")
    return UUID(str(user_id))


def _validate_memory_type(memory_type: Optional[str]) -> Optional[str]:
    if memory_type is None:
        return None
    if memory_type not in ALLOWED_MEMORY_TYPES:
        raise HTTPException(status_code=400, detail="Unsupported memory_type")
    return memory_type


def _serialize_memory(memory: BaseMemory) -> MemoryResponse:
    return MemoryResponse(**memory.model_dump())


def _build_transcript(messages: Iterable[dict]) -> str:
    lines = []
    for message in messages:
        role = message.get("role", "unknown")
        content = (message.get("content") or "").strip()
        if content:
            lines.append(f"{role}: {content}")
    return "\n".join(lines)


def _memory_or_503(action: str, memory: BaseMemory) -> tuple[str, UUID]:
    result_action, memory_id = memory_manager.upsert_memory(memory)
    if memory_id is None:
        raise RuntimeError(f"Memory {action} did not return an id")
    return result_action, memory_id


@router.get("/memories", response_model=MemoryListResponse)
async def get_memories(
    thread_id: Optional[UUID] = None,
    memory_type: Optional[str] = None,
    key: Optional[str] = None,
    limit: int = 50,
    user: dict = Depends(get_current_user),
) -> MemoryListResponse:
    user_id = _require_user_id(user)
    validated_memory_type = _validate_memory_type(memory_type)
    bounded_limit = max(1, min(limit, 200))

    try:
        memories = memory_manager.retrieve_memories(
            user_id=user_id,
            thread_id=thread_id,
            memory_type=validated_memory_type,
            key_pattern=key,
            limit=bounded_limit,
        )
    except Exception as exc:
        raise HTTPException(status_code=503, detail="Memory storage unavailable") from exc

    serialized = [_serialize_memory(memory) for memory in memories]
    return MemoryListResponse(memories=serialized, count=len(serialized))


@router.post("/memories/refresh", response_model=MemoryRefreshResponse)
async def refresh_memories(
    payload: MemoryRefreshRequest,
    user: dict = Depends(get_current_user),
) -> MemoryRefreshResponse:
    user_id = _require_user_id(user)

    try:
        messages = conversation_service.list_thread_messages(user_id, payload.thread_id)
    except KeyError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Thread not found",
        ) from exc

    transcript = _build_transcript(messages)

    try:
        current_memories = memory_manager.retrieve_memories(
            user_id=user_id,
            thread_id=payload.thread_id,
            limit=200,
        )
    except Exception as exc:
        raise HTTPException(status_code=503, detail="Memory storage unavailable") from exc

    extraction_result = memory_extractor.extract_memories(
        MemoryExtractionRequest(
            conversation=transcript,
            user_id=user_id,
            thread_id=payload.thread_id,
            current_memories=current_memories,
        )
    )

    created_ids: list[UUID] = []
    updated_ids: list[UUID] = []
    changed_memories: list[BaseMemory] = []

    try:
        for memory in extraction_result.new_memories:
            action, memory_id = _memory_or_503("create", memory)
            changed_memories.append(memory.model_copy(update={"id": memory_id}))
            if action == "created":
                created_ids.append(memory_id)
            else:
                updated_ids.append(memory_id)

        for memory in extraction_result.updated_memories:
            action, memory_id = _memory_or_503("update", memory)
            changed_memories.append(memory.model_copy(update={"id": memory_id}))
            if action == "created":
                created_ids.append(memory_id)
            else:
                updated_ids.append(memory_id)
    except Exception as exc:
        raise HTTPException(status_code=503, detail="Memory storage unavailable") from exc

    serialized_memories = [
        _serialize_memory(memory)
        for memory in sorted(
            changed_memories,
            key=lambda item: (item.memory_type, item.key, str(item.id)),
        )
    ]

    return MemoryRefreshResponse(
        thread_id=payload.thread_id,
        created_count=len(created_ids),
        updated_count=len(updated_ids),
        skipped_count=0,
        created_memory_ids=sorted(created_ids, key=str),
        updated_memory_ids=sorted(updated_ids, key=str),
        memories=serialized_memories,
    )


@router.get("", response_model=dict)
async def get_memories_alias(
    memory_type: Optional[str] = None,
    limit: int = 50,
    user: dict = Depends(get_current_user),
) -> dict:
    """Alias for /memories endpoint for frontend compatibility"""
    user_id = _require_user_id(user)
    validated_memory_type = _validate_memory_type(memory_type)
    bounded_limit = max(1, min(limit, 200))

    try:
        memories = memory_manager.retrieve_memories(
            user_id=user_id,
            thread_id=None,
            memory_type=validated_memory_type,
            key_pattern=None,
            limit=bounded_limit,
        )
    except Exception as exc:
        raise HTTPException(status_code=503, detail="Memory storage unavailable") from exc

    serialized = [_serialize_memory(memory) for memory in memories]
    return {"memories": serialized, "count": len(serialized)}


@router.delete("/{memory_id}")
async def delete_memory(memory_id: str, user: dict = Depends(get_current_user)) -> dict:
    """Delete a memory by ID"""
    user_id = _require_user_id(user)
    
    try:
        parsed_id = UUID(memory_id)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid memory_id")
    
    try:
        memory_manager.delete_memory(parsed_id, user_id)
        return {"message": "Memory deleted"}
    except KeyError:
        raise HTTPException(status_code=404, detail="Memory not found")
    except Exception as exc:
        raise HTTPException(status_code=500, detail="Failed to delete memory") from exc
