import asyncio
import uuid

import pytest

from apps.api.fastapi_compat import HTTPException
from apps.api.routes import memory as memory_route
from apps.api.schemas.base import MemoryRefreshRequest
from memory.schemas import MemoryExtractionResponse, SemanticMemory


def _build_memory(*, memory_id=None, user_id=None, thread_id=None, key="user_preference_python", evidence_count=1):
    return SemanticMemory(
        id=memory_id,
        user_id=user_id or uuid.uuid4(),
        thread_id=thread_id,
        key=key,
        value_json={
            "fact": "User prefers Python for scripting tasks",
            "provenance": "Observed in conversation",
            "evidence_count": evidence_count,
        },
        confidence=min(evidence_count / 10.0, 1.0),
        source_type="conversation",
        status="active",
    )


def test_get_memories_returns_user_scoped_results(monkeypatch):
    user_id = uuid.uuid4()
    thread_id = uuid.uuid4()
    recorded = {}

    def fake_retrieve_memories(user_id, thread_id=None, memory_type=None, key_pattern=None, limit=100):
        recorded["user_id"] = user_id
        recorded["thread_id"] = thread_id
        recorded["memory_type"] = memory_type
        recorded["key_pattern"] = key_pattern
        recorded["limit"] = limit
        return [_build_memory(memory_id=uuid.uuid4(), user_id=user_id, thread_id=thread_id)]

    monkeypatch.setattr(memory_route.memory_manager, "retrieve_memories", fake_retrieve_memories)

    response = asyncio.run(
        memory_route.get_memories(
            thread_id=thread_id,
            memory_type="semantic",
            key="python",
            limit=500,
            user={"user_id": str(user_id), "roles": ["user"]},
        )
    )

    assert recorded["user_id"] == user_id
    assert recorded["thread_id"] == thread_id
    assert recorded["memory_type"] == "semantic"
    assert recorded["key_pattern"] == "python"
    assert recorded["limit"] == 200
    assert response.count == 1
    assert response.memories[0].thread_id == thread_id
    assert response.memories[0].memory_type == "semantic"


def test_get_memories_returns_503_when_storage_unavailable(monkeypatch):
    monkeypatch.setattr(
        memory_route.memory_manager,
        "retrieve_memories",
        lambda **_kwargs: (_ for _ in ()).throw(RuntimeError("db unavailable")),
    )

    with pytest.raises(HTTPException) as exc_info:
        asyncio.run(
            memory_route.get_memories(
                user={"user_id": str(uuid.uuid4()), "roles": ["user"]},
            )
        )

    assert exc_info.value.status_code == 503


def test_refresh_memories_rebuilds_thread_memories(monkeypatch):
    user_id = uuid.uuid4()
    thread_id = uuid.uuid4()
    existing_memory_id = uuid.uuid4()
    created_memory_id = uuid.uuid4()
    updated_memory_id = existing_memory_id
    current_memory = _build_memory(
        memory_id=existing_memory_id,
        user_id=user_id,
        thread_id=thread_id,
        evidence_count=2,
    )
    new_memory = _build_memory(
        user_id=user_id,
        thread_id=thread_id,
        key="project_language_python",
        evidence_count=1,
    )
    updated_memory = _build_memory(
        memory_id=existing_memory_id,
        user_id=user_id,
        thread_id=thread_id,
        evidence_count=3,
    )
    recorded = {"upserts": []}

    monkeypatch.setattr(
        memory_route.conversation_service,
        "list_thread_messages",
        lambda requested_user_id, requested_thread_id: [
            {"role": "user", "content": "Please remember that we prefer Python."},
            {"role": "assistant", "content": "I will remember that preference."},
        ],
    )

    monkeypatch.setattr(
        memory_route.memory_manager,
        "retrieve_memories",
        lambda **_kwargs: [current_memory],
    )

    def fake_extract_memories(request):
        assert request.thread_id == thread_id
        assert "user: Please remember that we prefer Python." in request.conversation
        assert "assistant: I will remember that preference." in request.conversation
        assert request.current_memories == [current_memory]
        return MemoryExtractionResponse(
            new_memories=[new_memory],
            updated_memories=[updated_memory],
        )

    monkeypatch.setattr(memory_route.memory_extractor, "extract_memories", fake_extract_memories)

    def fake_upsert_memory(memory):
        recorded["upserts"].append(memory.key)
        if memory.key == "project_language_python":
            return "created", created_memory_id
        return "updated", updated_memory_id

    monkeypatch.setattr(memory_route.memory_manager, "upsert_memory", fake_upsert_memory)

    response = asyncio.run(
        memory_route.refresh_memories(
            MemoryRefreshRequest(thread_id=thread_id),
            user={"user_id": str(user_id), "roles": ["user"]},
        )
    )

    assert recorded["upserts"] == ["project_language_python", "user_preference_python"]
    assert response.thread_id == thread_id
    assert response.created_count == 1
    assert response.updated_count == 1
    assert response.skipped_count == 0
    assert response.created_memory_ids == [created_memory_id]
    assert response.updated_memory_ids == [updated_memory_id]
    assert [memory.key for memory in response.memories] == ["project_language_python", "user_preference_python"]


def test_refresh_memories_returns_404_for_unknown_thread(monkeypatch):
    monkeypatch.setattr(
        memory_route.conversation_service,
        "list_thread_messages",
        lambda *_args, **_kwargs: (_ for _ in ()).throw(KeyError("thread_not_found")),
    )

    with pytest.raises(HTTPException) as exc_info:
        asyncio.run(
            memory_route.refresh_memories(
                MemoryRefreshRequest(thread_id=uuid.uuid4()),
                user={"user_id": str(uuid.uuid4()), "roles": ["user"]},
            )
        )

    assert exc_info.value.status_code == 404


def test_refresh_memories_returns_503_when_storage_unavailable(monkeypatch):
    monkeypatch.setattr(
        memory_route.conversation_service,
        "list_thread_messages",
        lambda *_args, **_kwargs: [{"role": "user", "content": "hello"}],
    )
    monkeypatch.setattr(
        memory_route.memory_manager,
        "retrieve_memories",
        lambda **_kwargs: (_ for _ in ()).throw(RuntimeError("db unavailable")),
    )

    with pytest.raises(HTTPException) as exc_info:
        asyncio.run(
            memory_route.refresh_memories(
                MemoryRefreshRequest(thread_id=uuid.uuid4()),
                user={"user_id": str(uuid.uuid4()), "roles": ["user"]},
            )
        )

    assert exc_info.value.status_code == 503
