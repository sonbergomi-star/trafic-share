from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from datetime import datetime, date
from pydantic import BaseModel

from app.core.database import get_db
from app.models.user import User
from app.models.session import Session
from app.models.pricing import DailyPrice


router = APIRouter()


class DashboardResponse(BaseModel):
    user: dict
    balance: dict
    traffic: dict
    pricing: dict
    mini_stats: dict


@router.get("/{telegram_id}", response_model=DashboardResponse)
async def get_dashboard(telegram_id: int, db: AsyncSession = Depends(get_db)):
    """
    Get dashboard data for user
    """
    # Get user
    result = await db.execute(
        select(User).where(User.telegram_id == telegram_id)
    )
    user = result.scalar_one_or_none()
    
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Get today's price
    today = date.today()
    price_result = await db.execute(
        select(DailyPrice).where(DailyPrice.date == today)
    )
    daily_price = price_result.scalar_one_or_none()
    
    price_per_gb = daily_price.price_per_gb if daily_price else 1.50
    price_per_mb = daily_price.price_per_mb if daily_price else 0.0015
    
    # Get active sessions
    active_sessions_result = await db.execute(
        select(func.count(Session.id))
        .where(Session.telegram_id == telegram_id)
        .where(Session.is_active == True)
    )
    active_sessions_count = active_sessions_result.scalar()
    
    # Calculate statistics
    remaining_mb = user.sent_mb - user.used_mb
    
    return {
        "user": {
            "telegram_id": user.telegram_id,
            "first_name": user.first_name,
            "username": user.username,
            "photo_url": user.photo_url,
            "auth_date": user.auth_date.isoformat() if user.auth_date else None,
        },
        "balance": {
            "usd": round(user.balance_usd, 2),
            "sent_mb": round(user.sent_mb, 2),
            "used_mb": round(user.used_mb, 2),
        },
        "traffic": {
            "sent_mb": round(user.sent_mb, 2),
            "used_mb": round(user.used_mb, 2),
            "remaining_mb": round(remaining_mb, 2),
            "active_sessions": active_sessions_count,
        },
        "pricing": {
            "price_per_gb": price_per_gb,
            "price_per_mb": price_per_mb,
            "message": daily_price.message if daily_price else "Current traffic price",
        },
        "mini_stats": {
            "today_earning": 0.0,  # Will be calculated from today's sessions
            "week_earning": 0.0,   # Will be calculated from week's sessions
        }
    }
