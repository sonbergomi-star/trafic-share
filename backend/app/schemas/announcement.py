"""Announcement schemas."""

from datetime import datetime
from typing import Optional

from pydantic import BaseModel


class AnnouncementOut(BaseModel):
    id: int
    title: str
    description: str
    image_url: Optional[str]
    link: Optional[str]
    created_at: datetime
