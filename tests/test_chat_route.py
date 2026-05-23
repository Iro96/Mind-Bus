import asyncio
import uuid

import pytest

from apps.api.fastapi_compat import BackgroundTasks, HTTPException
from apps.api.routes import chat as chat_route
from apps.api.schemas.base import ChatRequest


class StubGraph:
    def __init__(self, response: str):
        self.response = response
        self.calls = []

    def invoke(self, state, config=None):
        self.calls.append((state, config))
        return {"final_response": self.response}


class StubConversationService:
    def __init__(self, thread_id=None, missing_thread=False):
        self.thread_id = thread_id or str(uuid.uuid4())
        self.missing_thread = missing_thread
        self.added_messages = []
        self.history = []

    def get_or_create_thread(self, user_id, requested_thread_id, title_hint):
        if self.missing_thread:
            raise KeyError("thread_not_found")
        return {
            "id": str(requested_thread_id or self.thread_id),
            "user_id": str(user_id),
            "session_id": str(uuid.uuid4()),
            "title": title_hint,
            "status": "active",
        }

    def add_message(self, thread_id, role, content, metadata=None):
        message = {
            "id": str(uuid.uuid4()),
            "thread_id": str(thread_id),
            "role": role,
            "content": content,
            "metadata": metadata or {},
        }
        self.added_messages.append(message)
        self.history.append(message)
        return message

    def build_state_messages(self, user_id, thread_id):
        return [{"role": item["role"], "content": item["content"]} for item in self.history]

    def list_thread_messages(self, user_id, thread_id):
        if self.missing_thread:
            raise KeyError("thread_not_found")
        return self.history


def test_chat_endpoint_invokes_graph_with_explicit_thread_id(monkeypatch):
    graph = StubGraph("stubbed response")
    enqueued = {}
    service = StubConversationService()

    def fake_dispatch(payload, timeout=300):
        enqueued["payload"] = payload
        enqueued["timeout"] = timeout
        return {"mode": "queue", "job_id": "job-1"}

    monkeypatch.setattr(chat_route, "conversation_service", service)
    monkeypatch.setattr(chat_route.agent, "create_graph", lambda: graph)
    monkeypatch.setattr(chat_route, "dispatch_request", fake_dispatch)
    monkeypatch.setattr(chat_route, "record_request_latency", lambda *_args: None)
    monkeypatch.setattr(chat_route, "get_request_id", lambda: "req-123")

    thread_id = uuid.UUID("00000000-0000-0000-0000-000000000123")
    user_id = str(uuid.uuid4())
    background_tasks = BackgroundTasks()

    response = asyncio.run(
        chat_route.chat_endpoint(
            ChatRequest(message="hello world", thread_id=thread_id),
            background_tasks,
            user={"user_id": user_id, "roles": ["user"]},
        )
    )

    assert response.message == "stubbed response"
    assert response.thread_id == thread_id
    assert graph.calls[0][1] == {"configurable": {"thread_id": str(thread_id)}}
    assert graph.calls[0][0]["current_user_message"] == "hello world"
    assert [item["role"] for item in service.added_messages] == ["user", "assistant"]

    asyncio.run(background_tasks())
    assert enqueued["payload"]["request_id"] == "req-123"
    assert enqueued["payload"]["thread_id"] == str(thread_id)
    assert enqueued["payload"]["user_id"] == user_id


def test_chat_endpoint_auto_provisions_thread_when_missing(monkeypatch):
    graph = StubGraph("stubbed response")
    auto_thread_id = uuid.uuid4()
    service = StubConversationService(thread_id=str(auto_thread_id))

    monkeypatch.setattr(chat_route, "conversation_service", service)
    monkeypatch.setattr(chat_route.agent, "create_graph", lambda: graph)
    monkeypatch.setattr(chat_route, "dispatch_request", lambda payload, timeout=300: {"mode": "inline"})
    monkeypatch.setattr(chat_route, "record_request_latency", lambda *_args: None)
    monkeypatch.setattr(chat_route, "get_request_id", lambda: "req-456")

    response = asyncio.run(
        chat_route.chat_endpoint(
            ChatRequest(message="hello again"),
            BackgroundTasks(),
            user={"user_id": str(uuid.uuid4()), "roles": ["user"]},
        )
    )

    assert response.message == "stubbed response"
    assert response.thread_id == auto_thread_id
    assert graph.calls[0][1] == {"configurable": {"thread_id": str(auto_thread_id)}}


def test_chat_endpoint_rejects_unknown_thread(monkeypatch):
    service = StubConversationService(missing_thread=True)

    monkeypatch.setattr(chat_route, "conversation_service", service)

    with pytest.raises(HTTPException) as exc_info:
        asyncio.run(
            chat_route.chat_endpoint(
                ChatRequest(message="hello", thread_id=uuid.uuid4()),
                BackgroundTasks(),
                user={"user_id": str(uuid.uuid4()), "roles": ["user"]},
            )
        )

    assert exc_info.value.status_code == 404


def test_get_thread_returns_persisted_messages(monkeypatch):
    service = StubConversationService()
    service.history = [
        {
            "id": str(uuid.uuid4()),
            "thread_id": service.thread_id,
            "role": "user",
            "content": "hello",
            "metadata": {},
        },
        {
            "id": str(uuid.uuid4()),
            "thread_id": service.thread_id,
            "role": "assistant",
            "content": "hi there",
            "metadata": {},
        },
    ]

    monkeypatch.setattr(chat_route, "conversation_service", service)

    response = asyncio.run(
        chat_route.get_thread(
            uuid.UUID(service.thread_id),
            user={"user_id": str(uuid.uuid4()), "roles": ["user"]},
        )
    )

    assert response.thread_id == uuid.UUID(service.thread_id)
    assert [message.role for message in response.messages] == ["user", "assistant"]
