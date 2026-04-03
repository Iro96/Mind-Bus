from langgraph.checkpoint.memory import MemorySaver

import agent.graph as graph_module


def test_create_checkpointer_uses_memory_saver_without_database_url(monkeypatch):
    monkeypatch.delenv("DATABASE_URL", raising=False)

    checkpointer = graph_module._create_checkpointer()

    assert isinstance(checkpointer, MemorySaver)


def test_create_checkpointer_falls_back_when_postgres_connect_fails(monkeypatch):
    monkeypatch.setenv("DATABASE_URL", "postgresql://example.invalid:5432/db")

    def fail_connect():
        raise RuntimeError("database unavailable")

    monkeypatch.setattr(graph_module.db, "connect", fail_connect)

    checkpointer = graph_module._create_checkpointer()

    assert isinstance(checkpointer, MemorySaver)
