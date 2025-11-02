"""User schemas."""

from datetime import datetime
from typing import Optional

from pydantic import BaseModel


class UserBase(BaseModel):
    telegram_id: int
    username: Optional[str]
    first_name: Optional[str]
    photo_url: Optional[str]


class ProfileResponse(UserBase):
    auth_date: Optional[datetime]
    jwt_token: Optional[str]
    two_factor_enabled: bool
    last_login_ip: Optional[str]
    last_login_device: Optional[str]


class LoginHistoryItem(BaseModel):
    city: Optional[str]
    device: Optional[str]
    time: datetime


class TokenRenewResponse(BaseModel):
    message: str
    access_token: str
    refresh_token: str
