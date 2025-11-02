from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, desc
from pydantic import BaseModel

from app.core.database import get_db
from app.models.user import User
from app.models.transaction import Transaction


router = APIRouter()


class BalanceResponse(BaseModel):
    user: dict
    balance: dict
    traffic: dict
    transactions: list


@router.get("/{telegram_id}", response_model=BalanceResponse)
async def get_balance(telegram_id: int, db: AsyncSession = Depends(get_db)):
    """
    Get user balance and transaction history
    """
    # Get user
    result = await db.execute(
        select(User).where(User.telegram_id == telegram_id)
    )
    user = result.scalar_one_or_none()
    
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Get recent transactions
    transactions_result = await db.execute(
        select(Transaction)
        .where(Transaction.telegram_id == telegram_id)
        .order_by(desc(Transaction.created_at))
        .limit(10)
    )
    transactions = transactions_result.scalars().all()
    
    return {
        "user": {
            "telegram_id": user.telegram_id,
            "first_name": user.first_name,
            "username": user.username,
            "photo_url": user.photo_url,
        },
        "balance": {
            "usd": round(user.balance_usd, 2),
        },
        "traffic": {
            "sent_mb": round(user.sent_mb, 2),
            "used_mb": round(user.used_mb, 2),
        },
        "transactions": [
            {
                "id": t.id,
                "type": t.type,
                "amount_usd": t.amount_usd,
                "status": t.status,
                "description": t.description,
                "created_at": t.created_at.isoformat(),
            }
            for t in transactions
        ]
    }


@router.post("/refresh")
async def refresh_balance(telegram_id: int, db: AsyncSession = Depends(get_db)):
    """
    Refresh user balance from pending transactions
    """
    result = await db.execute(
        select(User).where(User.telegram_id == telegram_id)
    )
    user = result.scalar_one_or_none()
    
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Here you would reconcile pending_chunks and calculate new balance
    # For now, just return current balance
    
    return {
        "status": "success",
        "new_balance_usd": round(user.balance_usd, 2),
        "delta": 0.0
    }
