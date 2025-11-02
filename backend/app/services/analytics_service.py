from datetime import datetime, timedelta
from typing import Dict

from sqlalchemy import func
from sqlalchemy.orm import Session

from app.db.models.traffic import TrafficLog


class AnalyticsService:
    @staticmethod
    def daily_stats(telegram_id: int, db: Session) -> Dict[str, float]:
        today = datetime.utcnow().date()
        record = (
            db.query(
                func.sum(TrafficLog.sent_mb),
                func.sum(TrafficLog.used_mb),
                func.sum(TrafficLog.profit_usd),
                func.avg(TrafficLog.price_per_mb),
            )
            .filter(TrafficLog.telegram_id == telegram_id, TrafficLog.date == today, TrafficLog.period == "daily")
            .first()
        )
        sent, used, profit, price = record or (0, 0, 0, 0)
        return {
            "sent_mb": float(sent or 0),
            "used_mb": float(used or 0),
            "profit_usd": float(profit or 0),
            "price_per_mb": float(price or 0),
        }

    @staticmethod
    def aggregate_period(telegram_id: int, period: str, days: int, db: Session):
        since = datetime.utcnow().date() - timedelta(days=days)
        rows = (
            db.query(TrafficLog)
            .filter(TrafficLog.telegram_id == telegram_id, TrafficLog.period == period, TrafficLog.date >= since)
            .order_by(TrafficLog.date.asc())
            .all()
        )
        return rows

