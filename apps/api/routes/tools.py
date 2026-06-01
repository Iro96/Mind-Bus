from apps.api.fastapi_compat import APIRouter, Depends, HTTPException, status
from typing import Dict, Any, List
from tools import run_tool
from apps.api.security import get_current_user

router = APIRouter(prefix="/tools")

# Available tools configuration
AVAILABLE_TOOLS: List[Dict[str, Any]] = [
    {
        "id": "web_search",
        "name": "Web Search",
        "description": "Search the web for information",
        "category": "information",
        "enabled": True,
        "version": "1.0",
        "parameters": ["query", "max_results"]
    },
    {
        "id": "calculator",
        "name": "Calculator",
        "description": "Perform mathematical calculations",
        "category": "utility",
        "enabled": True,
        "version": "1.0",
        "parameters": ["expression"]
    },
    {
        "id": "file_read",
        "name": "File Read",
        "description": "Read content from a file",
        "category": "file_operations",
        "enabled": True,
        "version": "1.0",
        "parameters": ["file_path"]
    },
    {
        "id": "file_write",
        "name": "File Write",
        "description": "Write content to a file",
        "category": "file_operations",
        "enabled": True,
        "version": "1.0",
        "parameters": ["file_path", "content"]
    },
    {
        "id": "database_query",
        "name": "Database Query",
        "description": "Execute SQL queries",
        "category": "database",
        "enabled": False,
        "version": "1.0",
        "parameters": ["query"]
    },
    {
        "id": "api_call",
        "name": "API Call",
        "description": "Call external APIs",
        "category": "integration",
        "enabled": True,
        "version": "1.0",
        "parameters": ["url", "method", "headers", "body"]
    }
]

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
    
    if not _tools_state.get(name, False):
        raise HTTPException(status_code=403, detail="Tool is disabled")
    
    result = run_tool(name, args)
    return {"tool": name, "args": args, "result": result}
