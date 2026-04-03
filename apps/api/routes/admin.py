from fastapi import APIRouter, Depends
from ..schemas.base import BaseResponse
from apps.api.security import require_roles

router = APIRouter(prefix="/admin", dependencies=[Depends(require_roles(["admin"]))])

@router.post("/reindex")
async def reindex() -> BaseResponse:
    return BaseResponse(message="Reindex placeholder")

@router.post("/rebuild-memory")
async def rebuild_memory() -> BaseResponse:
    return BaseResponse(message="Rebuild memory placeholder")

@router.post("/rollback")
async def rollback() -> BaseResponse:
    return BaseResponse(message="Rollback placeholder")

@router.get("/health")
async def health() -> BaseResponse:
    return BaseResponse(message="Health check placeholder")

from observability.metrics import metrics as metrics_registry, get_evaluation_metrics


@router.get("/metrics")
async def metrics() -> dict:
    return {
        "metrics": metrics_registry.get_snapshot(),
        "evaluations": get_evaluation_metrics(),
    }