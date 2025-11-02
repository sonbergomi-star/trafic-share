"""Support schemas."""

from datetime import datetime
from typing import Optional

from pydantic import BaseModel


class SupportCreateRequest(BaseModel):
    telegram_id: int
    subject: str
    message: str
    attachment_url: Optional[str] = None


class SupportItemResponse(BaseModel):
    id: int
    subject: str
    message: str
    status: str
    attachment_url: Optional[str]
    admin_reply: Optional[str]
    created_at: datetime
