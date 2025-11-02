from sqlalchemy.orm import Session
from sqlalchemy import func
from app.models.user import User
from app.models.session import TrafficSession
from app.models.daily_price import DailyPrice
from app.models.transaction import Transaction
from datetime import datetime, timedelta
from typing import Dict


def get_dashboard_data(db: Session, telegram_id: int) -> Dict:
    """Get dashboard data for user"""
    user = db.query(User).filter(User.telegram_id == telegram_id).first()
    if not user:
        return {}
    
    # Get today's price
    today = datetime.utcnow().date()
    daily_price = db.query(DailyPrice).filter(DailyPrice.date == today).first()
    price_per_gb = float(daily_price.price_per_gb) if daily_price else 1.50
    
    # Calculate remaining traffic
    remaining_mb = max(0, float(user.sent_mb) - float(user.used_mb))
    
    # Get last 7 days earnings
    week_ago = datetime.utcnow() - timedelta(days=7)
    week_transactions = db.query(func.sum(Transaction.amount_usd)).filter(
        Transaction.telegram_id == telegram_id,
        Transaction.type == "income",
        Transaction.status == "completed",
        Transaction.created_at >= week_ago
    ).scalar() or 0
    
    # Get today's earnings
    today_start = datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)
    today_transactions = db.query(func.sum(Transaction.amount_usd)).filter(
        Transaction.telegram_id == telegram_id,
        Transaction.type == "income",
        Transaction.status == "completed",
        Transaction.created_at >= today_start
    ).scalar() or 0
    
    return {
        "user": {
            "telegram_id": str(user.telegram_id),
            "first_name": user.first_name or "",
            "username": user.username or "",
            "photo_url": user.photo_url or "",
            "auth_date": user.auth_date.isoformat() if user.auth_date else None,
        },
        "balance": {
            "usd": float(user.balance_usd),
            "converted_usdt": float(user.balance_usd) * 0.90,  # Example conversion
            "converted_uzs": float(user.balance_usd) * 72000,  # Example conversion
        },
        "traffic": {
            "sent_mb": float(user.sent_mb),
            "used_mb": float(user.used_mb),
            "remaining_mb": remaining_mb,
        },
        "pricing": {
            "price_per_gb": price_per_gb,
            "date": today.isoformat(),
        },
        "mini_stats": {
            "today_earn": float(today_transactions),
            "week_earn": float(week_transactions),
        }
    }
