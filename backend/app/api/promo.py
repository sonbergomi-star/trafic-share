from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from datetime import datetime
import logging

from app.core.database import get_db
from app.middleware.auth import get_current_user
from app.models.user import User
from app.models.promo_code import PromoCode, PromoCodeUsage
from app.models.transaction import Transaction

logger = logging.getLogger(__name__)

router = APIRouter()


@router.post("/apply")
async def apply_promo_code(
    code: str,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    REAL apply promo code and get bonus
    """
    # Get promo code
    result = await db.execute(
        select(PromoCode)
        .where(PromoCode.code == code.upper())
        .where(PromoCode.is_active == True)
    )
    promo = result.scalar_one_or_none()
    
    if not promo:
        raise HTTPException(status_code=404, detail="Promo kod topilmadi yoki aktiv emas")
    
    # Check expiration
    if promo.expires_at and promo.expires_at < datetime.utcnow():
        raise HTTPException(status_code=400, detail="Promo kodning muddati tugagan")
    
    # Check max uses
    if promo.max_uses > 0 and promo.current_uses >= promo.max_uses:
        raise HTTPException(status_code=400, detail="Promo kod cheklovi tugagan")
    
    # Check if user already used this promo
    usage_result = await db.execute(
        select(PromoCodeUsage)
        .where(PromoCodeUsage.promo_code_id == promo.id)
        .where(PromoCodeUsage.telegram_id == user.telegram_id)
    )
    existing_usage = usage_result.scalar_one_or_none()
    
    if existing_usage:
        raise HTTPException(status_code=400, detail="Siz bu promo kodni allaqachon ishlatgansiz")
    
    # Apply bonus
    user.balance_usd += promo.bonus_usd
    
    # Create usage record
    usage = PromoCodeUsage(
        promo_code_id=promo.id,
        telegram_id=user.telegram_id,
        bonus_usd=promo.bonus_usd,
        used_at=datetime.utcnow()
    )
    db.add(usage)
    
    # Update promo code usage count
    promo.current_uses += 1
    
    # Create transaction
    transaction = Transaction(
        telegram_id=user.telegram_id,
        type="promo_bonus",
        amount_usd=promo.bonus_usd,
        status="completed",
        note=f"Promo kod: {code}",
        created_at=datetime.utcnow()
    )
    db.add(transaction)
    
    await db.commit()
    
    logger.info(f"User {user.telegram_id} applied promo code {code}: +${promo.bonus_usd}")
    
    # Send notification
    try:
        from app.services.notification_service import NotificationService
        notif_service = NotificationService(db)
        await notif_service.send_to_user(
            telegram_id=user.telegram_id,
            title="?? Promo kod qo'llanildi!",
            body=f"+${promo.bonus_usd:.2f} bonus balansingizga qo'shildi!",
            notif_type="promo_applied"
        )
    except Exception as e:
        logger.error(f"Failed to send promo notification: {e}")
    
    return {
        "status": "success",
        "message": "Promo kod muvaffaqiyatli qo'llanildi!",
        "bonus_usd": float(promo.bonus_usd),
        "new_balance": float(user.balance_usd)
    }
