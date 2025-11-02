from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.services.auth_service import authenticate_telegram_user

router = APIRouter()


class TelegramAuthRequest(BaseModel):
    id: int
    username: str = None
    first_name: str = None
    last_name: str = None
    photo_url: str = None
    auth_date: int
    hash: str


@router.post("/telegram")
async def telegram_auth(
    auth_data: TelegramAuthRequest,
    db: Session = Depends(get_db)
):
    """Authenticate user via Telegram"""
    result = authenticate_telegram_user(db, auth_data.dict())
    
    if result["status"] == "error":
        raise HTTPException(status_code=401, detail=result["message"])
    
    return result
