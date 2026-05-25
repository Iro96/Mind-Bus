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


def test_planner_routes_read_file_requests():
    state = {"messages": [{"role": "user", "content": "read file README.md"}], "tool_calls": []}

    result = planner(state)

    assert result["tool_calls"][0] == {"name": "file_system", "args": {"action": "read_text", "path": "README.md"}}


def test_planner_routes_list_and_tree_requests():
    state = {"messages": [{"role": "user", "content": "show folder docs"}], "tool_calls": []}

    result = planner(state)

    assert result["tool_calls"][0] == {"name": "file_system", "args": {"action": "list_dir", "path": "docs"}}

    state = {"messages": [{"role": "user", "content": "show folder structure src"}], "tool_calls": []}
    result = planner(state)

    assert result["tool_calls"][0] == {"name": "file_system", "args": {"action": "tree", "path": "src", "max_depth": 4}}


def test_planner_routes_resolve_and_directory_commands():
    state = {"messages": [{"role": "user", "content": "get path ./tests"}], "tool_calls": []}
    result = planner(state)
    assert result["tool_calls"][0] == {"name": "file_system", "args": {"action": "resolve_path", "path": "./tests"}}

    state = {"messages": [{"role": "user", "content": "mkdir build/output"}], "tool_calls": []}
    result = planner(state)
    assert result["tool_calls"][0] == {"name": "file_system", "args": {"action": "make_dir", "path": "build/output"}}


def test_planner_routes_write_and_append_with_fenced_content():
    state = {
        "messages": [
            {
                "role": "user",
                "content": "write file notes.txt\n```\nhello\n```",
            }
        ],
        "tool_calls": [],
    }
    result = planner(state)
    assert result["tool_calls"][0] == {
        "name": "file_system",
        "args": {"action": "write_text", "path": "notes.txt", "content": "hello"},
    }

    state = {
        "messages": [
            {
                "role": "user",
                "content": "append to file notes.txt\n```\nworld\n```",
            }
        ],
        "tool_calls": [],
    }
    result = planner(state)
    assert result["tool_calls"][0] == {
        "name": "file_system",
        "args": {"action": "append_text", "path": "notes.txt", "content": "world"},
    }


def test_planner_routes_replace_and_move_and_delete():
    state = {"messages": [{"role": "user", "content": 'replace "old" with "new" in file notes.txt'}], "tool_calls": []}
    result = planner(state)
    assert result["tool_calls"][0] == {
        "name": "file_system",
        "args": {"action": "replace_text", "path": "notes.txt", "old_text": "old", "new_text": "new"},
    }

    state = {"messages": [{"role": "user", "content": "move file src/a.txt to dst/b.txt"}], "tool_calls": []}
    result = planner(state)
    assert result["tool_calls"][0] == {
        "name": "file_system",
        "args": {"action": "move_path", "path": "src/a.txt", "destination": "dst/b.txt"},
    }

    state = {"messages": [{"role": "user", "content": "delete folder build"}], "tool_calls": []}
    result = planner(state)
    assert result["tool_calls"][0] == {
        "name": "file_system",
        "args": {"action": "delete_path", "path": "build", "recursive": True},
    }
