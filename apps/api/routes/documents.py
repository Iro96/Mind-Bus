from fastapi import APIRouter, UploadFile, File
from ..schemas.base import BaseResponse

router = APIRouter()

@router.post("/documents/upload")
async def upload_document(file: UploadFile = File(...)) -> BaseResponse:
    return BaseResponse(message="Upload document placeholder")