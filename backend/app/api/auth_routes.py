"""Firebase ID-token verification endpoints and shared authentication dependency."""

from typing import Any, Optional

from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from firebase_admin import auth

from app.models.request_models import TokenVerificationRequest
from app.models.response_models import AuthResponse
from app.services.firebase_service import initialize_firebase, save_user_profile

router = APIRouter(prefix="/api/auth", tags=["Authentication"])
bearer_scheme = HTTPBearer(auto_error=False)


def _verify_id_token(id_token: str) -> dict[str, Any]:
    initialize_firebase()
    try:
        claims = auth.verify_id_token(id_token, check_revoked=True)
    except (auth.InvalidIdTokenError, auth.ExpiredIdTokenError, auth.RevokedIdTokenError) as exc:
        raise HTTPException(status_code=401, detail="Invalid or expired Firebase ID token") from exc
    if claims.get("uid"):
        save_user_profile(claims["uid"], claims.get("name"), claims.get("email"))
    return claims


async def get_current_user(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(bearer_scheme),
) -> dict[str, Any]:
    if credentials is None or credentials.scheme.lower() != "bearer":
        raise HTTPException(status_code=401, detail="Firebase bearer token is required")

    claims = _verify_id_token(credentials.credentials)
    if not claims.get("uid"):
        raise HTTPException(status_code=401, detail="Firebase token does not contain a user ID")
    return claims


@router.post("/verify", response_model=AuthResponse)
async def verify_token(request: TokenVerificationRequest) -> AuthResponse:
    claims = _verify_id_token(request.id_token)
    return AuthResponse(
        success=True,
        user_id=claims["uid"],
        email=claims.get("email"),
    )