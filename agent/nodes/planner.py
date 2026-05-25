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


def planner(state: AgentState) -> AgentState:
    # Basic planner: analyze messages and set current_task
    last_message = state["messages"][-1] if state["messages"] else {}
    if "content" in last_message:
        raw_content = last_message["content"]
        content = raw_content.lower()

        # Choose tool based on keyword
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

        # default response generation
        state["current_task"] = "respond"

    return state
