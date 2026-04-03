from fastapi import APIRouter, Depends
from typing import Dict, Any
from tools import run_tool
from apps.api.security import get_current_user
from apps.api.schemas.base import BaseResponse

router = APIRouter(prefix="/tools")

@router.post("/run")
async def run_tool_endpoint(payload: Dict[str, Any], user=Depends(get_current_user)) -> BaseResponse:
    name = payload.get("name")
    args = payload.get("args", {})
    if not name:
        return BaseResponse(message="Tool name is required")
    result = run_tool(name, args)
    return BaseResponse(message=str(result))
