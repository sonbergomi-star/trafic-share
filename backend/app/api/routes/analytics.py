"""Analytics routes."""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user, get_db_session
from app.models import User
from app.schemas import DailyStatsResponse
from app.services.analytics_service import AnalyticsService


router = APIRouter()


@router.get("/stats/daily/{telegram_id}", response_model=DailyStatsResponse)
async def daily_stats(
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

    service = AnalyticsService(session)
    items = await service.daily(target_user.id)
    return DailyStatsResponse(items=items)
