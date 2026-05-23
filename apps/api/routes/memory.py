from apps.api.fastapi_compat import APIRouter, HTTPException, status
from ..schemas.base import BaseResponse

router = APIRouter()

@router.get("/memories")
async def get_memories() -> BaseResponse:
    raise HTTPException(
        status_code=status.HTTP_501_NOT_IMPLEMENTED,
        detail="Memory listing is not implemented in this beta",
    )

@router.post("/memories/refresh")
async def refresh_memories() -> BaseResponse:
    raise HTTPException(
        status_code=status.HTTP_501_NOT_IMPLEMENTED,
        detail="Memory refresh is not implemented in this beta",
    )
