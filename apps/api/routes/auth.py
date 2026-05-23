from apps.api.fastapi_compat import APIRouter, HTTPException
from apps.api.schemas.base import AuthTokenRequest, AuthTokenResponse
from apps.api.security import create_access_token
from apps.api.services.conversation_service import ConversationService

router = APIRouter(prefix="/auth")

@router.post("/token", response_model=AuthTokenResponse)
async def token(payload: AuthTokenRequest) -> AuthTokenResponse:
    if payload.password != "password":
        raise HTTPException(status_code=401, detail="Invalid credentials")

    roles = ["admin", "user"] if payload.username == "admin" else ["user"]
    user = ConversationService().upsert_demo_user(payload.username, roles)
    access_token = create_access_token(
        {
            "sub": payload.username,
            "user_id": user["id"],
            "roles": roles,
        }
    )
    return AuthTokenResponse(access_token=access_token, token_type="bearer")
