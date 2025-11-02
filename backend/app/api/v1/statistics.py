from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func
from app.core.database import get_db
from app.api.v1.dependencies import get_current_user
from datetime import datetime, timedelta

router = APIRouter()


@router.get("/daily/{telegram_id}")
async def get_daily_stats(
    telegram_id: int,
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get daily statistics"""
    if current_user.telegram_id != telegram_id:
        from app.services.user_service import is_admin
        if not is_admin(current_user.telegram_id):
            raise HTTPException(status_code=403, detail="Access denied")
    
    today_start = datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)
    
    # Get today's session data
    from app.models.session import TrafficSession
    sessions = db.query(TrafficSession).filter(
        TrafficSession.telegram_id == telegram_id,
        TrafficSession.start_time >= today_start
    ).all()
    
    sent_mb = sum(float(s.sent_mb) for s in sessions)
    used_mb = sum(float(s.used_mb) for s in sessions)
    
    # Get today's earnings
    from app.models.transaction import Transaction, TransactionType
    earnings = db.query(func.sum(Transaction.amount_usd)).filter(
        Transaction.telegram_id == telegram_id,
        Transaction.type == TransactionType.INCOME,
        Transaction.created_at >= today_start
    ).scalar() or 0
    
    # Get today's price
    from app.services.daily_price_service import get_today_price
    price = get_today_price(db)
    price_per_mb = (float(price.price_per_gb) / 1024) if price else 0.0042
    
    return {
        "date": datetime.utcnow().date().isoformat(),
        "sent_mb": sent_mb,
        "used_mb": used_mb,
        "profit_usd": float(earnings),
        "price_per_mb": price_per_mb
    }


@router.get("/weekly/{telegram_id}")
async def get_weekly_stats(
    telegram_id: int,
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get weekly statistics"""
    if current_user.telegram_id != telegram_id:
        from app.services.user_service import is_admin
        if not is_admin(current_user.telegram_id):
            raise HTTPException(status_code=403, detail="Access denied")
    
    week_ago = datetime.utcnow() - timedelta(days=7)
    
    from app.models.session import TrafficSession
    from app.models.transaction import Transaction, TransactionType
    
    sessions = db.query(TrafficSession).filter(
        TrafficSession.telegram_id == telegram_id,
        TrafficSession.start_time >= week_ago
    ).all()
    
    sent_mb = sum(float(s.sent_mb) for s in sessions)
    used_mb = sum(float(s.used_mb) for s in sessions)
    
    earnings = db.query(func.sum(Transaction.amount_usd)).filter(
        Transaction.telegram_id == telegram_id,
        Transaction.type == TransactionType.INCOME,
        Transaction.created_at >= week_ago
    ).scalar() or 0
    
    return {
        "period": "weekly",
        "sent_mb": sent_mb,
        "used_mb": used_mb,
        "profit_usd": float(earnings),
        "sessions_count": len(sessions)
    }


@router.get("/monthly/{telegram_id}")
async def get_monthly_stats(
    telegram_id: int,
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get monthly statistics"""
    if current_user.telegram_id != telegram_id:
        from app.services.user_service import is_admin
        if not is_admin(current_user.telegram_id):
            raise HTTPException(status_code=403, detail="Access denied")
    
    month_start = datetime.utcnow().replace(day=1, hour=0, minute=0, second=0, microsecond=0)
    
    from app.models.session import TrafficSession
    from app.models.transaction import Transaction, TransactionType
    
    sessions = db.query(TrafficSession).filter(
        TrafficSession.telegram_id == telegram_id,
        TrafficSession.start_time >= month_start
    ).all()
    
    sent_mb = sum(float(s.sent_mb) for s in sessions)
    used_mb = sum(float(s.used_mb) for s in sessions)
    
    earnings = db.query(func.sum(Transaction.amount_usd)).filter(
        Transaction.telegram_id == telegram_id,
        Transaction.type == TransactionType.INCOME,
        Transaction.created_at >= month_start
    ).scalar() or 0
    
    return {
        "period": "monthly",
        "sent_mb": sent_mb,
        "used_mb": used_mb,
        "profit_usd": float(earnings),
        "sessions_count": len(sessions)
    }
