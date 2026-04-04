from langgraph.checkpoint.memory import MemorySaver

import agent.graph as graph_module


def test_create_checkpointer_uses_memory_saver_without_database_url(monkeypatch):
    monkeypatch.delenv("GRAPH_CHECKPOINT_BACKEND", raising=False)
    monkeypatch.delenv("DATABASE_URL", raising=False)

    checkpointer = graph_module._create_checkpointer()

    assert isinstance(checkpointer, MemorySaver)


def test_create_checkpointer_defaults_to_memory_backend(monkeypatch):
    monkeypatch.delenv("GRAPH_CHECKPOINT_BACKEND", raising=False)
    monkeypatch.setenv("DATABASE_URL", "postgresql://example.invalid:5432/db")

    def fail_connect():
        raise AssertionError("db.connect should not be called for the default memory backend")

    monkeypatch.setattr(graph_module.db, "connect", fail_connect)

    first = graph_module._create_checkpointer()
    second = graph_module._create_checkpointer()

    assert isinstance(first, MemorySaver)
    assert first is second


def test_create_checkpointer_falls_back_when_postgres_connect_fails(monkeypatch):
    monkeypatch.setenv("GRAPH_CHECKPOINT_BACKEND", "postgres")
    monkeypatch.setenv("DATABASE_URL", "postgresql://example.invalid:5432/db")

    def fail_connect():
        raise RuntimeError("database unavailable")

    monkeypatch.setattr(graph_module.db, "connect", fail_connect)

    checkpointer = graph_module._create_checkpointer()

    assert isinstance(checkpointer, MemorySaver)


def test_create_checkpointer_falls_back_when_postgres_saver_is_unsupported(monkeypatch):
    monkeypatch.setenv("GRAPH_CHECKPOINT_BACKEND", "postgres")
    monkeypatch.setenv("DATABASE_URL", "postgresql://example.invalid:5432/db")
    monkeypatch.setattr(graph_module, "_supports_postgres_checkpointer", lambda: False)
    monkeypatch.setattr(graph_module.db, "connect", lambda: None)

    checkpointer = graph_module._create_checkpointer()

    assert isinstance(checkpointer, MemorySaver)
