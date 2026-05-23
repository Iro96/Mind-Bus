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


def test_feedback_service_persists_thread_and_user_context(monkeypatch):
    recorded_calls = []

    def fake_execute(query, params=None):
        recorded_calls.append((query, params))
        if "INSERT INTO feedback_events" in query:
            return [{"id": str(uuid.uuid4()), "created_at": None}]
        if "INSERT INTO reflection_jobs" in query:
            return [{"id": str(uuid.uuid4()), "created_at": None}]
        return 1

    from apps.api.services import feedback_service as feedback_module

    monkeypatch.setattr(feedback_module.db, "execute", fake_execute)

    service = FeedbackService()
    thread_id = uuid.uuid4()
    user_id = uuid.uuid4()
    target_message_id = uuid.uuid4()

    response = service.ingest_feedback(
        thread_id=thread_id,
        user_id=user_id,
        feedback_type="bug",
        feedback_text="The tool failed.",
        severity="high",
        target_message_id=target_message_id,
    )

    assert response["reflection_output"]["status"] == "pending"
    reflection_params = next(params for query, params in recorded_calls if "INSERT INTO reflection_jobs" in query)
    reflection_input = reflection_params[2]
    assert reflection_input["thread_id"] == str(thread_id)
    assert reflection_input["user_id"] == str(user_id)
    assert reflection_input["target_message_id"] == str(target_message_id)
