from pydantic import BaseModel
from typing import Optional
from uuid import UUID

class BaseResponse(BaseModel):
    message: str

class ErrorResponse(BaseModel):
    error: str

class ChatRequest(BaseModel):
    message: str

class FeedbackRequest(BaseModel):
    thread_id: UUID
    user_id: UUID
    target_message_id: Optional[UUID] = None
    feedback_type: str
    feedback_text: str
    severity: Optional[str] = None

class FeedbackResponse(BaseModel):
    feedback_event_id: UUID
    reflection_job_id: UUID
    correction_memory_id: Optional[UUID] = None
    reflection_output: dict
