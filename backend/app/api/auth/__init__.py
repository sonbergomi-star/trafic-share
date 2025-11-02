from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from datetime import datetime
from pydantic import BaseModel

from app.core.database import get_db
from app.core.security import verify_telegram_auth, create_access_token
from app.models.user import User
from app.models.notification import FCMToken
from app.middleware.auth import get_current_user
import logging

logger = logging.getLogger(__name__)

router = APIRouter()


class TelegramAuthData(BaseModel):
    id: int
    first_name: str
    last_name: str | None = None
    username: str | None = None
    photo_url: str | None = None
    auth_date: int
    hash: str


@router.post("/telegram")
async def telegram_auth(auth_data: TelegramAuthData, db: AsyncSession = Depends(get_db)):
    """
    REAL Telegram OAuth authentication with signature verification
    """
    # Verify Telegram signature
    auth_dict = auth_data.model_dump()
    is_valid = verify_telegram_auth(auth_dict)
    
    if not is_valid:
        logger.warning(f"Invalid Telegram signature for user {auth_data.id}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid Telegram authentication signature"
        )
    
    # Check if user exists
    result = await db.execute(
        select(User).where(User.telegram_id == auth_data.id)
    )
    user = result.scalar_one_or_none()
    
    is_new_user = False
    if user:
        # Update existing user info
        user.username = auth_data.username
        user.first_name = auth_data.first_name
        user.last_name = auth_data.last_name
        user.last_seen = datetime.utcnow()
        logger.info(f"Existing user logged in: {auth_data.id} (@{auth_data.username})")
    else:
        # Create new user
        is_new_user = True
        user = User(
            telegram_id=auth_data.id,
            username=auth_data.username,
            first_name=auth_data.first_name,
            last_name=auth_data.last_name,
            balance_usd=0.0,
            sent_mb=0.0,
            used_mb=0.0,
            is_active=True,
            is_banned=False,
            created_at=datetime.utcnow(),
            last_seen=datetime.utcnow()
        )
        db.add(user)
        logger.info(f"New user registered: {auth_data.id} (@{auth_data.username})")
    
    await db.commit()
    await db.refresh(user)
    
    # Generate JWT token
    token_data = {
        "sub": str(auth_data.id),
        "username": auth_data.username,
        "type": "access"
    }
    access_token = create_access_token(token_data)
    
    # Get user's session count
    from app.models.session import Session
    sessions_count = await db.execute(
        select(func.count(Session.id)).where(Session.telegram_id == user.telegram_id)
    )
    total_sessions = sessions_count.scalar() or 0
    
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "expires_in": 604800,
        "is_new_user": is_new_user,
        "user": {
            "telegram_id": user.telegram_id,
            "username": user.username,
            "first_name": user.first_name,
            "last_name": user.last_name,
            "balance_usd": float(user.balance_usd),
            "sent_mb": float(user.sent_mb),
            "used_mb": float(user.used_mb),
            "total_sessions": total_sessions,
            "is_active": user.is_active,
            "created_at": user.created_at.isoformat(),
        }
    }


@router.post("/renew")
async def renew_token(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    REAL token renewal with user data refresh
    """
    # Update last seen
    current_user.last_seen = datetime.utcnow()
    await db.commit()
    
    # Generate new token
    token_data = {
        "sub": str(current_user.telegram_id),
        "username": current_user.username,
        "type": "access"
    }
    new_token = create_access_token(token_data)
    
    logger.info(f"Token renewed for user: {current_user.telegram_id}")
    
    return {
        "access_token": new_token,
        "token_type": "bearer",
        "expires_in": 604800,
        "user": {
            "telegram_id": current_user.telegram_id,
            "balance_usd": float(current_user.balance_usd),
        }
    }


@router.post("/logout")
async def logout(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    REAL logout - deactivates FCM tokens
    """
    # Deactivate all FCM tokens
    result = await db.execute(
        select(FCMToken).where(FCMToken.telegram_id == current_user.telegram_id)
    )
    tokens = result.scalars().all()
    
    for token in tokens:
        token.is_active = False
    
    await db.commit()
    
    logger.info(f"User logged out: {current_user.telegram_id}")
    
    return {
        "status": "success",
        "message": "Logged out successfully"
    }
