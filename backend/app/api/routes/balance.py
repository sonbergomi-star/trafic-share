"""Balance APIs."""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user, get_db_session
from app.models import User
from app.schemas import BalanceRefreshRequest, BalanceResponse
from app.services.balance_service import BalanceService


router = APIRouter()


@router.get("/user/balance/{telegram_id}", response_model=BalanceResponse)
async def get_balance(
    telegram_id: int,
    session: AsyncSession = Depends(get_db_session),
    current_user=Depends(get_current_user),
):
    target_user = current_user
    if current_user.telegram_id != telegram_id:
        if current_user.role.value != "admin":
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="forbidden")
        stmt = select(User).where(User.telegram_id == telegram_id)
        target_user = (await session.execute(stmt)).scalar_one_or_none()
        if target_user is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="user_not_found")

    service = BalanceService(session)
    return await service.get_balance_snapshot(target_user)


@router.post("/user/refresh_balance")
async def refresh_balance(
    payload: BalanceRefreshRequest,
    session: AsyncSession = Depends(get_db_session),
    current_user=Depends(get_current_user),
):
    if current_user.telegram_id != payload.telegram_id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="forbidden")
    service = BalanceService(session)
    return await service.refresh_balance(current_user)
