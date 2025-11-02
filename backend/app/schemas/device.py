"""Device registration schemas."""

from typing import Optional

from pydantic import BaseModel


class DeviceRegistrationRequest(BaseModel):
    telegram_id: int
    device_id: str
    device_token: str
    platform: str
    notifications_enabled: Optional[bool] = True
