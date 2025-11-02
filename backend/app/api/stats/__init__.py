from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from datetime import datetime, timedelta, date
from pydantic import BaseModel

from app.core.database import get_db
from app.models.pricing import TrafficLog
from app.models.session import Session


router = APIRouter()


@router.get("/daily/{telegram_id}")
async def get_daily_stats(telegram_id: int, db: AsyncSession = Depends(get_db)):
    """
    Get daily statistics
    """
    today = date.today()
    
    # Get today's traffic logs
    result = await db.execute(
        select(TrafficLog)
        .where(TrafficLog.telegram_id == telegram_id)
        .where(TrafficLog.date == today)
        .where(TrafficLog.period == 'daily')
    )
    log = result.scalar_one_or_none()
    
    if not log:
        return {
            "date": today.isoformat(),
            "sent_mb": 0.0,
            "sold_mb": 0.0,
            "profit_usd": 0.0,
            "price_per_mb": 0.0,
        }
    
    return {
        "date": log.date.isoformat(),
        "sent_mb": log.sent_mb,
        "sold_mb": log.sold_mb,
        "profit_usd": log.profit_usd,
        "price_per_mb": log.price_per_mb,
    }


@router.get("/weekly/{telegram_id}")
async def get_weekly_stats(telegram_id: int, db: AsyncSession = Depends(get_db)):
    """
    Get weekly statistics
    """
    today = date.today()
    week_ago = today - timedelta(days=7)
    
    result = await db.execute(
        select(
            func.sum(TrafficLog.sent_mb).label('total_sent'),
            func.sum(TrafficLog.sold_mb).label('total_sold'),
            func.sum(TrafficLog.profit_usd).label('total_profit'),
            func.avg(TrafficLog.price_per_mb).label('avg_price'),
        )
        .where(TrafficLog.telegram_id == telegram_id)
        .where(TrafficLog.date >= week_ago)
        .where(TrafficLog.period == 'daily')
    )
    stats = result.one()
    
    return {
        "period": "last_7_days",
        "sent_mb": float(stats.total_sent or 0.0),
        "sold_mb": float(stats.total_sold or 0.0),
        "profit_usd": float(stats.total_profit or 0.0),
        "avg_price_per_mb": float(stats.avg_price or 0.0),
    }


@router.get("/monthly/{telegram_id}")
async def get_monthly_stats(telegram_id: int, db: AsyncSession = Depends(get_db)):
    """
    Get monthly statistics
    """
    today = date.today()
    month_start = date(today.year, today.month, 1)
    
    result = await db.execute(
        select(
            func.sum(TrafficLog.sent_mb).label('total_sent'),
            func.sum(TrafficLog.sold_mb).label('total_sold'),
            func.sum(TrafficLog.profit_usd).label('total_profit'),
            func.avg(TrafficLog.price_per_mb).label('avg_price'),
        )
        .where(TrafficLog.telegram_id == telegram_id)
        .where(TrafficLog.date >= month_start)
        .where(TrafficLog.period == 'daily')
    )
    stats = result.one()
    
    return {
        "period": f"{today.year}-{today.month:02d}",
        "sent_mb": float(stats.total_sent or 0.0),
        "sold_mb": float(stats.total_sold or 0.0),
        "profit_usd": float(stats.total_profit or 0.0),
        "avg_price_per_mb": float(stats.avg_price or 0.0),
    }
