from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session
from sqlalchemy import func, desc
from app.core.database import get_db
from app.api.v1.dependencies import get_current_admin
from app.models.user import User
from app.models.withdraw import WithdrawRequest
from app.models.daily_price import DailyPrice
from app.models.announcement import Announcement, PromoCode
from datetime import datetime, date, timedelta

router = APIRouter()


@router.get("/dashboard/summary")
async def admin_dashboard_summary(
    admin = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """Get admin dashboard summary"""
    users_count = db.query(func.count(User.id)).scalar()
    total_balance = db.query(func.sum(User.balance_usd)).scalar() or 0
    
    from app.models.session import TrafficSession
    active_sessions = db.query(func.count(TrafficSession.id)).filter(
        TrafficSession.is_active == True
    ).scalar()
    
    today = datetime.utcnow().date()
    today_withdraws = db.query(func.sum(WithdrawRequest.amount_usd)).filter(
        WithdrawRequest.created_at >= datetime.combine(today, datetime.min.time()),
        WithdrawRequest.status == "completed"
    ).scalar() or 0
    
    from app.models.transaction import Transaction, TransactionType
    today_revenue = db.query(func.sum(Transaction.amount_usd)).filter(
        Transaction.type == TransactionType.INCOME,
        Transaction.created_at >= datetime.combine(today, datetime.min.time())
    ).scalar() or 0
    
    return {
        "users_count": users_count,
        "total_balance": float(total_balance),
        "active_sessions": active_sessions,
        "today_withdraws": float(today_withdraws),
        "today_revenue": float(today_revenue)
    }


@router.get("/users")
async def get_users(
    admin = Depends(get_current_admin),
    db: Session = Depends(get_db),
    limit: int = 50,
    offset: int = 0
):
    """Get all users"""
    users = db.query(User).offset(offset).limit(limit).all()
    
    return [
        {
            "telegram_id": u.telegram_id,
            "username": u.username,
            "first_name": u.first_name,
            "balance_usd": float(u.balance_usd),
            "sent_mb": float(u.sent_mb),
            "used_mb": float(u.used_mb),
            "auth_date": u.auth_date.isoformat() if u.auth_date else None,
            "status": u.status
        }
        for u in users
    ]


class DailyPriceCreate(BaseModel):
    date: date
    price_per_gb: float
    message: str = None


@router.post("/daily_price")
async def create_daily_price(
    price_data: DailyPriceCreate,
    admin = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """Create or update daily price"""
    from app.services.daily_price_service import create_or_update_price
    
    price = create_or_update_price(
        db,
        price_data.date,
        price_data.price_per_gb,
        price_data.message
    )
    
    # Send notification to all users
    from app.services.notification_service import send_notification_to_all
    send_notification_to_all(
        db,
        "?? Kunlik narx yangilandi!",
        f"Bugungi narx: ${price_data.price_per_gb}/GB",
        {"type": "daily_price", "price": price_data.price_per_gb}
    )
    
    return {
        "status": "success",
        "price": {
            "date": price.date.isoformat(),
            "price_per_gb": float(price.price_per_gb),
            "message": price.message
        }
    }


@router.get("/withdraws")
async def get_withdraws(
    admin = Depends(get_current_admin),
    db: Session = Depends(get_db),
    status: str = None
):
    """Get withdraw requests"""
    query = db.query(WithdrawRequest)
    
    if status:
        query = query.filter(WithdrawRequest.status == status)
    
    withdraws = query.order_by(desc(WithdrawRequest.created_at)).limit(50).all()
    
    return [
        {
            "id": w.id,
            "telegram_id": w.telegram_id,
            "amount_usd": float(w.amount_usd),
            "wallet_address": w.wallet_address,
            "status": w.status.value,
            "created_at": w.created_at.isoformat() if w.created_at else None,
        }
        for w in withdraws
    ]
