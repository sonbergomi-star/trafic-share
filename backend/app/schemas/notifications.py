"""Notification schemas."""

from typing import Optional

from pydantic import BaseModel


class PushSendRequest(BaseModel):
    title: str
    body: str
    type: str
    data: Optional[dict] = None


class PushSendResponse(BaseModel):
    sent: int
    failed: int
