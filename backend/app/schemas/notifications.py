from datetime import datetime
from typing import Dict, Optional

from pydantic import BaseModel

from app.schemas.base import ORMModel


class DeviceRegisterPayload(BaseModel):
    telegram_id: int
    device_id: str
    device_token: str
    platform: str
    notifications_enabled: bool = True


class DeviceRegistrySchema(ORMModel):
    id: int
    telegram_id: int
    device_id: str
    platform: str
    device_token: str
    notifications_enabled: bool
    last_seen: Optional[datetime]
    updated_at: datetime


class PushNotificationPayload(BaseModel):
    title: str
    body: str
    type: str
    data: Optional[Dict[str, str]] = None


class NotificationDispatchResult(ORMModel):
    sent: int
    failed: int


class NotificationLogSchema(ORMModel):
    id: int
    telegram_id: int
    device_id: Optional[str]
    notif_type: str
    title: Optional[str]
    body: Optional[str]
    payload: Dict[str, str]
    sent_at: datetime
    delivered: bool
    opened: bool
    error: Optional[str]

