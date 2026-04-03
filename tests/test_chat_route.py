import asyncio
import uuid

from fastapi import BackgroundTasks

from apps.api.routes import chat as chat_route
from apps.api.schemas.base import ChatRequest


class StubGraph:
    def __init__(self, response: str):
        self.response = response
        self.calls = []

    def invoke(self, state, config=None):
        self.calls.append((state, config))
        return {"final_response": self.response}


def test_chat_endpoint_invokes_graph_with_explicit_thread_id(monkeypatch):
    graph = StubGraph("stubbed response")
    enqueued = {}

    def fake_enqueue(payload, timeout=300):
        enqueued["payload"] = payload
        enqueued["timeout"] = timeout
        return "job-1"

    monkeypatch.setattr(chat_route, "create_graph", lambda: graph)
    monkeypatch.setattr(chat_route, "enqueue_request", fake_enqueue)
    monkeypatch.setattr(chat_route, "record_request_latency", lambda *_args: None)
    monkeypatch.setattr(chat_route, "get_request_id", lambda: "req-123")

    thread_id = uuid.UUID("00000000-0000-0000-0000-000000000123")
    background_tasks = BackgroundTasks()

    response = asyncio.run(
        chat_route.chat_endpoint(
            ChatRequest(message="hello world", thread_id=thread_id),
            background_tasks,
        )
    )

    assert response.message == "stubbed response"
    assert graph.calls[0][1] == {"configurable": {"thread_id": str(thread_id)}}
    assert graph.calls[0][0]["current_user_message"] == "hello world"

    asyncio.run(background_tasks())
    assert enqueued["payload"]["request_id"] == "req-123"
    assert enqueued["payload"]["thread_id"] == str(thread_id)


def test_chat_endpoint_defaults_thread_id_to_request_id(monkeypatch):
    graph = StubGraph("stubbed response")

    monkeypatch.setattr(chat_route, "create_graph", lambda: graph)
    monkeypatch.setattr(chat_route, "enqueue_request", lambda payload, timeout=300: "job-1")
    monkeypatch.setattr(chat_route, "record_request_latency", lambda *_args: None)
    monkeypatch.setattr(chat_route, "get_request_id", lambda: "req-456")

    response = asyncio.run(
        chat_route.chat_endpoint(
            ChatRequest(message="hello again"),
            BackgroundTasks(),
        )
    )

    assert response.message == "stubbed response"
    assert graph.calls[0][1] == {"configurable": {"thread_id": "req-456"}}
