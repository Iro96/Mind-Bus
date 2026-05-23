import os

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
    previous = os.environ.get("ENABLE_CODE_EXEC")
    os.environ["ENABLE_CODE_EXEC"] = "1"
    result = run_tool("code_exec", {"code": "print(42)"})
    assert result.get("stdout", "").strip() == "42"
    if previous is None:
        os.environ.pop("ENABLE_CODE_EXEC", None)
    else:
        os.environ["ENABLE_CODE_EXEC"] = previous


def test_chat_tool_flow_code_exec_disabled_by_default(monkeypatch):
    monkeypatch.delenv("ENABLE_CODE_EXEC", raising=False)

    result = run_tool("code_exec", {"code": "print(42)"})

    assert result.get("available") is False
    assert result.get("tool") == "code_exec"
