"""Authentication routes."""

from fastapi import APIRouter, Depends, Request
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_db_session
from app.schemas import TelegramAuthRequest, TelegramAuthResponse, TokenResponse
from app.services.auth_service import AuthService


router = APIRouter()


@router.post("/telegram", response_model=TelegramAuthResponse)
async def telegram_auth(
    payload: TelegramAuthRequest,
    request: Request,
    session: AsyncSession = Depends(get_db_session),
):
    service = AuthService(session)
    user, access_token, refresh_token = await service.authenticate_telegram(
        payload, request.client.host if request.client else None
    )
    return TelegramAuthResponse(
        user={
            "telegram_id": user.telegram_id,
            "username": user.username,
            "first_name": user.first_name,
            "photo_url": user.photo_url,
            "balance_usd": float(user.balance_usd or 0),
        },
        token=TokenResponse(access_token=access_token, refresh_token=refresh_token),
    )
