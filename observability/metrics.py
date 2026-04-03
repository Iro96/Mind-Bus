import threading
import time
from typing import Dict

class MetricRegistry:
    def __init__(self):
        self._lock = threading.Lock()
        self.counters: Dict[str, int] = {}
        self.gauges: Dict[str, float] = {}
        self.histograms: Dict[str, list] = {}

    def inc(self, name: str, value: int = 1):
        with self._lock:
            self.counters[name] = self.counters.get(name, 0) + value

    def set_gauge(self, name: str, value: float):
        with self._lock:
            self.gauges[name] = value

    def observe(self, name: str, value: float):
        with self._lock:
            lst = self.histograms.setdefault(name, [])
            lst.append(value)

    def get_snapshot(self):
        with self._lock:
            return {
                "counters": dict(self.counters),
                "gauges": dict(self.gauges),
                "histograms": {k: list(v) for k, v in self.histograms.items()},
            }


metrics = MetricRegistry()


def record_request_latency(latency_ms: float):
    metrics.observe("request_latency_ms", latency_ms)
    metrics.inc("request_count")


def record_tool_call_latency(latency_ms: float):
    metrics.observe("tool_call_latency_ms", latency_ms)
    metrics.inc("tool_call_count")


def record_retrieval_hit(success: bool):
    metrics.inc("retrieval_hits" if success else "retrieval_misses")


def record_memory_write(overwrite: bool = False):
    metrics.inc("memory_writes")
    if overwrite:
        metrics.inc("memory_overwrites")


def record_acc_savings(tokens_saved: int):
    metrics.inc("acc_token_savings", tokens_saved)


def record_hallucination_report():
    metrics.inc("hallucination_reports")


def record_correction(accepted: bool):
    metrics.inc("correction_reports")
    if accepted:
        metrics.inc("correction_acceptances")


def record_rollback():
    metrics.inc("rollback_count")


def record_queue_backlog(length: int):
    metrics.set_gauge("queue_backlog", length)


def record_retrieval_failure():
    metrics.inc("retrieval_failures")


def get_evaluation_metrics() -> Dict[str, float]:
    snapshot = metrics.get_snapshot()
    counters = snapshot.get("counters", {})

    retrieval_hits = counters.get("retrieval_hits", 0)
    retrieval_misses = counters.get("retrieval_misses", 0)
    correction_acceptances = counters.get("correction_acceptances", 0)
    correction_reports = counters.get("correction_reports", 0)
    acc_token_savings = counters.get("acc_token_savings", 0)

    return {
        "retrieval_hit_rate": retrieval_hits / (retrieval_hits + retrieval_misses) if (retrieval_hits + retrieval_misses) > 0 else 0.0,
        "correction_success_rate": correction_acceptances / correction_reports if correction_reports > 0 else 0.0,
        "acc_token_savings": acc_token_savings,
    }
