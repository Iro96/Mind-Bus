import contextvars
import logging
import time
import uuid
from contextlib import contextmanager

logger = logging.getLogger(__name__)

trace_id_var = contextvars.ContextVar("trace_id", default=None)
span_stack_var = contextvars.ContextVar("span_stack", default=[])


def new_trace_id():
    return str(uuid.uuid4())


def get_trace_id():
    return trace_id_var.get() or "unknown"


def get_span_stack():
    return span_stack_var.get() or []


@contextmanager
def trace_request(request_id: str = None):
    tid = new_trace_id() if request_id is None else request_id
    token = trace_id_var.set(tid)
    span_stack_var.set([])
    start = time.perf_counter()
    logger.debug("Trace started %s", tid)
    try:
        yield tid
    finally:
        duration = (time.perf_counter() - start) * 1000.0
        logger.debug("Trace ended %s %.2fms", tid, duration)
        trace_id_var.reset(token)
        span_stack_var.set([])


@contextmanager
def trace_span(name: str):
    parent_stack = get_span_stack()
    span = {"name": name, "start": time.perf_counter(), "parent": parent_stack[-1] if parent_stack else None}
    span_stack_var.set(parent_stack + [span])

    logger.debug("Span start %s (trace=%s)", name, get_trace_id())

    try:
        yield span
    finally:
        end = time.perf_counter()
        duration = (end - span["start"]) * 1000.0
        logger.debug("Span end %s (trace=%s %.2fms)", name, get_trace_id(), duration)
        stack = get_span_stack()[:-1]
        span_stack_var.set(stack)


def current_trace_metadata():
    return {
        "trace_id": get_trace_id(),
        "span_depth": len(get_span_stack()),
    }
