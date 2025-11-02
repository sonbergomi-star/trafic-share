from sqlalchemy.orm import Session
from datetime import timedelta
from app.models.user import User
from app.core.jwt_manager import create_access_token
from app.core.telegram_auth import parse_telegram_auth_data
from app.core.config import settings


def authenticate_telegram_user(db: Session, auth_data: dict) -> dict:
    """Authenticate user via Telegram and create/update user record"""
    parsed_data = parse_telegram_auth_data(auth_data)
    if not parsed_data:
        return {"status": "error", "message": "Invalid Telegram signature"}
    
    telegram_id = parsed_data["telegram_id"]
    
    # Check if user exists
    user = db.query(User).filter(User.telegram_id == telegram_id).first()
    
    if user:
        # Update existing user
        user.username = parsed_data.get("username") or user.username
        user.first_name = parsed_data.get("first_name") or user.first_name
        user.photo_url = parsed_data.get("photo_url") or user.photo_url
        user.auth_date = parsed_data.get("auth_date")
    else:
        # Create new user
        user = User(
            telegram_id=telegram_id,
            username=parsed_data.get("username", ""),
            first_name=parsed_data.get("first_name", ""),
            photo_url=parsed_data.get("photo_url", ""),
        )
        db.add(user)
    
    db.commit()
    db.refresh(user)
    
    # Create JWT token
    token_data = {
        "telegram_id": user.telegram_id,
        "username": user.username or "",
    }
    token = create_access_token(token_data)
    user.jwt_token = token
    db.commit()
    
    return {
        "status": "success",
        "user": {
            "telegram_id": str(user.telegram_id),
            "username": user.username or "",
            "first_name": user.first_name or "",
            "photo_url": user.photo_url or "",
            "balance_usd": float(user.balance_usd),
            "auth_date": user.auth_date.isoformat() if user.auth_date else None,
        },
        "token": token
    }
