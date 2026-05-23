from pydantic import BaseModel, Field
from typing import Any, Optional
from uuid import UUID
from datetime import datetime

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
