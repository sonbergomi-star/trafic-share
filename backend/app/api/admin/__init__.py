from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from pydantic import BaseModel
from datetime import date

from app.core.database import get_db
from app.core.config import settings
from app.models.user import User
from app.models.session import Session
from app.models.transaction import Transaction, WithdrawRequest
from app.models.pricing import DailyPrice
from app.models.announcement import Announcement


router = APIRouter()


def check_admin(telegram_id: int):
    """Check if user is admin"""
    if telegram_id not in settings.admin_ids_list:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required"
        )


@router.get("/dashboard")
async def admin_dashboard(admin_id: int, db: AsyncSession = Depends(get_db)):
    """
    Get admin dashboard statistics
    """
    check_admin(admin_id)
    
    # Get total users
    users_count = await db.execute(select(func.count(User.id)))
    total_users = users_count.scalar()
    
    # Get total balance
    balance_sum = await db.execute(select(func.sum(User.balance_usd)))
    total_balance = balance_sum.scalar() or 0.0
    
    # Get active sessions
    active_sessions = await db.execute(
        select(func.count(Session.id)).where(Session.is_active == True)
    )
    active_sessions_count = active_sessions.scalar()
    
    # Get pending withdraws
    pending_withdraws = await db.execute(
        select(func.count(WithdrawRequest.id)).where(WithdrawRequest.status == 'pending')
    )
    pending_withdraws_count = pending_withdraws.scalar()
    
    return {
        "total_users": total_users,
        "total_balance_usd": round(total_balance, 2),
        "active_sessions": active_sessions_count,
        "pending_withdraws": pending_withdraws_count,
    }


class SetPriceRequest(BaseModel):
    price_per_gb: float
    message: str | None = None


@router.post("/price/set")
async def set_daily_price(
    admin_id: int,
    request: SetPriceRequest,
    db: AsyncSession = Depends(get_db)
):
    """
    Set daily price
    """
    check_admin(admin_id)
    
    today = date.today()
    
    # Check if price exists for today
    result = await db.execute(
        select(DailyPrice).where(DailyPrice.date == today)
    )
    price = result.scalar_one_or_none()
    
    if price:
        price.price_per_gb = request.price_per_gb
        price.price_per_mb = request.price_per_gb / 1024
        price.message = request.message
    else:
        price = DailyPrice(
            date=today,
            price_per_gb=request.price_per_gb,
            price_per_mb=request.price_per_gb / 1024,
            message=request.message,
        )
        db.add(price)
    
    await db.commit()
    
    # TODO: Send push notification to all users
    
    return {
        "status": "success",
        "message": "Price updated successfully",
        "price_per_gb": request.price_per_gb,
    }


@router.get("/users")
async def get_all_users(admin_id: int, db: AsyncSession = Depends(get_db)):
    """
    Get all users (admin only)
    """
    check_admin(admin_id)
    
    result = await db.execute(select(User).limit(100))
    users = result.scalars().all()
    
    return {
        "users": [
            {
                "id": u.id,
                "telegram_id": u.telegram_id,
                "username": u.username,
                "first_name": u.first_name,
                "balance_usd": u.balance_usd,
                "is_active": u.is_active,
                "is_banned": u.is_banned,
                "created_at": u.created_at.isoformat(),
            }
            for u in users
        ]
    }


@router.get("/withdraws/pending")
async def get_pending_withdraws(admin_id: int, db: AsyncSession = Depends(get_db)):
    """
    Get pending withdraw requests
    """
    check_admin(admin_id)
    
    result = await db.execute(
        select(WithdrawRequest)
        .where(WithdrawRequest.status.in_(['pending', 'processing']))
        .limit(50)
    )
    withdraws = result.scalars().all()
    
    return {
        "withdraws": [
            {
                "id": w.id,
                "telegram_id": w.telegram_id,
                "amount_usd": w.amount_usd,
                "wallet_address": w.wallet_address,
                "status": w.status,
                "created_at": w.created_at.isoformat(),
            }
            for w in withdraws
        ]
    }
