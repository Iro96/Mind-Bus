from datetime import datetime
from typing import Any, Literal, Optional
from uuid import UUID

from pydantic import BaseModel, Field

class BaseResponse(BaseModel):
    message: str

class ErrorResponse(BaseModel):
    error: str

class AuthTokenRequest(BaseModel):
    username: str
    password: str

class AuthTokenResponse(BaseModel):
    access_token: str
    token_type: str

class ChatResponse(BaseModel):
    message: str
    thread_id: UUID

class ThreadMessageResponse(BaseModel):
    id: UUID
    role: str
    content: Optional[str] = None
    created_at: Optional[datetime] = None
    metadata: dict[str, Any] = Field(default_factory=dict)

class ThreadResponse(BaseModel):
    thread_id: UUID
    messages: list[ThreadMessageResponse]

class ChatRequest(BaseModel):
    message: str
    thread_id: Optional[UUID] = None

class FeedbackRequest(BaseModel):
    thread_id: UUID
    target_message_id: Optional[UUID] = None
    feedback_type: str
    feedback_text: str
    severity: Optional[str] = None

class FeedbackResponse(BaseModel):
    feedback_event_id: UUID
    reflection_job_id: UUID
    correction_memory_id: Optional[UUID] = None
    reflection_output: dict


MemoryType = Literal["episodic", "semantic", "correction"]


class MemoryResponse(BaseModel):
    id: UUID
    user_id: UUID
    thread_id: Optional[UUID] = None
    memory_type: MemoryType
    key: str
    value_json: dict[str, Any] = Field(default_factory=dict)
    confidence: Optional[float] = None
    source_type: Optional[str] = None
    source_id: Optional[UUID] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    expires_at: Optional[datetime] = None
    status: str


class MemoryListResponse(BaseModel):
    memories: list[MemoryResponse]
    count: int


class MemoryRefreshRequest(BaseModel):
    thread_id: UUID


class MemoryRefreshResponse(BaseModel):
    thread_id: UUID
    created_count: int
    updated_count: int
    skipped_count: int
    created_memory_ids: list[UUID] = Field(default_factory=list)
    updated_memory_ids: list[UUID] = Field(default_factory=list)
    memories: list[MemoryResponse] = Field(default_factory=list)
