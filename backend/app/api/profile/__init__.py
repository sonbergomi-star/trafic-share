from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from pydantic import BaseModel
import logging

from app.core.database import get_db
from app.middleware.auth import get_current_user
from app.models.user import User
from app.models.session import Session
from app.models.transaction import Transaction

logger = logging.getLogger(__name__)

router = APIRouter()


class UpdateProfileRequest(BaseModel):
    first_name: str | None = None
    last_name: str | None = None
    username: str | None = None


@router.get("/")
async def get_profile(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    REAL get user profile with statistics
    """
    # Get total sessions
    sessions_result = await db.execute(
        select(func.count(Session.id))
        .where(Session.telegram_id == current_user.telegram_id)
    )
    total_sessions = sessions_result.scalar()
    
    # Get completed sessions
    completed_result = await db.execute(
        select(func.count(Session.id))
        .where(Session.telegram_id == current_user.telegram_id)
        .where(Session.status == 'completed')
    )
    completed_sessions = completed_result.scalar()
    
    # Get total earned
    earned_result = await db.execute(
        select(func.sum(Session.earned_usd))
        .where(Session.telegram_id == current_user.telegram_id)
        .where(Session.status == 'completed')
    )
    total_earned = earned_result.scalar() or 0.0
    
    # Get total withdrawn
    withdrawn_result = await db.execute(
        select(func.sum(Transaction.amount_usd))
        .where(Transaction.telegram_id == current_user.telegram_id)
        .where(Transaction.type == 'withdraw')
        .where(Transaction.status == 'completed')
    )
    total_withdrawn = abs(withdrawn_result.scalar() or 0.0)
    
    return {
        "status": "success",
        "data": {
            "user": {
                "telegram_id": current_user.telegram_id,
                "username": current_user.username,
                "first_name": current_user.first_name,
                "last_name": current_user.last_name,
                "balance_usd": float(current_user.balance_usd),
                "created_at": current_user.created_at.isoformat(),
                "last_seen": current_user.last_seen.isoformat() if current_user.last_seen else None,
            },
            "stats": {
                "total_sessions": total_sessions,
                "completed_sessions": completed_sessions,
                "success_rate": (completed_sessions / total_sessions * 100) if total_sessions > 0 else 0,
                "sent_mb": float(current_user.sent_mb),
                "sent_gb": float(current_user.sent_mb / 1024),
                "total_earned": float(total_earned),
                "total_withdrawn": float(total_withdrawn),
            },
            "security": {
                "is_active": current_user.is_active,
                "is_banned": current_user.is_banned,
            }
        }
    }


@router.put("/update")
async def update_profile(
    request: UpdateProfileRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    REAL update user profile
    """
    # Update fields if provided
    if request.first_name is not None:
        current_user.first_name = request.first_name
    
    if request.last_name is not None:
        current_user.last_name = request.last_name
    
    if request.username is not None:
        current_user.username = request.username
    
    await db.commit()
    await db.refresh(current_user)
    
    logger.info(f"Profile updated for user {current_user.telegram_id}")
    
    return {
        "status": "success",
        "data": {
            "telegram_id": current_user.telegram_id,
            "username": current_user.username,
            "first_name": current_user.first_name,
            "last_name": current_user.last_name,
        }
    }


@router.delete("/account")
async def delete_account(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    REAL delete user account (soft delete)
    """
    # Soft delete - just deactivate
    current_user.is_active = False
    await db.commit()
    
    logger.warning(f"Account deactivated for user {current_user.telegram_id}")
    
    return {
        "status": "success",
        "message": "Account deactivated successfully"
    }
