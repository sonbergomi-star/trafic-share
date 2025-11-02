from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from datetime import datetime
from pydantic import BaseModel

from app.core.database import get_db
from app.core.security import verify_telegram_auth, create_access_token
from app.models.user import User


router = APIRouter()


class TelegramAuthData(BaseModel):
    id: int
    first_name: str
    username: str | None = None
    photo_url: str | None = None
    auth_date: int
    hash: str


class AuthResponse(BaseModel):
    status: str
    user: dict
    token: str


@router.post("/telegram", response_model=AuthResponse)
async def telegram_auth(auth_data: TelegramAuthData, db: AsyncSession = Depends(get_db)):
    """
    Telegram OAuth authentication
    """
    # Verify Telegram signature
    auth_dict = auth_data.dict()
    if not verify_telegram_auth(auth_dict):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid Telegram signature"
        )
    
    # Check if user exists
    result = await db.execute(
        select(User).where(User.telegram_id == auth_data.id)
    )
    user = result.scalar_one_or_none()
    
    if user:
        # Update existing user
        user.username = auth_data.username
        user.first_name = auth_data.first_name
        user.photo_url = auth_data.photo_url
        user.auth_date = datetime.fromtimestamp(auth_data.auth_date)
        user.last_seen = datetime.utcnow()
    else:
        # Create new user
        user = User(
            telegram_id=auth_data.id,
            username=auth_data.username,
            first_name=auth_data.first_name,
            photo_url=auth_data.photo_url,
            auth_date=datetime.fromtimestamp(auth_data.auth_date),
            last_seen=datetime.utcnow()
        )
        db.add(user)
    
    # Generate JWT token
    token = create_access_token(
        data={
            "telegram_id": auth_data.id,
            "username": auth_data.username,
        }
    )
    
    user.jwt_token = token
    await db.commit()
    await db.refresh(user)
    
    return {
        "status": "success",
        "user": {
            "telegram_id": user.telegram_id,
            "username": user.username,
            "first_name": user.first_name,
            "photo_url": user.photo_url,
            "balance_usd": user.balance_usd,
        },
        "token": token
    }


@router.post("/logout")
async def logout(telegram_id: int, db: AsyncSession = Depends(get_db)):
    """
    Logout user
    """
    result = await db.execute(
        select(User).where(User.telegram_id == telegram_id)
    )
    user = result.scalar_one_or_none()
    
    if user:
        user.jwt_token = None
        await db.commit()
    
    return {"status": "success", "message": "Logged out successfully"}
