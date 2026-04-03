import logging
import uuid
from worker.pipelines.reflection_pipeline import ReflectionPipeline
from memory.long_term import LongTermMemoryManager
from memory.extraction import MemoryExtractor

logger = logging.getLogger(__name__)


def process_task(payload: dict) -> dict:
    """Process queued payloads from RQ."""
    logger.info("Processing task payload: %s", payload)
    task_type = payload.get("type")

    if task_type == "chat_analysis":
        conversation = payload.get("message")
        user_id = payload.get("user_id")
        thread_id = payload.get("thread_id")

        if not (conversation and user_id):
            return {"status": "bad_payload"}

        # Extract memories from chat history
        extractor = MemoryExtractor()
        from memory.schemas import MemoryExtractionRequest
        extraction_request = MemoryExtractionRequest(
            conversation=conversation,
            user_id=uuid.UUID(user_id) if isinstance(user_id, str) else user_id,
            thread_id=uuid.UUID(thread_id) if isinstance(thread_id, str) and thread_id else None,
        )
        extraction_result = extractor.extract_memories(extraction_request)
        # Write extracted memories
        manager = LongTermMemoryManager()
        for memory in extraction_result.new_memories:
            manager.store_memory(memory)

        return {"status": "ok", "extracted": len(extraction_result.new_memories)}

    if task_type == "feedback_reflection":
        reflection_pipeline = ReflectionPipeline()
        reflection_job = payload.get("reflection_job")
        result = reflection_pipeline.process_feedback_job(reflection_job)
        return {"status": "ok", "result": result}

    return {"status": "unknown_task", "type": task_type}
