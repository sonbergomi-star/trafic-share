from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.api.v1.dependencies import get_current_user
from app.models.user import User
from app.models.transaction import Transaction, TransactionType
from sqlalchemy import desc, func
from datetime import datetime, timedelta

router = APIRouter()


@router.get("/balance/{telegram_id}")
async def get_balance(
    telegram_id: int,
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get user balance and transactions"""
    if current_user.telegram_id != telegram_id:
        from app.services.user_service import is_admin
        if not is_admin(current_user.telegram_id):
            raise HTTPException(status_code=403, detail="Access denied")
    
    user = current_user if current_user.telegram_id == telegram_id else db.query(User).filter(User.telegram_id == telegram_id).first()
    
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Get recent transactions
    transactions = db.query(Transaction).filter(
        Transaction.telegram_id == telegram_id
    ).order_by(desc(Transaction.created_at)).limit(10).all()
    
    # Calculate today and month earnings
    today_start = datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)
    month_start = datetime.utcnow().replace(day=1, hour=0, minute=0, second=0, microsecond=0)
    
    from sqlalchemy import func
    today_earn = db.query(func.sum(Transaction.amount_usd)).filter(
        Transaction.telegram_id == telegram_id,
        Transaction.type == TransactionType.INCOME,
        Transaction.created_at >= today_start
    ).scalar() or 0
    
    month_earn = db.query(func.sum(Transaction.amount_usd)).filter(
        Transaction.telegram_id == telegram_id,
        Transaction.type == TransactionType.INCOME,
        Transaction.created_at >= month_start
    ).scalar() or 0
    
    return {
        "user": {
            "telegram_id": telegram_id,
            "first_name": user.first_name,
            "username": user.username,
            "photo_url": user.photo_url,
            "auth_date": user.auth_date.isoformat() if user.auth_date else None,
        },
        "balance": {
            "usd": float(user.balance_usd),
            "usdt_equivalent": float(user.balance_usd) * 0.90,
            "sent_mb": float(user.sent_mb),
            "used_mb": float(user.used_mb),
            "pending_usd": 0.00,
            "last_refreshed": datetime.utcnow().isoformat(),
        },
        "today_earn": float(today_earn),
        "month_earn": float(month_earn),
        "transactions": [
            {
                "id": t.id,
                "type": t.type.value,
                "amount_usd": float(t.amount_usd),
                "status": t.status.value,
                "created_at": t.created_at.isoformat() if t.created_at else None,
            }
            for t in transactions
        ]
    }


@router.post("/refresh_balance")
async def refresh_balance(
    telegram_id: int,
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Refresh user balance"""
    if current_user.telegram_id != telegram_id:
        raise HTTPException(status_code=403, detail="Access denied")
    
    # TODO: Implement balance reconciliation logic
    # For now, just return current balance
    
    return {
        "status": "success",
        "new_balance_usd": float(current_user.balance_usd),
        "delta": 0.00
    }
