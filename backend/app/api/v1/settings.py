from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.api.v1.dependencies import get_current_user

router = APIRouter()


class SettingsUpdate(BaseModel):
    language: str = None
    push_notifications: bool = None
    session_updates: bool = None
    system_updates: bool = None
    two_factor_enabled: bool = None
    single_device_mode: bool = None
    battery_saver: bool = None
    theme: str = None


@router.get("/settings")
async def get_settings(
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get user settings"""
    return {
        "language": current_user.language,
        "push_notifications": current_user.notifications_enabled,
        "session_updates": True,  # Can be stored separately
        "system_updates": True,
        "two_factor_enabled": current_user.two_factor_enabled,
        "single_device_mode": current_user.single_device_mode,
        "battery_saver": current_user.battery_saver,
        "theme": current_user.theme
    }


@router.patch("/settings")
async def update_settings(
    settings_update: SettingsUpdate,
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Update user settings"""
    if settings_update.language:
        current_user.language = settings_update.language
    if settings_update.push_notifications is not None:
        current_user.notifications_enabled = settings_update.push_notifications
    if settings_update.two_factor_enabled is not None:
        current_user.two_factor_enabled = settings_update.two_factor_enabled
    if settings_update.single_device_mode is not None:
        current_user.single_device_mode = settings_update.single_device_mode
    if settings_update.battery_saver is not None:
        current_user.battery_saver = settings_update.battery_saver
    if settings_update.theme:
        current_user.theme = settings_update.theme
    
    db.commit()
    
    return {"status": "updated", **settings_update.dict(exclude_unset=True)}


@router.post("/security/2fa")
async def enable_2fa(
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Enable 2FA"""
    current_user.two_factor_enabled = True
    db.commit()
    return {"status": "success", "message": "2FA enabled"}


@router.post("/security/disable_2fa")
async def disable_2fa(
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Disable 2FA"""
    current_user.two_factor_enabled = False
    db.commit()
    return {"status": "success", "message": "2FA disabled"}


@router.post("/logout_all")
async def logout_all(
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Logout from all devices"""
    current_user.jwt_token = None
    db.commit()
    return {"status": "success", "message": "Logged out from all devices"}
