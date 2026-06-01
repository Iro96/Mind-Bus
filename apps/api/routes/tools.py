from apps.api.fastapi_compat import APIRouter, Depends, HTTPException, status
from typing import Dict, Any, List
from tools import run_tool, TOOL_REGISTRY
from apps.api.security import get_current_user

router = APIRouter(prefix="/tools")

# Available tools configuration - derived from TOOL_REGISTRY
def _get_available_tools() -> List[Dict[str, Any]]:
    """Get available tools from registry."""
    tools_map = {
        "calculator": {
            "name": "Calculator",
            "description": "Perform mathematical calculations",
            "category": "utility",
            "version": "1.0",
            "parameters": ["expression"]
        },
        "web_search": {
            "name": "Web Search",
            "description": "Search the web for information",
            "category": "information",
            "version": "1.0",
            "parameters": ["query", "max_results"]
        },
        "code_exec": {
            "name": "Code Executor",
            "description": "Execute code snippets",
            "category": "execution",
            "version": "1.0",
            "parameters": ["code", "language"]
        }
    }
    
    return [
        {
            "id": tool_id,
            "enabled": True,
            **tools_map.get(tool_id, {
                "name": tool_id.title(),
                "description": f"Tool: {tool_id}",
                "category": "general",
                "version": "1.0",
                "parameters": []
            })
        }
        for tool_id in TOOL_REGISTRY.keys()
    ]

AVAILABLE_TOOLS: List[Dict[str, Any]] = _get_available_tools()
_tools_state = {tool["id"]: tool["enabled"] for tool in AVAILABLE_TOOLS}


@router.get("")
async def list_tools(user=Depends(get_current_user)) -> Dict[str, Any]:
    """List all available tools"""
    tools = [
        {**tool, "enabled": _tools_state.get(tool["id"], tool["enabled"])}
        for tool in AVAILABLE_TOOLS
    ]
    return {"tools": tools}


@router.patch("/{tool_id}")
async def toggle_tool(
    tool_id: str,
    payload: Dict[str, bool],
    user=Depends(get_current_user)
) -> Dict[str, Any]:
    """Enable or disable a tool"""
    if tool_id not in _tools_state:
        raise HTTPException(status_code=404, detail="Tool not found")
    
    enabled = payload.get("enabled", _tools_state[tool_id])
    _tools_state[tool_id] = enabled
    
    return {
        "tool_id": tool_id,
        "enabled": enabled,
        "message": f"Tool {'enabled' if enabled else 'disabled'}"
    }


@router.post("/run")
async def run_tool_endpoint(payload: Dict[str, Any], user=Depends(get_current_user)) -> Dict[str, Any]:
    name = payload.get("name")
    args = payload.get("args", {})
    if not name:
        return {"error": "Tool name is required"}
    
    if name not in TOOL_REGISTRY:
        raise HTTPException(status_code=404, detail=f"Tool '{name}' not found")
    
    if not _tools_state.get(name, False):
        raise HTTPException(status_code=403, detail="Tool is disabled")
    
    result = run_tool(name, args)
    return {"tool": name, "args": args, "result": result}
