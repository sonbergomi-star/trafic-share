from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import desc
from app.core.database import get_db
from app.models.announcement import Announcement, PromoCode
from app.core.config import settings
from datetime import datetime

router = APIRouter()


@router.get("/promo")
async def get_news_promo(
    db: Session = Depends(get_db)
):
    """Get news, promo codes, and Telegram links"""
    # Get announcements
    announcements = db.query(Announcement).order_by(desc(Announcement.created_at)).limit(10).all()
    
    # Get active promo codes
    promo_codes = db.query(PromoCode).filter(
        PromoCode.is_active == True,
        (PromoCode.expires_at.is_(None)) | (PromoCode.expires_at > datetime.utcnow())
    ).all()
    
    return {
        "telegram_links": {
            "channel": getattr(settings, "TELEGRAM_CHANNEL_LINK", "https://t.me/your_channel"),
            "chat": getattr(settings, "TELEGRAM_CHAT_LINK", "https://t.me/your_chat")
        },
        "announcements": [
            {
                "id": a.id,
                "title": a.title,
                "description": a.description,
                "image_url": a.image_url,
                "link": a.link,
                "created_at": a.created_at.isoformat() if a.created_at else None,
            }
            for a in announcements
        ],
        "promo": [
            {
                "code": p.code,
                "bonus_percent": float(p.bonus_percent),
                "expires_at": p.expires_at.isoformat() if p.expires_at else None,
                "is_active": p.is_active
            }
            for p in promo_codes
        ]
    }


@router.post("/promo/activate")
async def activate_promo(
    code: str,
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Activate promo code"""
    promo = db.query(PromoCode).filter(
        PromoCode.code == code.upper(),
        PromoCode.is_active == True
    ).first()
    
    if not promo:
        raise HTTPException(status_code=404, detail="Promo code not found")
    
    if promo.expires_at and promo.expires_at < datetime.utcnow():
        raise HTTPException(status_code=400, detail="Promo code expired")
    
    # Apply bonus to user balance
    bonus_amount = float(current_user.balance_usd) * (float(promo.bonus_percent) / 100)
    from app.services.user_service import update_user_balance
    update_user_balance(db, current_user.telegram_id, bonus_amount, f"Promo code: {code}")
    
    return {
        "status": "success",
        "message": f"Promo-kod muvaffaqiyatli faollashtirildi! +${bonus_amount:.2f}"
    }
