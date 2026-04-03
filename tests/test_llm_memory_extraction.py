import uuid
from memory.extraction import MemoryExtractor
from memory.schemas import MemoryExtractionRequest


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
