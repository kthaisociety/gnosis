import secrets
import datetime
from fastapi import APIRouter, HTTPException, Depends, Header
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel

from lib.db.operations.api_keys import (
    create_api_key,
    list_api_keys,
    revoke_api_key,
    get_api_key,
)

from .utils import hash_key, get_admin_key
from .models import (
    APIKeyCreateRequest,
    APIKeyCreateResponse,
    APIKeyListResponse,
    APIKeyRevokeResponse,
)

router = APIRouter(prefix="/auth", tags=["Authentication"])
security = HTTPBearer(auto_error=False)


@router.post(
    "/keys",
    summary="Create an API key",
    response_model=APIKeyCreateResponse,
)
async def create_key(
    request: APIKeyCreateRequest,
    user_api_key: str = Header(..., alias="X-Admin-Key"),
):
    if user_api_key != get_admin_key():
        raise HTTPException(status_code=403, detail="Unauthorized")

    key = secrets.token_urlsafe(32)
    key_hash = hash_key(key)
    expires_at = None
    if request.expires_in_days:
        expires_at = datetime.datetime.utcnow() + datetime.timedelta(
            days=request.expires_in_days
        )
    row = create_api_key(request.name, key_hash, expires_at)
    return APIKeyCreateResponse(
        key=key,
        name=request.name,
        expires_at=expires_at,
    )


@router.get(
    "/keys",
    summary="List API keys",
    response_model=list[APIKeyListResponse],
)
async def list_keys(user_api_key: str = Header(..., alias="X-Admin-Key")):
    if user_api_key != get_admin_key():
        raise HTTPException(status_code=403, detail="Unauthorized")

    keys = list_api_keys()
    return [APIKeyListResponse(**k) for k in keys]


@router.delete(
    "/keys/{key_id}",
    summary="Revoke an API key",
    response_model=APIKeyRevokeResponse,
)
async def revoke_key(
    key_id: str,
    user_api_key: str = Header(..., alias="X-Admin-Key"),
) -> APIKeyRevokeResponse:
    if user_api_key != get_admin_key():
        raise HTTPException(status_code=403, detail="Unauthorized")
    revoke_api_key(key_id)
    return APIKeyRevokeResponse(status="success")


async def get_current_api_key(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    x_api_key: str = Header(None, alias="X-API-Key"),
) -> str:
    """Validate API key from Bearer token or X-API-Key header."""
    api_key = None

    # Try Bearer token first
    if credentials and credentials.credentials:
        api_key = credentials.credentials
    # Fall back to X-API-Key header
    elif x_api_key:
        api_key = x_api_key

    if not api_key:
        raise HTTPException(status_code=401, detail="API key required")

    key_hash = hash_key(api_key)
    get_api_key(key_hash)
    return api_key
