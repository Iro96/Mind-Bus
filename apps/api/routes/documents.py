from apps.api.fastapi_compat import APIRouter, File, HTTPException, UploadFile, status
from ..schemas.base import BaseResponse

router = APIRouter()

@router.post("/documents/upload")
async def upload_document(file: UploadFile = File(...)) -> BaseResponse:
    raise HTTPException(
        status_code=status.HTTP_501_NOT_IMPLEMENTED,
        detail="Document upload is not implemented in this beta",
    )
