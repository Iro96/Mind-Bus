from pydantic import BaseModel, Field
from typing import Optional, Dict, Any
from datetime import datetime
from uuid import UUID


class BaseMemory(BaseModel):
    id: Optional[UUID] = None
    user_id: UUID
    thread_id: Optional[UUID] = None
    memory_type: str  # 'episodic', 'semantic', 'correction'
    key: str
    value_json: Dict[str, Any]
    confidence: Optional[float] = None
    source_type: Optional[str] = None
    source_id: Optional[UUID] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    expires_at: Optional[datetime] = None
    status: str = "active"


class EpisodicMemory(BaseMemory):
    memory_type: str = "episodic"
    # Contents: completed tasks, user decisions, important sessions, project milestones, failed attempts with explanation
    # Format: compact summary, timestamp, thread id, source pointers, confidence
    value_json: Dict[str, Any] = Field(..., description="Contains summary, timestamp, thread_id, source_pointers, confidence")


class SemanticMemory(BaseMemory):
    memory_type: str = "semantic"
    # Contents: user preferences, project constraints, stable facts, named entities, glossary terms, canonical decisions
    # Policy: only store with sufficient evidence, merge duplicates, allow overwrite, attach provenance and confidence
    value_json: Dict[str, Any] = Field(..., description="Contains fact, provenance, evidence_count, confidence")


class CorrectionMemory(BaseMemory):
    memory_type: str = "correction"
    # Contents: user corrections, confirmed mistakes, rejected assumptions, tool-use failures, retrieval failures, preferred style fixes
    # Policy: highest priority for similar errors, time-decay old corrections unless reinforced
    value_json: Dict[str, Any] = Field(..., description="Contains error_description, correction, context, reinforcement_count, confidence")


class MemoryExtractionRequest(BaseModel):
    conversation: str
    user_id: UUID
    thread_id: Optional[UUID] = None
    current_memories: Optional[list[BaseMemory]] = None


class MemoryExtractionResponse(BaseModel):
    new_memories: list[BaseMemory]
    updated_memories: list[BaseMemory]