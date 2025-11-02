"""Profile & security endpoints."""

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user, get_db_session
from app.core.security import create_access_token, create_refresh_token
from app.schemas import ProfileResponse, TokenRenewResponse


router = APIRouter()


@router.get("/user/profile", response_model=ProfileResponse)
async def get_profile(current_user=Depends(get_current_user)):
    return ProfileResponse(
        telegram_id=current_user.telegram_id,
        username=current_user.username,
        first_name=current_user.first_name,
        photo_url=current_user.photo_url,
        auth_date=current_user.auth_date,
        jwt_token=current_user.jwt_token,
        two_factor_enabled=current_user.two_factor_enabled,
        last_login_ip=current_user.last_login_ip,
        last_login_device=current_user.last_login_device,
    )


@router.post("/user/token/renew", response_model=TokenRenewResponse)
async def renew_token(
    current_user=Depends(get_current_user),
    session: AsyncSession = Depends(get_db_session),
):
    access_token = create_access_token(
        subject=str(current_user.id),
        additional_claims={
            "telegram_id": current_user.telegram_id,
            "username": current_user.username,
            "role": current_user.role.value,
        },
    )
    refresh_token = create_refresh_token(subject=str(current_user.id))
    current_user.jwt_token = access_token
    await session.commit()
    return TokenRenewResponse(
        message="Token successfully renewed",
        access_token=access_token,
        refresh_token=refresh_token,
    )


@router.post("/user/logout")
async def logout(
    current_user=Depends(get_current_user),
    session: AsyncSession = Depends(get_db_session),
):
    current_user.jwt_token = None
    await session.commit()
    return {"message": "Successfully logged out"}


@router.post("/user/logout_all")
async def logout_all(
    current_user=Depends(get_current_user),
    session: AsyncSession = Depends(get_db_session),
):
    current_user.jwt_token = None
    await session.commit()
    return {"message": "All sessions terminated"}
