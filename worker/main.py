import logging
import time
import uuid
from datetime import datetime

from storage.postgres import db
from worker.pipelines.reflection_pipeline import ReflectionPipeline
from observability.logging import init_logging, set_request_context, clear_request_context
from observability.tracing import trace_request, trace_span
from observability.metrics import record_request_latency, record_queue_backlog
from observability.alerts import check_all_alerts

logger = logging.getLogger(__name__)
init_logging()


def fetch_pending_reflection_jobs(limit: int = 10):
    query = """
    SELECT id, feedback_event_id, input_json
    FROM reflection_jobs
    WHERE status = 'pending'
    ORDER BY created_at ASC
    LIMIT %s
    """
    return db.execute(query, (limit,)) or []


def update_reflection_job_status(job_id: str, status: str, output_json: dict = None):
    query = """
    UPDATE reflection_jobs
    SET status = %s, output_json = %s, updated_at = NOW()
    WHERE id = %s
    """
    db.execute(query, (status, output_json, job_id))


def process_pending_jobs():
    pipeline = ReflectionPipeline()

    while True:
        jobs = fetch_pending_reflection_jobs(limit=5)
        record_queue_backlog(len(jobs))

        if not jobs:
            logger.debug("No pending reflection jobs found, sleeping for 5 seconds")
            time.sleep(5)
            continue

        for job in jobs:
            job_id = job["id"]
            request_id = str(uuid.uuid4())
            set_request_context(request_id=request_id)

            with trace_request(request_id):
                with trace_span("reflection_job"):
                    logger.info("Processing reflection job %s (request_id=%s)", job_id, request_id)
                    start = time.perf_counter()
                    try:
                        update_reflection_job_status(job_id, "in_progress")

                        result = pipeline.process_feedback_job(job)

                        update_reflection_job_status(job_id, "completed", output_json={
                            "result": result,
                            "processed_at": datetime.utcnow().isoformat() + "Z",
                        })

                        duration_ms = (time.perf_counter() - start) * 1000.0
                        record_request_latency(duration_ms)

                        logger.info(
                            "Reflection job %s completed (request_id=%s, latency_ms=%.2f)",
                            job_id,
                            request_id,
                            duration_ms,
                        )
                        check_all_alerts()
                    except Exception as exc:
                        logger.exception("Reflection job %s failed (request_id=%s)", job_id, request_id)
                        update_reflection_job_status(job_id, "failed", output_json={
                            "error": str(exc),
                            "traceback": None,
                            "failed_at": datetime.utcnow().isoformat() + "Z",
                        })
                    finally:
                        clear_request_context()

        time.sleep(1)


if __name__ == "__main__":
    logger.info("Starting reflection worker")
    process_pending_jobs()
