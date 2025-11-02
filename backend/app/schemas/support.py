from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel

from app.schemas.base import ORMModel


class SupportRequestPayload(BaseModel):
    telegram_id: int
    subject: str
    message: str
    attachment_url: Optional[str] = None


class SupportRequestSchema(ORMModel):
    id: int
    telegram_id: int
    subject: str
    message: str
    attachment_url: Optional[str]
    status: str
    admin_reply: Optional[str]
    reply_at: Optional[datetime]
    created_at: datetime
    updated_at: datetime


class SupportHistoryResponse(ORMModel):
    items: List[SupportRequestSchema]

