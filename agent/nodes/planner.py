import re

from ..state import AgentState

TOOL_KEYWORDS = {
    "calculate": "calculator",
    "compute": "calculator",
    "search": "web_search",
    "google": "web_search",
    "execute": "code_exec",
    "run": "code_exec",
}


def _strip_trigger(content: str, keyword: str) -> str:
    pattern = rf"^\s*(?:please\s+)?{re.escape(keyword)}\b[:\s-]*"
    cleaned = re.sub(pattern, "", content, flags=re.IGNORECASE).strip()
    return cleaned or content.strip()


def _extract_code(content: str, keyword: str) -> str:
    fenced_match = re.search(r"```(?:python)?\s*(.*?)```", content, flags=re.IGNORECASE | re.DOTALL)
    if fenced_match:
        return fenced_match.group(1).strip()
    cleaned = _strip_trigger(content, keyword)
    cleaned = re.sub(r"^\s*python\b[:\s-]*", "", cleaned, flags=re.IGNORECASE).strip()
    return cleaned or content.strip()


def _extract_fenced_content(content: str) -> str | None:
    fenced_match = re.search(r"```(?:[^\n`]*)\s*\n(.*?)```", content, flags=re.IGNORECASE | re.DOTALL)
    if fenced_match:
        return fenced_match.group(1).strip()
    return None


def _path_or_default(value: str) -> str:
    return value.strip().strip("\"'")


