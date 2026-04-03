from ..state import AgentState

TOOL_KEYWORDS = {
    "calculate": "calculator",
    "compute": "calculator",
    "search": "web_search",
    "google": "web_search",
    "execute": "code_exec",
    "run": "code_exec",
}

def planner(state: AgentState) -> AgentState:
    # Basic planner: analyze messages and set current_task
    last_message = state["messages"][-1] if state["messages"] else {}
    if "content" in last_message:
        content = last_message["content"].lower()

        # Choose tool based on keyword
        for keyword, tool_name in TOOL_KEYWORDS.items():
            if keyword in content:
                state["current_task"] = "call_tool"
                if tool_name == "calculator":
                    state["tool_calls"] = [{"name": "calculator", "args": {"expression": content}}]
                elif tool_name == "web_search":
                    state["tool_calls"] = [{"name": "web_search", "args": {"query": content}}]
                elif tool_name == "code_exec":
                    state["tool_calls"] = [{"name": "code_exec", "args": {"code": content}}]
                else:
                    state["tool_calls"] = [{"name": tool_name, "args": {}}]
                return state

        # default response generation
        state["current_task"] = "respond"

    return state