from datetime import datetime
from typing import Optional

from pydantic import BaseModel

from app.schemas.base import ORMModel


class TelegramAuthPayload(BaseModel):
    id: int
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    username: Optional[str] = None
    photo_url: Optional[str] = None
    auth_date: int
    hash: str


class AuthToken(ORMModel):
    access_token: str
    token_type: str = "bearer"
    expires_in: int


class UserProfile(ORMModel):
    id: int
    telegram_id: int
    username: Optional[str]
    first_name: Optional[str]
    photo_url: Optional[str]
    auth_date: Optional[datetime]
    balance_usd: float
    sent_mb: float
    used_mb: float


class AuthResponse(ORMModel):
    status: str = "success"
    user: UserProfile
    token: str


class TokenPayload(BaseModel):
    telegram_id: int
    username: Optional[str] = None
    role: str = "user"
    exp: int

