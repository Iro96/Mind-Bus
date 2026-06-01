import logging
from uuid import UUID
from urllib.parse import quote
from apps.api.fastapi_compat import APIRouter, File, HTTPException, UploadFile, status, Depends
from apps.api.security import get_current_user
from ..schemas.base import BaseResponse

router = APIRouter()
logger = logging.getLogger(__name__)

# In-memory document store (replace with database in production)
_documents_store = {}
_document_counter = 0


def _sanitize_filename(filename: str) -> str:
    """Sanitize filename by removing control characters and properly encoding it."""
    # Remove control characters (ASCII < 0x20 and 0x7f)
    sanitized = ''.join(c for c in filename if ord(c) >= 0x20 and ord(c) != 0x7f)
    # Remove or escape problematic characters
    sanitized = sanitized.replace('"', '').replace(';', '').replace('\\', '')
    return sanitized.strip()


@router.post("/documents/upload")
async def upload_document(
    file: UploadFile = File(...),
    user: dict = Depends(get_current_user)
):
    global _document_counter
    
    if not file.filename:
        raise HTTPException(status_code=400, detail="No file selected")
    
    try:
        contents = await file.read()
        
        _document_counter += 1
        doc_id = f"doc_{_document_counter}"
        
        document = {
            "id": doc_id,
            "filename": file.filename,
            "size": len(contents),
            "content_type": file.content_type or "text/plain",
            "created_at": "2026-05-31T20:17:53Z",
            "user_id": str(user.get("user_id", ""))
        }
        
        _documents_store[doc_id] = {
            **document,
            "content": contents
        }
        
        return {"document": document}
    except Exception as e:
        logger.error(f"Error uploading document: {e}")
        raise HTTPException(status_code=500, detail="Failed to upload document") from e


@router.get("/documents")
async def list_documents(user: dict = Depends(get_current_user)):
    user_id = str(user.get("user_id", ""))
    documents = [
        {k: v for k, v in doc.items() if k != "content"}
        for doc in _documents_store.values()
        if doc.get("user_id") == user_id
    ]
    return {"documents": documents}


@router.get("/documents/{doc_id}/download")
async def download_document(doc_id: str, user: dict = Depends(get_current_user)):
    if doc_id not in _documents_store:
        raise HTTPException(status_code=404, detail="Document not found")
    
    doc = _documents_store[doc_id]
    if doc.get("user_id") != str(user.get("user_id", "")):
        raise HTTPException(status_code=403, detail="Unauthorized")
    
    from fastapi.responses import StreamingResponse
    import io
    
    sanitized_filename = _sanitize_filename(doc['filename'])
    quoted_filename = quote(sanitized_filename.encode('utf-8'), safe='')
    
    headers = {
        "Content-Disposition": f'attachment; filename="{sanitized_filename}"; filename*=UTF-8\'\'{quoted_filename}'
    }
    
    content = doc["content"]
    return StreamingResponse(
        iter([content]),
        media_type=doc["content_type"],
        headers=headers
    )


@router.delete("/documents/{doc_id}")
async def delete_document(doc_id: str, user: dict = Depends(get_current_user)):
    if doc_id not in _documents_store:
        raise HTTPException(status_code=404, detail="Document not found")
    
    doc = _documents_store[doc_id]
    if doc.get("user_id") != str(user.get("user_id", "")):
        raise HTTPException(status_code=403, detail="Unauthorized")
    
    del _documents_store[doc_id]
    return {"message": "Document deleted"}
