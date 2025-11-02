"""Authentication schemas."""

from typing import Optional

from pydantic import BaseModel, Field


class TelegramAuthRequest(BaseModel):
    """Payload from Telegram login widget."""

    id: int
    username: Optional[str] = None
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    photo_url: Optional[str] = None
    auth_date: int
    hash: str


class TokenResponse(BaseModel):
    """JWT token response."""

    access_token: str
    refresh_token: str
    token_type: str = "bearer"


class TelegramAuthResponse(BaseModel):
    """Response after successful Telegram authentication."""

    status: str = Field(default="success")
    user: dict
    token: TokenResponse


class TokenRenewResponse(BaseModel):
    """New token on renewal."""

    message: str
    token: TokenResponse
