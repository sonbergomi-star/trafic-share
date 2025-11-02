from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel

from app.schemas.base import ORMModel


class AnnouncementSchema(ORMModel):
    id: int
    title: str
    description: str
    image_url: Optional[str]
    link: Optional[str]
    created_at: datetime


class PromoCodeSchema(ORMModel):
    id: int
    code: str
    bonus_percent: float
    expires_at: Optional[datetime]
    is_active: bool
    description: Optional[str]


class NewsPromoResponse(ORMModel):
    telegram_links: dict
    announcements: List[AnnouncementSchema]
    promo: List[PromoCodeSchema]


class PromoActivatePayload(BaseModel):
    user_id: int
    code: str


class PromoActivateResponse(ORMModel):
    status: str
    message: str

