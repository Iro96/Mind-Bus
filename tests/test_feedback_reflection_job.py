import uuid
from apps.api.services.feedback_service import FeedbackService
from worker.pipelines.reflection_pipeline import ReflectionPipeline


def test_feedback_reflection_job_integration():
    feedback_service = FeedbackService()

    # Create a fake reflection job payload
    feedback_payload = {
        "feedback_event_id": str(uuid.uuid4()),
        "feedback_type": "bug",
        "feedback_text": "The tool did not produce output.",
        "severity": "medium",
        "thread_id": None,
        "user_id": str(uuid.uuid4()),
        "target_message_id": None
    }

    reflection_pipeline = ReflectionPipeline()
    # Simulate reflection job row shape
    reflection_job = {"input_json": feedback_payload}
    result = reflection_pipeline.process_feedback_job(reflection_job)

    assert "candidate_fix" in result
    assert "validated_fix" in result
    assert result.get("pipeline_trace", {}).get("status") in ["validated", "rejected"]
