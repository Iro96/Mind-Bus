import logging
import threading
import uuid
import contextvars
from typing import Optional

request_id_var = contextvars.ContextVar("request_id", default=None)
thread_id_var = contextvars.ContextVar("thread_id", default=None)
model_version_var = contextvars.ContextVar("model_version", default=None)
prompt_version_var = contextvars.ContextVar("prompt_version", default=None)


class RequestContextFilter(logging.Filter):
    def filter(self, record):
        record.request_id = request_id_var.get() or "unknown"
        record.thread_id = thread_id_var.get() or threading.get_ident()
        record.model_version = model_version_var.get() or "unknown"
        record.prompt_version = prompt_version_var.get() or "unknown"
        return True


def init_logging(level: int = logging.INFO):
    formatter = logging.Formatter(
        "%(asctime)s %(levelname)s [request=%(request_id)s thread=%(thread_id)s] "
        "[model=%(model_version)s prompt=%(prompt_version)s] %(name)s: %(message)s"
    )
    handler = logging.StreamHandler()
    handler.setFormatter(formatter)

    root = logging.getLogger()
    root.setLevel(level)
    root.handlers = [handler]
    root.addFilter(RequestContextFilter())
    root.debug("Logging initialized")


def set_request_context(request_id: Optional[str] = None, thread_id: Optional[int] = None,
                        model_version: Optional[str] = None, prompt_version: Optional[str] = None):
    request_id_var.set(request_id or str(uuid.uuid4()))
    thread_id_var.set(thread_id or threading.get_ident())
    if model_version is not None:
        model_version_var.set(model_version)
    if prompt_version is not None:
        prompt_version_var.set(prompt_version)


def clear_request_context():
    request_id_var.set(None)
    thread_id_var.set(None)
    model_version_var.set(None)
    prompt_version_var.set(None)
