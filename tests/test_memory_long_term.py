import uuid

from memory.long_term import LongTermMemoryManager
from memory.schemas import SemanticMemory


def _memory_row(*, user_id, thread_id, memory_id=None, key="user_preference_python", evidence_count=1):
    return {
        "id": str(memory_id or uuid.uuid4()),
        "user_id": str(user_id),
        "thread_id": str(thread_id) if thread_id else None,
        "memory_type": "semantic",
        "key": key,
        "value_json": {
            "fact": "User prefers Python for scripting tasks",
            "provenance": "Observed in conversation",
            "evidence_count": evidence_count,
        },
        "confidence": 0.5,
        "source_type": "conversation",
        "source_id": None,
        "created_at": None,
        "updated_at": None,
        "expires_at": None,
        "status": "active",
    }


def test_retrieve_memories_filters_by_thread_id(monkeypatch):
    manager = LongTermMemoryManager()
    user_id = uuid.uuid4()
    thread_id = uuid.uuid4()
    recorded = {}

    def fake_execute(query, params=None):
        recorded["query"] = query
        recorded["params"] = params
        return [_memory_row(user_id=user_id, thread_id=thread_id)]

    from memory import long_term as long_term_module

    monkeypatch.setattr(long_term_module.db, "execute", fake_execute)

    result = manager.retrieve_memories(user_id=user_id, thread_id=thread_id, limit=25)

    assert len(result) == 1
    assert "thread_id = %s" in recorded["query"]
    assert recorded["params"][0] == str(user_id)
    assert recorded["params"][1] == str(thread_id)
    assert recorded["params"][-1] == 25
    assert result[0].thread_id == thread_id


def test_upsert_memory_updates_existing_record_by_identity(monkeypatch):
    manager = LongTermMemoryManager()
    user_id = uuid.uuid4()
    thread_id = uuid.uuid4()
    existing_id = uuid.uuid4()
    existing_memory = SemanticMemory(
        id=existing_id,
        user_id=user_id,
        thread_id=thread_id,
        key="user_preference_python",
        value_json={"fact": "Old preference", "evidence_count": 1},
        confidence=0.1,
        source_type="conversation",
        status="active",
    )
    incoming_memory = SemanticMemory(
        user_id=user_id,
        thread_id=thread_id,
        key="user_preference_python",
        value_json={"fact": "Updated preference", "evidence_count": 2},
        confidence=0.3,
        source_type="conversation",
        status="active",
    )
    recorded = {}

    monkeypatch.setattr(manager, "find_memory", lambda **_kwargs: existing_memory)

    def fake_update_memory(memory_id, updates):
        recorded["memory_id"] = memory_id
        recorded["updates"] = updates
        return True

    monkeypatch.setattr(manager, "update_memory", fake_update_memory)
    monkeypatch.setattr(manager, "store_memory", lambda *_args, **_kwargs: (_ for _ in ()).throw(AssertionError("store_memory should not be called")))

    action, memory_id = manager.upsert_memory(incoming_memory)

    assert action == "updated"
    assert memory_id == existing_id
    assert recorded["memory_id"] == existing_id
    assert recorded["updates"]["value_json"]["fact"] == "Updated preference"
    assert recorded["updates"]["confidence"] == 0.3
