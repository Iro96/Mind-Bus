from apps.api.fastapi_compat import APIRouter, Depends, HTTPException, status
from ..schemas.base import BaseResponse
from apps.api.security import require_roles

router = APIRouter(prefix="/admin", dependencies=[Depends(require_roles(["admin"]))])

@router.post("/reindex")
async def reindex() -> BaseResponse:
    raise HTTPException(
        status_code=status.HTTP_501_NOT_IMPLEMENTED,
        detail="Reindex is not implemented in this beta",
    )

@router.post("/rebuild-memory")
async def rebuild_memory() -> BaseResponse:
    raise HTTPException(
        status_code=status.HTTP_501_NOT_IMPLEMENTED,
        detail="Memory rebuild is not implemented in this beta",
    )

@router.post("/rollback")
async def rollback() -> BaseResponse:
    raise HTTPException(
        status_code=status.HTTP_501_NOT_IMPLEMENTED,
        detail="Rollback is not implemented in this beta",
    )

@router.get("/health")
async def health() -> BaseResponse:
    return BaseResponse(message="ok")

from observability.metrics import metrics as metrics_registry, get_evaluation_metrics


@router.get("/metrics")
async def metrics() -> dict:
    return {
        "metrics": metrics_registry.get_snapshot(),
        "evaluations": get_evaluation_metrics(),
    }
