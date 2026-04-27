from pydantic import BaseModel
from typing import Optional
import datetime


class AuthResponse(BaseModel):
    status: str


class APIKeyCreateRequest(BaseModel):
    name: str
    expires_in_days: Optional[int] = None


class APIKeyCreateResponse(BaseModel):
    key: str
    name: str
    expires_at: Optional[datetime.datetime] = None


class APIKeyListResponse(BaseModel):
    id: str
    name: str
    created_at: datetime.datetime
    expires_at: Optional[datetime.datetime] = None
    last_used_at: Optional[datetime.datetime] = None
    is_active: bool


class APIKeyRevokeResponse(BaseModel):
    status: str
