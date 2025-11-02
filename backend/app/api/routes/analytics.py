from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.db.session import get_db
from app.schemas.analytics import AnalyticsPoint, AnalyticsResponse
from app.services.analytics_service import AnalyticsService


router = APIRouter(prefix="/api/stats", tags=["analytics"])


@router.get("/daily/{telegram_id}", response_model=AnalyticsResponse)
def daily_stats(telegram_id: int, current_user=Depends(get_current_user), db: Session = Depends(get_db)):
    if telegram_id != current_user.telegram_id and current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Forbidden")
    data = AnalyticsService.aggregate_period(telegram_id, "daily", 1, db)
    points = [
        AnalyticsPoint(
            date=row.date,
            sent_mb=row.sent_mb,
            sold_mb=row.used_mb,
            profit_usd=row.profit_usd,
            price_per_mb=row.price_per_mb,
        )
        for row in data
    ]
    return AnalyticsResponse(period="daily", points=points)


@router.get("/weekly/{telegram_id}", response_model=AnalyticsResponse)
def weekly_stats(telegram_id: int, current_user=Depends(get_current_user), db: Session = Depends(get_db)):
    if telegram_id != current_user.telegram_id and current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Forbidden")
    data = AnalyticsService.aggregate_period(telegram_id, "weekly", 7, db)
    points = [
        AnalyticsPoint(
            date=row.date,
            sent_mb=row.sent_mb,
            sold_mb=row.used_mb,
            profit_usd=row.profit_usd,
            price_per_mb=row.price_per_mb,
        )
        for row in data
    ]
    return AnalyticsResponse(period="weekly", points=points)


@router.get("/monthly/{telegram_id}", response_model=AnalyticsResponse)
def monthly_stats(telegram_id: int, current_user=Depends(get_current_user), db: Session = Depends(get_db)):
    if telegram_id != current_user.telegram_id and current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Forbidden")
    data = AnalyticsService.aggregate_period(telegram_id, "monthly", 30, db)
    points = [
        AnalyticsPoint(
            date=row.date,
            sent_mb=row.sent_mb,
            sold_mb=row.used_mb,
            profit_usd=row.profit_usd,
            price_per_mb=row.price_per_mb,
        )
        for row in data
    ]
    return AnalyticsResponse(period="monthly", points=points)