def _parse_file_command(raw_content: str) -> dict | None:
    trimmed = raw_content.strip()

    pattern = re.compile(r"^\s*(?:please\s+)?(?:read|show|open)\s+file\s+(?P<path>.+)$", re.IGNORECASE)
    match = pattern.match(trimmed)
    if match:
        return {"name": "file_system", "args": {"action": "read_text", "path": _path_or_default(match.group("path"))}}

    pattern = re.compile(r"^\s*(?:please\s+)?list\s+files\s+in\s+(?P<path>.+)$", re.IGNORECASE)
    match = pattern.match(trimmed)
    if match:
        return {"name": "file_system", "args": {"action": "list_dir", "path": _path_or_default(match.group("path"))}}

    pattern = re.compile(r"^\s*(?:please\s+)?show\s+folder\s+(?P<path>.+)$", re.IGNORECASE)
    match = pattern.match(trimmed)
    if match:
        return {"name": "file_system", "args": {"action": "list_dir", "path": _path_or_default(match.group("path"))}}

    pattern = re.compile(r"^\s*(?:please\s+)?show\s+folder\s+structure\s+(?P<path>.+)$", re.IGNORECASE)
    match = pattern.match(trimmed)
    if match:
        return {"name": "file_system", "args": {"action": "tree", "path": _path_or_default(match.group("path")), "max_depth": 4}}

    pattern = re.compile(r"^\s*(?:please\s+)?tree\s+(?P<path>.+)$", re.IGNORECASE)
    match = pattern.match(trimmed)
    if match:
        return {"name": "file_system", "args": {"action": "tree", "path": _path_or_default(match.group("path")), "max_depth": 4}}

    pattern = re.compile(r"^\s*(?:please\s+)?(?:get|resolve)\s+path\s+(?P<path>.+)$", re.IGNORECASE)
    match = pattern.match(trimmed)
    if match:
        return {"name": "file_system", "args": {"action": "resolve_path", "path": _path_or_default(match.group("path"))}}

    pattern = re.compile(r"^\s*(?:please\s+)?(?:create\s+folder|mkdir)\s+(?P<path>.+)$", re.IGNORECASE)
    match = pattern.match(trimmed)
    if match:
        return {"name": "file_system", "args": {"action": "make_dir", "path": _path_or_default(match.group("path"))}}

    pattern = re.compile(
        r"^\s*(?:please\s+)?(?:create|write)\s+file\s+(?P<path>.+?)(?:\s+with\s+content(?:\s*[:\-]?)?)?(?:\n|$)",
        re.IGNORECASE | re.DOTALL,
    )
    match = pattern.match(trimmed)
    if match:
        path = _path_or_default(match.group("path"))
        content = _extract_fenced_content(raw_content)
        if content is None:
            content = re.sub(r"^\s*(?:please\s+)?(?:create|write)\s+file\s+.*?\s+with\s+content\s*[:\-]?\s*", "", raw_content, flags=re.IGNORECASE | re.DOTALL).strip()
        if not content:
            return None
        return {"name": "file_system", "args": {"action": "write_text", "path": path, "content": content}}

    pattern = re.compile(
        r"^\s*(?:please\s+)?append\s+to\s+file\s+(?P<path>.+?)(?:\s+with\s+content(?:\s*[:\-]?)?)?(?:\n|$)",
        re.IGNORECASE | re.DOTALL,
    )
    match = pattern.match(trimmed)
    if match:
        path = _path_or_default(match.group("path"))
        content = _extract_fenced_content(raw_content)
        if content is None:
            content = re.sub(r"^\s*(?:please\s+)?append\s+to\s+file\s+.*?\s+with\s+content\s*[:\-]?\s*", "", raw_content, flags=re.IGNORECASE | re.DOTALL).strip()
        if not content:
            return None
        return {"name": "file_system", "args": {"action": "append_text", "path": path, "content": content}}

    pattern = re.compile(
        r'^\s*(?:please\s+)?replace\s+["\'](?P<old>.+?)["\']\s+with\s+["\'](?P<new>.+?)["\']\s+in\s+file\s+(?P<path>.+)$',
        re.IGNORECASE,
    )
    match = pattern.match(trimmed)
    if match:
        return {
            "name": "file_system",
            "args": {
                "action": "replace_text",
                "path": _path_or_default(match.group("path")),
                "old_text": match.group("old"),
                "new_text": match.group("new"),
            },
        }

    pattern = re.compile(r"^\s*(?:please\s+)?move\s+(?:file|folder)\s+(?P<src>.+?)\s+to\s+(?P<dest>.+)$", re.IGNORECASE)
    match = pattern.match(trimmed)
    if match:
        return {
            "name": "file_system",
            "args": {
                "action": "move_path",
                "path": _path_or_default(match.group("src")),
                "destination": _path_or_default(match.group("dest")),
            },
        }

    pattern = re.compile(r"^\s*(?:please\s+)?(?:delete|remove)\s+(?:file|folder)\s+(?P<path>.+)$", re.IGNORECASE)
    match = pattern.match(trimmed)
    if match:
        recursive = bool(re.search(r"\bfolder\b", trimmed, flags=re.IGNORECASE))
        return {"name": "file_system", "args": {"action": "delete_path", "path": _path_or_default(match.group("path")), "recursive": recursive}}

    return None


def planner(state: AgentState) -> AgentState:
    last_message = state["messages"][-1] if state["messages"] else {}
    if "content" in last_message:
        raw_content = last_message["content"]
        content = raw_content.lower()

        file_call = _parse_file_command(raw_content)
        if file_call is not None:
            state["current_task"] = "call_tool"
            state["tool_calls"] = [file_call]
            return state

        for keyword, tool_name in TOOL_KEYWORDS.items():
            if keyword in content:
                state["current_task"] = "call_tool"
                if tool_name == "calculator":
                    state["tool_calls"] = [{"name": "calculator", "args": {"expression": _strip_trigger(raw_content, keyword)}}]
                elif tool_name == "web_search":
                    state["tool_calls"] = [{"name": "web_search", "args": {"query": _strip_trigger(raw_content, keyword)}}]
                elif tool_name == "code_exec":
                    state["tool_calls"] = [{"name": "code_exec", "args": {"code": _extract_code(raw_content, keyword)}}]
                else:
                    state["tool_calls"] = [{"name": tool_name, "args": {}}]
                return state

        state["current_task"] = "respond"

    return state
