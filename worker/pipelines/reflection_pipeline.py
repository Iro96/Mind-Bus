import logging
from typing import Any, Dict
from uuid import UUID

from apps.api.services.feedback_service import FeedbackService
from memory.correction import CorrectionMemoryHandler
from memory.long_term import LongTermMemoryManager
from observability.metrics import record_correction

logger = logging.getLogger(__name__)


class ReflectionPipeline:
    """Reflection pipeline for analyzing feedback and updating long-term memory."""

    def __init__(self):
        self.feedback_service = FeedbackService()
        self.correction_handler = CorrectionMemoryHandler(LongTermMemoryManager())

    def process_feedback_job(self, reflection_job: Dict[str, Any]) -> Dict[str, Any]:
        """Process a single reflection job row and return pipeline output."""
        input_json = reflection_job.get("input_json") or {}
        feedback_type = input_json.get("feedback_type")
        feedback_text = input_json.get("feedback_text")
        severity = input_json.get("severity")
        thread_id = input_json.get("thread_id")
        user_id = input_json.get("user_id")
        target_message_id = input_json.get("target_message_id")

        # 1. Classification and candidate generation (LLM placeholder)
        reflection_result = self.feedback_service._analyze_feedback(
            feedback_type=feedback_type,
            feedback_text=feedback_text,
            severity=severity,
        )

        # 2. Validate candidate fix (placeholder) with guardrail
        reflection_result["validated_fix"] = self.validate_candidate_fix(reflection_result)

        # 3. Update memory if valid
        correction_memory_id = None
        if reflection_result["validated_fix"] and user_id:
            try:
                correction_memory_id = self.correction_handler.add_correction(
                    user_id=UUID(user_id),
                    error_description=reflection_result.get("issue_explanation", "reflection update"),
                    correction=reflection_result.get("candidate_fix", ""),
                    context=f"thread:{thread_id} target_message:{target_message_id}",
                    thread_id=UUID(thread_id) if thread_id else None,
                )
            except Exception as e:
                logger.warning("Failed to write correction memory: %s", e)

        reflection_result["correction_memory_id"] = str(correction_memory_id) if correction_memory_id else None

        # Correction metrics
        record_correction(accepted=bool(reflection_result.get("validated_fix", False)))

        # 4. Trace field
        reflection_result["pipeline_trace"] = {
            "processed_by": "ReflectionPipeline",
            "status": "validated" if reflection_result["validated_fix"] else "rejected",
        }

        return reflection_result

    @staticmethod
    def validate_candidate_fix(reflection_result: Dict[str, Any]) -> bool:
        """Placeholder validation check for candidate fixes."""
        if not reflection_result:
            return False
        candidate_fix = (reflection_result.get("candidate_fix") or "").strip()
        if not candidate_fix:
            return False

        # Confidence threshold guardrail placeholder
        if reflection_result.get("valid_fix") is False:
            return False

        return True
