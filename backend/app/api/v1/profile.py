from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.api.v1.dependencies import get_current_user
from app.core.jwt_manager import create_access_token

router = APIRouter()


@router.get("")
async def get_profile(
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get user profile"""
    return {
        "telegram_id": current_user.telegram_id,
        "username": current_user.username,
        "first_name": current_user.first_name,
        "photo_url": current_user.photo_url,
        "auth_date": current_user.auth_date.isoformat() if current_user.auth_date else None,
        "jwt_token": current_user.jwt_token,
        "two_factor_enabled": current_user.two_factor_enabled,
        "last_login_ip": current_user.last_login_ip,
        "last_login_device": current_user.last_login_device
    }


@router.post("/token/renew")
async def renew_token(
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Renew JWT token"""
    from datetime import timedelta
    
    token_data = {
        "telegram_id": current_user.telegram_id,
        "username": current_user.username or "",
    }
    new_token = create_access_token(token_data)
    
    current_user.jwt_token = new_token
    db.commit()
    
    return {
        "message": "Token successfully renewed",
        "jwt_token": new_token
    }


@router.post("/logout")
async def logout(
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Logout user"""
    current_user.jwt_token = None
    db.commit()
    
    return {"message": "Successfully logged out"}
