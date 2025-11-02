from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, Field

from app.schemas.base import ORMModel


class UserBasic(ORMModel):
    telegram_id: int
    username: Optional[str]
    first_name: Optional[str]
    photo_url: Optional[str]
    auth_date: Optional[datetime]
    role: str


class UserDetail(UserBasic):
    id: int
    balance_usd: float
    sent_mb: float
    used_mb: float
    notifications_enabled: bool
    session_notifications_enabled: bool
    system_notifications_enabled: bool
    last_seen: Optional[datetime]
    last_login_ip: Optional[str]
    last_login_device: Optional[str]
    two_factor_enabled: bool
    language: str
    single_device_mode: bool
    battery_saver: bool
    theme: str


class SettingsPayload(BaseModel):
    language: Optional[str] = Field(default=None)
    push_notifications: Optional[bool] = None
    session_updates: Optional[bool] = None
    system_updates: Optional[bool] = None
    single_device_mode: Optional[bool] = None
    battery_saver: Optional[bool] = None
    theme: Optional[str] = Field(default=None, pattern="^(light|dark)$")


class SettingsResponse(ORMModel):
    language: str
    push_notifications: bool
    session_updates: bool
    system_updates: bool
    single_device_mode: bool
    battery_saver: bool
    theme: str
    two_factor_enabled: bool
    updated_at: datetime


class LoginHistoryEntry(ORMModel):
    city: Optional[str]
    device: Optional[str]
    ip: Optional[str]
    time: datetime


class LoginHistoryResponse(ORMModel):
    history: List[LoginHistoryEntry]


class TokenRenewResponse(ORMModel):
    message: str
    jwt_token: str
    masked_token: str


class LogoutResponse(ORMModel):
    message: str

