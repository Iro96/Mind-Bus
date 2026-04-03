import os
from llm.client import LLMClient
from memory.extraction import MemoryExtractor
from memory.schemas import MemoryExtractionRequest


def test_llm_client_fallback_mock():
    client = LLMClient()
    response = client.generate_text("Hello world", max_tokens=10)
    assert isinstance(response, str)


def test_memory_extraction_fallback_data():
    extractor = MemoryExtractor()
    request = MemoryExtractionRequest(conversation="User said this and that", user_id="00000000-0000-0000-0000-000000000000", thread_id="00000000-0000-0000-0000-000000000000")
    output = extractor.extract_memories(request)
    assert output.new_memories
    assert output.updated_memories == []
