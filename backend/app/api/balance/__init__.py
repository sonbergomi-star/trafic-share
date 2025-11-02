from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, desc
from datetime import datetime, date

from app.core.database import get_db
from app.middleware.auth import get_current_user
from app.models.user import User
from app.models.transaction import Transaction, WithdrawRequest
from app.models.session import Session
import logging

logger = logging.getLogger(__name__)

router = APIRouter()


@router.get("/")
async def get_balance(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    REAL balance calculation from database
    """
    # Calculate pending withdrawals
    pending_result = await db.execute(
        select(func.sum(WithdrawRequest.amount_usd))
        .where(WithdrawRequest.telegram_id == current_user.telegram_id)
        .where(WithdrawRequest.status.in_(['pending', 'processing']))
    )
    pending_amount = pending_result.scalar() or 0.0
    
    # Calculate today's earnings
    today_start = datetime.combine(date.today(), datetime.min.time())
    today_result = await db.execute(
        select(func.sum(Session.earned_usd))
        .where(Session.telegram_id == current_user.telegram_id)
        .where(Session.start_time >= today_start)
        .where(Session.status == 'completed')
    )
    today_earnings = today_result.scalar() or 0.0
    
    # Total withdrawn
    withdrawn_result = await db.execute(
        select(func.sum(WithdrawRequest.amount_usd))
        .where(WithdrawRequest.telegram_id == current_user.telegram_id)
        .where(WithdrawRequest.status == 'completed')
    )
    total_withdrawn = withdrawn_result.scalar() or 0.0
    
    return {
        "status": "success",
        "data": {
            "balance_usd": float(current_user.balance_usd),
            "available_balance": float(current_user.balance_usd - pending_amount),
            "pending_withdrawals": float(pending_amount),
            "sent_mb": float(current_user.sent_mb),
            "used_mb": float(current_user.used_mb),
            "sent_gb": float(current_user.sent_mb / 1024),
            "today_earnings": float(today_earnings),
            "total_withdrawn": float(abs(total_withdrawn)),
            "can_withdraw": (current_user.balance_usd - pending_amount) >= 1.39,
        }
    }


@router.get("/transactions")
async def get_transactions(
    page: int = Query(1, ge=1),
    per_page: int = Query(20, ge=1, le=100),
    type_filter: str = Query(None),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    REAL transaction history from database with pagination
    """
    # Base query
    query = select(Transaction).where(Transaction.telegram_id == current_user.telegram_id)
    
    # Apply filter
    if type_filter:
        query = query.where(Transaction.type == type_filter)
    
    # Count total
    count_query = select(func.count()).select_from(query.subquery())
    count_result = await db.execute(count_query)
    total = count_result.scalar()
    
    # Get paginated data
    offset = (page - 1) * per_page
    query = query.order_by(desc(Transaction.created_at)).offset(offset).limit(per_page)
    result = await db.execute(query)
    transactions = result.scalars().all()
    
    return {
        "status": "success",
        "data": {
            "transactions": [
                {
                    "id": t.id,
                    "type": t.type,
                    "amount_usd": float(t.amount_usd),
                    "status": t.status,
                    "description": t.description,
                    "note": t.note,
                    "created_at": t.created_at.isoformat(),
                }
                for t in transactions
            ],
            "pagination": {
                "page": page,
                "per_page": per_page,
                "total": total,
                "total_pages": (total + per_page - 1) // per_page,
                "has_next": page * per_page < total,
                "has_prev": page > 1,
            }
        }
    }


@router.post("/refresh")
async def refresh_balance(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    REAL balance refresh - recalculates from sessions and withdrawals
    """
    # Calculate total earnings
    earnings_result = await db.execute(
        select(func.sum(Session.earned_usd))
        .where(Session.telegram_id == current_user.telegram_id)
        .where(Session.status == 'completed')
    )
    total_earnings = earnings_result.scalar() or 0.0
    
    # Calculate total withdrawn
    withdrawn_result = await db.execute(
        select(func.sum(WithdrawRequest.amount_usd))
        .where(WithdrawRequest.telegram_id == current_user.telegram_id)
        .where(WithdrawRequest.status == 'completed')
    )
    total_withdrawn = abs(withdrawn_result.scalar() or 0.0)
    
    # Calculate correct balance
    correct_balance = total_earnings - total_withdrawn
    old_balance = current_user.balance_usd
    delta = correct_balance - old_balance
    
    # Update if different
    if abs(delta) > 0.01:
        current_user.balance_usd = correct_balance
        await db.commit()
        logger.info(f"Balance refreshed for {current_user.telegram_id}: {old_balance:.2f} -> {correct_balance:.2f}")
    
    return {
        "status": "success",
        "data": {
            "old_balance": float(old_balance),
            "new_balance": float(correct_balance),
            "delta": float(delta),
            "total_earnings": float(total_earnings),
            "total_withdrawn": float(total_withdrawn),
        }
    }
