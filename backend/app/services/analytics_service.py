"""Analytics computation service."""

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import TrafficSession


class AnalyticsService:
    """Aggregates traffic statistics."""

    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def daily(self, user_id: int) -> list[dict]:
        stmt = (
            select(
                func.date(TrafficSession.start_time).label("date"),
                func.sum(TrafficSession.sent_mb).label("sent_mb"),
                func.sum(TrafficSession.used_mb).label("used_mb"),
                func.sum(TrafficSession.earned_usd).label("profit_usd"),
            )
            .where(TrafficSession.user_id == user_id)
            .group_by(func.date(TrafficSession.start_time))
            .order_by(func.date(TrafficSession.start_time).desc())
            .limit(30)
        )
        rows = (await self.session.execute(stmt)).all()
        return [
            {
                "date": row.date,
                "sent_mb": float(row.sent_mb or 0),
                "sold_mb": float(row.used_mb or 0),
                "profit_usd": float(row.profit_usd or 0),
                "price_per_mb": 0.0,
            }
            for row in rows
        ]
