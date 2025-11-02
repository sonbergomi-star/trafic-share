from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_
from datetime import datetime
import logging

from app.core.database import get_db
from app.middleware.auth import get_current_user
from app.models.user import User
from app.models.announcement import Announcement, PromoCode
from app.core.config import settings

logger = logging.getLogger(__name__)

router = APIRouter()


@router.get("/")
async def get_news(
    page: int = Query(1, ge=1),
    per_page: int = Query(10, ge=1, le=50),
    db: AsyncSession = Depends(get_db)
):
    """
    REAL get news and announcements
    """
    # Get total count of active announcements
    count_result = await db.execute(
        select(func.count(Announcement.id))
        .where(Announcement.is_active == True)
    )
    total = count_result.scalar()
    
    # Get announcements
    offset = (page - 1) * per_page
    result = await db.execute(
        select(Announcement)
        .where(Announcement.is_active == True)
        .order_by(Announcement.created_at.desc())
        .offset(offset)
        .limit(per_page)
    )
    announcements = result.scalars().all()
    
    # Get Telegram links from settings
    telegram_links = {
        "channel": settings.TELEGRAM_CHANNEL_LINK if hasattr(settings, 'TELEGRAM_CHANNEL_LINK') else None,
        "group": settings.TELEGRAM_GROUP_LINK if hasattr(settings, 'TELEGRAM_GROUP_LINK') else None,
        "support": settings.TELEGRAM_SUPPORT_LINK if hasattr(settings, 'TELEGRAM_SUPPORT_LINK') else None,
    }
    
    return {
        "status": "success",
        "data": {
            "telegram_links": telegram_links,
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
            ],
            "pagination": {
                "page": page,
                "per_page": per_page,
                "total": total,
                "total_pages": (total + per_page - 1) // per_page,
            }
        }
    }


@router.get("/promo")
async def get_promo_codes(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    REAL get active promo codes
    """
    now = datetime.utcnow()
    
    result = await db.execute(
        select(PromoCode)
        .where(PromoCode.is_active == True)
        .where(
            (PromoCode.expires_at.is_(None)) | 
            (PromoCode.expires_at > now)
        )
        .where(
            (PromoCode.max_uses.is_(None)) |
            (PromoCode.used_count < PromoCode.max_uses)
        )
        .order_by(PromoCode.created_at.desc())
    )
    promo_codes = result.scalars().all()
    
    return {
        "status": "success",
        "data": {
            "promo_codes": [
                {
                    "code": p.code,
                    "bonus_percent": float(p.bonus_percent),
                    "description": p.description,
                    "expires_at": p.expires_at.isoformat() if p.expires_at else None,
                    "remaining_uses": (p.max_uses - p.used_count) if p.max_uses else None,
                }
                for p in promo_codes
            ]
        }
    }


@router.post("/promo/apply")
async def apply_promo_code(
    code: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    REAL apply promo code for bonus
    """
    now = datetime.utcnow()
    
    # Get promo code
    result = await db.execute(
        select(PromoCode)
        .where(PromoCode.code == code.upper())
        .where(PromoCode.is_active == True)
    )
    promo = result.scalar_one_or_none()
    
    if not promo:
        raise HTTPException(status_code=404, detail="Promo code not found")
    
    # Check if expired
    if promo.expires_at and promo.expires_at < now:
        raise HTTPException(status_code=400, detail="Promo code expired")
    
    # Check if max uses reached
    if promo.max_uses and promo.used_count >= promo.max_uses:
        raise HTTPException(status_code=400, detail="Promo code usage limit reached")
    
    # Check if user already used this promo
    # TODO: Add used_promo_codes tracking to User model
    
    # Apply bonus
    bonus_amount = current_user.balance_usd * (promo.bonus_percent / 100)
    
    if bonus_amount < 0.01:
        raise HTTPException(
            status_code=400,
            detail="Insufficient balance for promo bonus. Minimum $0.01 balance required."
        )
    
    current_user.balance_usd += bonus_amount
    promo.used_count += 1
    
    # Create transaction
    from app.models.transaction import Transaction
    transaction = Transaction(
        telegram_id=current_user.telegram_id,
        type='bonus',
        amount_usd=bonus_amount,
        status='completed',
        description=f"Promo code bonus: {promo.code}",
        created_at=datetime.utcnow()
    )
    db.add(transaction)
    
    await db.commit()
    
    logger.info(
        f"Promo code applied: {code} by user {current_user.telegram_id} "
        f"bonus=${bonus_amount:.2f}"
    )
    
    return {
        "status": "success",
        "data": {
            "code": promo.code,
            "bonus_amount": float(bonus_amount),
            "new_balance": float(current_user.balance_usd),
        }
    }
