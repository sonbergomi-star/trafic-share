"""News and promo service."""

from datetime import datetime

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import Announcement, PromoCode


class NewsService:
    """Provide news feed and promo operations."""

    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def get_feed(self) -> dict:
        announcements_stmt = select(Announcement).order_by(Announcement.created_at.desc()).limit(20)
        promos_stmt = select(PromoCode).where(PromoCode.is_active.is_(True))
        announcements = (await self.session.execute(announcements_stmt)).scalars().all()
        promos = (await self.session.execute(promos_stmt)).scalars().all()
        return {
            "announcements": [
                {
                    "id": item.id,
                    "title": item.title,
                    "description": item.description,
                    "image_url": item.image_url,
                    "link": item.link,
                    "created_at": item.created_at,
                }
                for item in announcements
            ],
            "promo": [
                {
                    "code": promo.code,
                    "bonus_percent": float(promo.bonus_percent),
                    "expires_at": promo.expires_at,
                    "is_active": promo.is_active,
                }
                for promo in promos
            ],
            "telegram_links": {
                "channel": "https://t.me/project_news",
                "chat": "https://t.me/project_chat",
            },
        }
