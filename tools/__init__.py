from typing import Any, Dict
from .calculator import calculator_tool
from .web_search import web_search_tool
from .code_exec import code_exec_tool

TOOL_REGISTRY = {
    "calculator": calculator_tool,
    "web_search": web_search_tool,
    "code_exec": code_exec_tool,
}


def run_tool(name: str, args: Dict[str, Any]) -> Dict[str, Any]:
    tool = TOOL_REGISTRY.get(name)
    if not tool:
        return {"error": f"Tool '{name}' not found"}
    return tool(args)
