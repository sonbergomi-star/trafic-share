from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from pydantic import BaseModel

from app.core.database import get_db
from app.core.security import create_access_token
from app.models.user import User
from app.models.settings import UserSettings


router = APIRouter()


@router.get("/{telegram_id}")
async def get_profile(telegram_id: int, db: AsyncSession = Depends(get_db)):
    """
    Get user profile information
    """
    result = await db.execute(
        select(User).where(User.telegram_id == telegram_id)
    )
    user = result.scalar_one_or_none()
    
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    return {
        "telegram_id": user.telegram_id,
        "username": user.username,
        "first_name": user.first_name,
        "photo_url": user.photo_url,
        "auth_date": user.auth_date.isoformat() if user.auth_date else None,
        "jwt_token": user.jwt_token,
        "two_factor_enabled": user.two_factor_enabled,
        "last_login_ip": user.last_login_ip,
        "last_login_device": user.last_login_device,
    }


@router.post("/token/renew")
async def renew_token(telegram_id: int, db: AsyncSession = Depends(get_db)):
    """
    Renew JWT token
    """
    result = await db.execute(
        select(User).where(User.telegram_id == telegram_id)
    )
    user = result.scalar_one_or_none()
    
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Generate new token
    new_token = create_access_token(
        data={
            "telegram_id": user.telegram_id,
            "username": user.username,
        }
    )
    
    user.jwt_token = new_token
    await db.commit()
    
    return {
        "message": "Token successfully renewed",
        "jwt_token": new_token,
    }


@router.get("/settings/{telegram_id}")
async def get_settings(telegram_id: int, db: AsyncSession = Depends(get_db)):
    """
    Get user settings
    """
    result = await db.execute(
        select(UserSettings).where(UserSettings.telegram_id == telegram_id)
    )
    settings = result.scalar_one_or_none()
    
    if not settings:
        # Create default settings
        user_result = await db.execute(
            select(User).where(User.telegram_id == telegram_id)
        )
        user = user_result.scalar_one_or_none()
        
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        
        settings = UserSettings(
            user_id=user.id,
            telegram_id=telegram_id,
        )
        db.add(settings)
        await db.commit()
        await db.refresh(settings)
    
    return {
        "language": settings.language,
        "push_notifications": settings.push_notifications,
        "session_updates": settings.session_updates,
        "system_updates": settings.system_updates,
        "two_factor_enabled": settings.two_factor_enabled,
        "single_device_mode": settings.single_device_mode,
        "battery_saver": settings.battery_saver,
        "theme": settings.theme,
    }


class UpdateSettingsRequest(BaseModel):
    language: str | None = None
    push_notifications: bool | None = None
    session_updates: bool | None = None
    system_updates: bool | None = None
    battery_saver: bool | None = None
    theme: str | None = None


@router.patch("/settings/{telegram_id}")
async def update_settings(
    telegram_id: int,
    request: UpdateSettingsRequest,
    db: AsyncSession = Depends(get_db)
):
    """
    Update user settings
    """
    result = await db.execute(
        select(UserSettings).where(UserSettings.telegram_id == telegram_id)
    )
    settings = result.scalar_one_or_none()
    
    if not settings:
        raise HTTPException(status_code=404, detail="Settings not found")
    
    # Update only provided fields
    if request.language is not None:
        settings.language = request.language
    if request.push_notifications is not None:
        settings.push_notifications = request.push_notifications
    if request.session_updates is not None:
        settings.session_updates = request.session_updates
    if request.system_updates is not None:
        settings.system_updates = request.system_updates
    if request.battery_saver is not None:
        settings.battery_saver = request.battery_saver
    if request.theme is not None:
        settings.theme = request.theme
    
    await db.commit()
    
    return {
        "status": "success",
        "message": "Settings updated successfully",
    }
