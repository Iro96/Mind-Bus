import os
import logging

try:
    from redis import Redis
except ImportError:
    Redis = None

try:
    from rq import Queue
except ImportError:
    Queue = None

logger = logging.getLogger(__name__)

redis_url = os.getenv("REDIS_URL", "redis://localhost:6379")
redis_conn = Redis.from_url(redis_url, decode_responses=True) if Redis and Queue else None
queue = Queue("ai_agent_tasks", connection=redis_conn) if Redis and Queue else None


def enqueue_request(payload: dict, timeout: int = 300) -> str:
    """Enqueue a request for Redis/RQ worker processing."""
    if queue is None:
        logger.warning("Background queue unavailable; skipping enqueue")
        return ""

    try:
        from worker.tasks import process_task
        job = queue.enqueue(process_task, payload, timeout=timeout)
    except Exception as exc:
        logger.warning(
            "Failed to enqueue request for background processing; continuing without queue: %s",
            exc,
        )
        return ""

    logger.debug("Enqueued request: %s job_id=%s", payload.get("type"), job.id)
    return job.id


async def process_queue_worker():
    """Deprecated local worker; use rq worker ai_agent_tasks."""
    logger.info("RQ worker should be started separately with 'rq worker ai_agent_tasks'")
