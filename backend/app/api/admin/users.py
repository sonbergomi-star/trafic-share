from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional

from app.core.database import get_db
from app.middleware.auth import verify_admin
from app.models.user import User
from app.services.admin_service import AdminService

router = APIRouter(prefix="/admin/users", tags=["Admin - Users"])


@router.get("/")
async def get_users(
    page: int = Query(1, ge=1),
    per_page: int = Query(50, ge=1, le=100),
    search: Optional[str] = None,
    status_filter: Optional[str] = None,
    admin: User = Depends(verify_admin),
    db: AsyncSession = Depends(get_db)
):
    """
    Get all users with pagination and filters (Admin only)
    """
    admin_service = AdminService(db)
    result = await admin_service.get_all_users(
        page=page,
        per_page=per_page,
        search=search,
        status_filter=status_filter
    )
    
    return {
        "status": "success",
        "data": result
    }


@router.post("/{telegram_id}/ban")
async def ban_user(
    telegram_id: int,
    reason: Optional[str] = None,
    admin: User = Depends(verify_admin),
    db: AsyncSession = Depends(get_db)
):
    """
    Ban a user (Admin only)
    """
    admin_service = AdminService(db)
    result = await admin_service.ban_user(telegram_id, reason)
    
    return {
        "status": "success",
        "data": result
    }


@router.post("/{telegram_id}/unban")
async def unban_user(
    telegram_id: int,
    admin: User = Depends(verify_admin),
    db: AsyncSession = Depends(get_db)
):
    """
    Unban a user (Admin only)
    """
    admin_service = AdminService(db)
    result = await admin_service.unban_user(telegram_id)
    
    return {
        "status": "success",
        "data": result
    }


@router.post("/{telegram_id}/adjust-balance")
async def adjust_balance(
    telegram_id: int,
    amount: float,
    reason: str,
    admin: User = Depends(verify_admin),
    db: AsyncSession = Depends(get_db)
):
    """
    Manually adjust user balance (Admin only)
    """
    admin_service = AdminService(db)
    result = await admin_service.adjust_user_balance(
        telegram_id=telegram_id,
        amount=amount,
        reason=reason,
        admin_id=admin.telegram_id
    )
    
    return {
        "status": "success",
        "data": result
    }


@router.get("/{telegram_id}/details")
async def get_user_details(
    telegram_id: int,
    admin: User = Depends(verify_admin),
    db: AsyncSession = Depends(get_db)
):
    """
    Get detailed user information (Admin only)
    """
    from sqlalchemy import select
    from app.models.session import Session
    from app.models.transaction import Transaction
    
    # Get user
    result = await db.execute(
        select(User).where(User.telegram_id == telegram_id)
    )
    user = result.scalar_one_or_none()
    
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Get session count
    sessions_result = await db.execute(
        select(func.count(Session.id))
        .where(Session.telegram_id == telegram_id)
    )
    session_count = sessions_result.scalar()
    
    # Get transaction count
    transactions_result = await db.execute(
        select(func.count(Transaction.id))
        .where(Transaction.telegram_id == telegram_id)
    )
    transaction_count = transactions_result.scalar()
    
    return {
        "status": "success",
        "data": {
            "user": {
                "telegram_id": user.telegram_id,
                "username": user.username,
                "first_name": user.first_name,
                "balance_usd": user.balance_usd,
                "sent_mb": user.sent_mb,
                "used_mb": user.used_mb,
                "is_active": user.is_active,
                "is_banned": user.is_banned,
                "created_at": user.created_at.isoformat(),
                "last_seen": user.last_seen.isoformat() if user.last_seen else None,
            },
            "stats": {
                "total_sessions": session_count,
                "total_transactions": transaction_count,
            }
        }
    }


from sqlalchemy import func
