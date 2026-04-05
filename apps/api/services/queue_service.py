import os
import logging
from redis import Redis
from worker.tasks import process_task

logger = logging.getLogger(__name__)

redis_url = os.getenv("REDIS_URL", "redis://localhost:6379")
redis_conn = Redis.from_url(redis_url, decode_responses=True)
queue = None

try:
    from rq import Queue

    queue = Queue("ai_agent_tasks", connection=redis_conn)
except (ImportError, ValueError) as exc:
    logger.warning(
        "Redis Queue unavailable in this environment (%s); enqueue_request will be a no-op.",
        exc,
    )


def enqueue_request(payload: dict, timeout: int = 300) -> str:
    """Enqueue a request for Redis/RQ worker processing."""
    if queue is None:
        logger.warning(
            "enqueue_request called but Redis Queue is unavailable; skipping background queue enqueue."
        )
        return "queue-unavailable"

    job = queue.enqueue(process_task, payload, timeout=timeout)
    logger.debug("Enqueued request: %s job_id=%s", payload.get("type"), job.id)
    return job.id


async def process_queue_worker():
    """Deprecated local worker; use rq worker ai_agent_tasks."""
    logger.info("RQ worker should be started separately with 'rq worker ai_agent_tasks'")
