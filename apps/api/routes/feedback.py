from uuid import UUID

from apps.api.fastapi_compat import APIRouter, Depends, HTTPException
from ..schemas.base import FeedbackRequest, FeedbackResponse
from ..services.feedback_service import FeedbackService
from apps.api.security import get_current_user, require_roles

router = APIRouter(dependencies=[Depends(require_roles(["user", "admin"]))])

@router.post("/feedback", response_model=FeedbackResponse)
async def submit_feedback(payload: FeedbackRequest, user: dict = Depends(get_current_user)) -> FeedbackResponse:
    service = FeedbackService()
    try:
        result = service.ingest_feedback(
            thread_id=payload.thread_id,
            user_id=UUID(str(user["user_id"])),
            target_message_id=payload.target_message_id,
            feedback_type=payload.feedback_type,
            feedback_text=payload.feedback_text,
            severity=payload.severity,
        )
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc))

    return FeedbackResponse(
        feedback_event_id=result["feedback_event_id"],
        reflection_job_id=result["reflection_job_id"],
        correction_memory_id=result.get("correction_memory_id"),
        reflection_output=result["reflection_output"],
    )
