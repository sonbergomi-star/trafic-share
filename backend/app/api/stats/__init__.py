from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from datetime import date, timedelta
import logging

from app.core.database import get_db
from app.middleware.auth import get_current_user
from app.models.user import User
from app.services.analytics_service import AnalyticsService

logger = logging.getLogger(__name__)

router = APIRouter()


@router.get("/")
async def get_statistics(
    period: str = Query("week", regex="^(today|week|month|year)$"),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    REAL statistics calculation from database
    """
    analytics_service = AnalyticsService(db)
    
    try:
        stats = await analytics_service.get_user_analytics(
            telegram_id=current_user.telegram_id,
            period=period
        )
        
        return {
            "status": "success",
            "data": stats
        }
    
    except Exception as e:
        logger.error(f"Failed to get statistics: {e}")
        raise HTTPException(status_code=500, detail="Failed to retrieve statistics")


@router.get("/summary")
async def get_statistics_summary(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    REAL quick statistics summary
    """
    analytics_service = AnalyticsService(db)
    
    try:
        # Get today, week, and month stats in parallel
        today_stats = await analytics_service.get_user_analytics(current_user.telegram_id, "today")
        week_stats = await analytics_service.get_user_analytics(current_user.telegram_id, "week")
        month_stats = await analytics_service.get_user_analytics(current_user.telegram_id, "month")
        
        return {
            "status": "success",
            "data": {
                "today": {
                    "sessions": today_stats['summary']['total_sessions'],
                    "earned": today_stats['summary']['total_earned_usd'],
                    "traffic_mb": today_stats['summary']['total_sent_mb'],
                },
                "week": {
                    "sessions": week_stats['summary']['total_sessions'],
                    "earned": week_stats['summary']['total_earned_usd'],
                    "traffic_mb": week_stats['summary']['total_sent_mb'],
                },
                "month": {
                    "sessions": month_stats['summary']['total_sessions'],
                    "earned": month_stats['summary']['total_earned_usd'],
                    "traffic_mb": month_stats['summary']['total_sent_mb'],
                },
                "success_rate": week_stats['summary']['success_rate'],
                "avg_duration": week_stats['summary']['avg_duration'],
            }
        }
    
    except Exception as e:
        logger.error(f"Failed to get summary: {e}")
        raise HTTPException(status_code=500, detail="Failed to retrieve summary")


@router.get("/hourly")
async def get_hourly_distribution(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    REAL hourly distribution of sessions
    """
    analytics_service = AnalyticsService(db)
    
    try:
        result = await analytics_service.get_hourly_distribution(
            telegram_id=current_user.telegram_id
        )
        
        return {
            "status": "success",
            "data": result
        }
    
    except Exception as e:
        logger.error(f"Failed to get hourly distribution: {e}")
        raise HTTPException(status_code=500, detail="Failed to retrieve hourly distribution")


@router.get("/trends")
async def get_traffic_trends(
    days: int = Query(30, ge=1, le=365),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    REAL traffic trends over time
    """
    analytics_service = AnalyticsService(db)
    
    try:
        result = await analytics_service.get_traffic_trends(days=days)
        
        return {
            "status": "success",
            "data": result
        }
    
    except Exception as e:
        logger.error(f"Failed to get trends: {e}")
        raise HTTPException(status_code=500, detail="Failed to retrieve trends")


@router.get("/report")
async def generate_report(
    start_date: date = Query(...),
    end_date: date = Query(...),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    REAL generate custom date range report
    """
    # Validate date range
    if start_date > end_date:
        raise HTTPException(status_code=400, detail="Start date must be before end date")
    
    if (end_date - start_date).days > 365:
        raise HTTPException(status_code=400, detail="Date range cannot exceed 365 days")
    
    analytics_service = AnalyticsService(db)
    
    try:
        report = await analytics_service.generate_user_report(
            telegram_id=current_user.telegram_id,
            start_date=start_date,
            end_date=end_date
        )
        
        return {
            "status": "success",
            "data": report
        }
    
    except Exception as e:
        logger.error(f"Failed to generate report: {e}")
        raise HTTPException(status_code=500, detail="Failed to generate report")
