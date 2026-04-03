import logging
from .metrics import metrics

logger = logging.getLogger(__name__)

ALERT_THRESHOLDS = {
    "retrieval_failures": 10,
    "memory_overwrites": 5,
    "queue_backlog": 100,
    "hallucination_reports": 10,
    "correction_reports": 20,
}


def _alert(name: str, value):
    logger.warning("ALERT: %s threshold crossed (value=%s)", name, value)


def check_all_alerts():
    snapshot = metrics.get_snapshot()
    counters = snapshot.get("counters", {})
    gauges = snapshot.get("gauges", {})

    if counters.get("retrieval_failures", 0) >= ALERT_THRESHOLDS["retrieval_failures"]:
        _alert("retrieval_failure_spike", counters.get("retrieval_failures"))

    if counters.get("memory_overwrites", 0) >= ALERT_THRESHOLDS["memory_overwrites"]:
        _alert("memory_overwrite_anomaly", counters.get("memory_overwrites"))

    if gauges.get("queue_backlog", 0) >= ALERT_THRESHOLDS["queue_backlog"]:
        _alert("queue_backlog", gauges.get("queue_backlog"))

    if counters.get("hallucination_reports", 0) >= ALERT_THRESHOLDS["hallucination_reports"]:
        _alert("high_hallucination_feedback", counters.get("hallucination_reports"))

    if counters.get("correction_reports", 0) >= ALERT_THRESHOLDS["correction_reports"]:
        _alert("repeated_correction_loop", counters.get("correction_reports"))
