from agent.nodes.planner import planner


def test_planner_strips_calculator_trigger():
    state = {"messages": [{"role": "user", "content": "calculate 2 + 2"}], "tool_calls": []}

    result = planner(state)

    assert result["tool_calls"][0]["name"] == "calculator"
    assert result["tool_calls"][0]["args"]["expression"] == "2 + 2"


def test_planner_strips_search_trigger():
    state = {"messages": [{"role": "user", "content": "search latest python release"}], "tool_calls": []}

    result = planner(state)

    assert result["tool_calls"][0]["name"] == "web_search"
    assert result["tool_calls"][0]["args"]["query"] == "latest python release"


def test_planner_extracts_fenced_code():
    state = {
        "messages": [
            {
                "role": "user",
                "content": "run python ```python\nprint(42)\n```",
            }
        ],
        "tool_calls": [],
    }

    result = planner(state)

    assert result["tool_calls"][0]["name"] == "code_exec"
    assert result["tool_calls"][0]["args"]["code"] == "print(42)"
