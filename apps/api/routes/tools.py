from apps.api.fastapi_compat import APIRouter, Depends
from typing import Dict, Any
from tools import run_tool
from apps.api.security import get_current_user

router = APIRouter(prefix="/tools")

@router.post("/run")
async def run_tool_endpoint(payload: Dict[str, Any], user=Depends(get_current_user)) -> Dict[str, Any]:
    name = payload.get("name")
    args = payload.get("args", {})
    if not name:
        return {"error": "Tool name is required"}
    result = run_tool(name, args)
    return {"tool": name, "args": args, "result": result}
