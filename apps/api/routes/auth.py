from fastapi import APIRouter, HTTPException
from apps.api.schemas.base import BaseResponse
from apps.api.security import create_access_token

router = APIRouter(prefix="/auth")

# In a real app, replace with db user check.

@router.post("/token")
async def token(username: str, password: str):
    if username != "admin" or password != "password":
        raise HTTPException(status_code=401, detail="Invalid credentials")

    token = create_access_token({"sub": username, "roles": ["admin", "user"]})
    return {"access_token": token, "token_type": "bearer"}
