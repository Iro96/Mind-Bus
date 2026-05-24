import agent.graph as graph_module
from agent.langgraph_compat import MemorySaver
from agent.nodes.reflector import reflector


def _base_state():
    return {
        "messages": [{"role": "user", "content": "help me"}],
        "current_task": None,
        "current_user_message": "help me",
        "tool_calls": [],
        "tool_results": [],
        "retry_count": 0,
        "final_response": None,
        "retrieved_passages": [],
        "compact_context": "",
    }


def test_reflector_marks_successful_tool_results_ready():
    state = _base_state()
    state["tool_results"] = [{"tool": "calculator", "expression": "2 + 2", "result": 4}]
    state["last_tool_calls"] = [{"name": "calculator", "args": {"expression": "2 + 2"}}]
    state["compact_context"] = "user_message: help me"

    updated = reflector(state)

    assert updated["current_task"] == "respond"
    assert updated["tool_calls"] == []
    assert updated["reflection"]["status"] == "ready"
    assert "calculator result: 4" in updated["response_context"]


def test_reflector_retries_retryable_tool_failures():
    state = _base_state()
    state["tool_results"] = [
        {
            "tool": "web_search",
            "query": "python",
            "results": [],
            "error": "network unavailable",
        }
    ]
    state["last_tool_calls"] = [{"name": "web_search", "args": {"query": "python"}}]

    updated = reflector(state)

    assert updated["current_task"] == "call_tool"
    assert updated["retry_count"] == 1
    assert updated["tool_calls"] == [{"name": "web_search", "args": {"query": "python"}}]
    assert updated["reflection"]["status"] == "retrying_tools"
    assert updated["reflection"]["retry_planned"] is True


def test_reflector_does_not_retry_non_retryable_tool_failures():
    state = _base_state()
    state["tool_results"] = [
        {
            "tool": "code_exec",
            "code": "print(42)",
            "available": False,
            "error": "code execution is disabled",
        }
    ]
    state["last_tool_calls"] = [{"name": "code_exec", "args": {"code": "print(42)"}}]

    updated = reflector(state)

    assert updated["current_task"] == "respond"
    assert updated["tool_calls"] == []
    assert updated["reflection"]["status"] == "tool_failures"
    assert updated["reflection"]["retry_planned"] is False


def test_create_graph_routes_through_reflector_before_responder(monkeypatch):
    calls = []

    monkeypatch.setattr(graph_module, "_create_checkpointer", lambda: MemorySaver())

    def planner(state):
        calls.append("planner")
        return state

    def retriever(state):
        calls.append("retriever")
        return state

    def compressor(state):
        calls.append("compressor")
        state["tool_calls"] = []
        return state

    def tool_runner(state):
        calls.append("tool_runner")
        return state

    def reflector_node(state):
        calls.append("reflector")
        state["tool_calls"] = []
        return state

    def responder(state):
        calls.append("responder")
        state["final_response"] = "done"
        return state

    monkeypatch.setattr(graph_module, "planner", planner)
    monkeypatch.setattr(graph_module, "retriever", retriever)
    monkeypatch.setattr(graph_module, "compressor", compressor)
    monkeypatch.setattr(graph_module, "tool_runner", tool_runner)
    monkeypatch.setattr(graph_module, "reflector", reflector_node)
    monkeypatch.setattr(graph_module, "responder", responder)

    graph = graph_module.create_graph()
    result = graph.invoke(
        _base_state(),
        config={"configurable": {"thread_id": "test-thread"}},
    )

    assert result["final_response"] == "done"
    assert calls == ["planner", "retriever", "compressor", "reflector", "responder"]
