from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, desc
from datetime import datetime

from app.core.database import get_db
from app.models.announcement import Announcement, PromoCode


router = APIRouter()


@router.get("/announcements")
async def get_announcements(db: AsyncSession = Depends(get_db)):
    """
    Get all active announcements
    """
    result = await db.execute(
        select(Announcement)
        .where(Announcement.is_active == True)
        .order_by(desc(Announcement.created_at))
        .limit(10)
    )
    announcements = result.scalars().all()
    
    return {
        "announcements": [
            {
                "id": a.id,
                "title": a.title,
                "description": a.description,
                "image_url": a.image_url,
                "link": a.link,
                "created_at": a.created_at.isoformat(),
            }
            for a in announcements
        ]
    }


@router.get("/promo")
async def get_promo_codes(db: AsyncSession = Depends(get_db)):
    """
    Get active promo codes
    """
    result = await db.execute(
        select(PromoCode)
        .where(PromoCode.is_active == True)
        .where((PromoCode.expires_at == None) | (PromoCode.expires_at > datetime.utcnow()))
    )
    promos = result.scalars().all()
    
    return {
        "promo_codes": [
            {
                "id": p.id,
                "code": p.code,
                "bonus_percent": p.bonus_percent,
                "bonus_amount_usd": p.bonus_amount_usd,
                "description": p.description,
                "expires_at": p.expires_at.isoformat() if p.expires_at else None,
            }
            for p in promos
        ]
    }


@router.get("/telegram_links")
async def get_telegram_links():
    """
    Get Telegram channel and chat links
    """
    return {
        "telegram_links": {
            "channel": "https://t.me/traffic_platform_news",
            "chat": "https://t.me/traffic_platform_chat",
        }
    }
