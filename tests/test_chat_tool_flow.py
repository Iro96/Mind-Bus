from tools import run_tool


def test_chat_tool_flow_calculator():
    result = run_tool("calculator", {"expression": "2 + 2"})
    assert result.get("result") == 4


def test_chat_tool_flow_web_search():
    # This is a live network call; we assert result structure
    result = run_tool("web_search", {"query": "Python programming"})
    assert result.get("tool") == "web_search"
    assert "results" in result


def test_chat_tool_flow_code_exec():
    result = run_tool("code_exec", {"code": "print(42)"})
    assert result.get("stdout").strip() == "42"