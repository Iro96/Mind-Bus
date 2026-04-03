from fastapi import APIRouter
from ..schemas.base import BaseResponse

router = APIRouter()

@router.get("/memories")
async def get_memories() -> BaseResponse:
    return BaseResponse(message="Get memories placeholder")

@router.post("/memories/refresh")
async def refresh_memories() -> BaseResponse:
    return BaseResponse(message="Refresh memories placeholder")