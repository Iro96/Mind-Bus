from apps.api.services import queue_service


def test_enqueue_request_returns_empty_string_when_queue_is_unavailable(monkeypatch):
    class StubQueue:
        def enqueue(self, *_args, **_kwargs):
            raise RuntimeError("redis unavailable")

    monkeypatch.setattr(queue_service, "queue", StubQueue())

    def fail_enqueue(*_args, **_kwargs):
        raise RuntimeError("redis unavailable")

    monkeypatch.setattr(queue_service.queue, "enqueue", fail_enqueue)

    job_id = queue_service.enqueue_request({"type": "chat_analysis"})

    assert job_id == ""


def test_dispatch_request_processes_inline_when_queue_is_unavailable(monkeypatch):
    monkeypatch.setattr(queue_service, "enqueue_request", lambda payload, timeout=300: "")

    import worker.tasks as worker_tasks

    monkeypatch.setattr(worker_tasks, "process_task", lambda payload: {"status": "ok", "payload": payload})

    result = queue_service.dispatch_request({"type": "chat_analysis", "message": "hello"})

    assert result["mode"] == "inline"
    assert result["result"]["status"] == "ok"
