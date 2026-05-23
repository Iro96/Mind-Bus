import uuid

from memory.extraction import MemoryExtractor
from memory.schemas import MemoryExtractionRequest, SemanticMemory


def test_llm_memory_extraction():
    extractor = MemoryExtractor()
    request = MemoryExtractionRequest(
        conversation="User: I love every time we use Python.",
        user_id=uuid.UUID("00000000-0000-0000-0000-000000000000"),
        thread_id=uuid.UUID("00000000-0000-0000-0000-000000000000")
    )
    response = extractor.extract_memories(request)
    assert response.new_memories is not None
    assert isinstance(response.new_memories, list)
    assert len(response.new_memories) > 0


def test_extract_memories_updates_existing_memory_and_recalculates_confidence(monkeypatch):
    extractor = MemoryExtractor()
    user_id = uuid.uuid4()
    thread_id = uuid.uuid4()
    existing_memory = SemanticMemory(
        id=uuid.uuid4(),
        user_id=user_id,
        thread_id=thread_id,
        key="user_preference_python",
        value_json={
            "fact": "User prefers Python for scripting tasks",
            "provenance": "Observed earlier",
            "evidence_count": 2,
        },
        confidence=0.2,
        source_type="conversation",
        status="active",
    )

    monkeypatch.setattr(
        extractor,
        "_extract_via_llm",
        lambda _request: [
            {
                "type": "semantic",
                "key": "user_preference_python",
                "value": {
                    "fact": "User prefers Python for scripting tasks",
                    "provenance": "Observed again",
                    "evidence_count": 1,
                },
            }
        ],
    )

    response = extractor.extract_memories(
        MemoryExtractionRequest(
            conversation="User: Please remember that I prefer Python.",
            user_id=user_id,
            thread_id=thread_id,
            current_memories=[existing_memory],
        )
    )

    assert response.new_memories == []
    assert len(response.updated_memories) == 1
    updated_memory = response.updated_memories[0]
    assert updated_memory.id == existing_memory.id
    assert updated_memory.value_json["evidence_count"] == 3
    assert updated_memory.value_json["provenance"] == "Observed again"
    assert updated_memory.confidence > existing_memory.confidence
