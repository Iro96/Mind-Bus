from datetime import datetime
from typing import Optional
from uuid import UUID

from memory.correction import CorrectionMemoryHandler
from memory.long_term import LongTermMemoryManager
from storage.postgres import db


class FeedbackService:
    def __init__(self):
        self.memory_manager = LongTermMemoryManager()
        self.correction_handler = CorrectionMemoryHandler(self.memory_manager)

    def ingest_feedback(
        self,
        thread_id: UUID,
        user_id: UUID,
        feedback_type: str,
        feedback_text: str,
        severity: Optional[str] = None,
        target_message_id: Optional[UUID] = None,
    ) -> dict:
        # 1. Persist feedback event
        insert_feedback = """
        INSERT INTO feedback_events (
            thread_id, user_id, target_message_id, feedback_type, feedback_text, severity
        ) VALUES (%s, %s, %s, %s, %s, %s)
        RETURNING id, created_at
        """

        feedback_row = db.execute(
            insert_feedback,
            (
                str(thread_id),
                str(user_id),
                str(target_message_id) if target_message_id else None,
                feedback_type,
                feedback_text,
                severity,
            ),
        )

        if not feedback_row or len(feedback_row) == 0:
            raise RuntimeError("Failed to persist feedback event")

        feedback_event_id = UUID(feedback_row[0]["id"])

        # 2. Create reflection job
        reflection_input = {
            "feedback_event_id": str(feedback_event_id),
            "feedback_type": feedback_type,
            "feedback_text": feedback_text,
            "severity": severity,
            "target_message_id": str(target_message_id) if target_message_id else None,
        }

        insert_reflection = """
        INSERT INTO reflection_jobs (feedback_event_id, status, input_json)
        VALUES (%s, %s, %s)
        RETURNING id, created_at
        """

        reflection_row = db.execute(
            insert_reflection,
            (str(feedback_event_id), "pending", reflection_input),
        )

        if not reflection_row or len(reflection_row) == 0:
            raise RuntimeError("Failed to create reflection job")

        reflection_job_id = UUID(reflection_row[0]["id"])

        # 3. Mark feedback processed, reflection worker handles analysis
        update_feedback_processed = """
        UPDATE feedback_events
        SET processed_at = NOW()
        WHERE id = %s
        """

        db.execute(update_feedback_processed, (str(feedback_event_id),))

        # 4. Return reflection-job reference (placeholder output from worker)
        return {
            "feedback_event_id": str(feedback_event_id),
            "reflection_job_id": str(reflection_job_id),
            "correction_memory_id": None,
            "reflection_output": {"status": "pending", "details": "Reflection pipeline worker will process this job shortly."},
        }

    def _analyze_feedback(self, feedback_type: str, feedback_text: str, severity: Optional[str]) -> dict:
        """LLM-based reflection analysis logic."""
        from llm.client import LLMClient

        llm = LLMClient()
        prompt = (
            "Analyze this user feedback and classify the root issue. "
            "Return JSON with fields: issue_source, issue_explanation, candidate_fix, valid_fix (bool).\n"
            f"feedback_type: {feedback_type}\n"
            f"feedback_text: {feedback_text}\n"
            f"severity: {severity}\n"
        )

        response = llm.chat_completion([
            {"role": "system", "content": "You are an assistant that maps feedback to corrective actions."},
            {"role": "user", "content": prompt},
        ])

        # Normalize output
        if isinstance(response, dict) and "issue_source" in response:
            return response

        if isinstance(response, dict) and "content" in response:
            try:
                parsed = json.loads(response["content"])
                if isinstance(parsed, dict):
                    return parsed
            except Exception:
                pass

        # fallback rule-based
        text = feedback_text.lower() if feedback_text else ""
        candidate_fix = "Please provide a correct response based on the intended user instruction."

        if "tool" in text or "api" in text:
            issue_source = "missing tool use"
            candidate_fix = "Try using the relevant tool or API to satisfy user intent."
        elif "stale" in text or "outdated" in text:
            issue_source = "stale memory"
            candidate_fix = "Refresh context and retrieve the most recent data for this query."
        elif "wrong" in text or "incorrect" in text or "error" in text:
            issue_source = "generation error"
            candidate_fix = "Adjust generation to correct the mistaken detail in the response."
        else:
            issue_source = "other"

        valid_fix = feedback_type.lower() in ["correction", "bug", "issue", "feedback"] or "fix" in text

        return {
            "issue_source": issue_source,
            "issue_explanation": f"Detected {issue_source} from feedback",
            "candidate_fix": candidate_fix,
            "valid_fix": valid_fix,
            "raw_feedback_text": feedback_text,
            "severity": severity,
        }
