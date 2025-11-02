"""Dashboard aggregation service."""

from datetime import datetime, timezone

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import DailyPrice, TrafficSession, Transaction, TransactionType, User


UZS_PER_USD = 12600


class DashboardService:
    """Aggregates dashboard data for a user."""

    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def get_dashboard_data(self, user: User) -> dict:
        """Return dashboard data for the given user."""

        pricing_stmt = select(DailyPrice).order_by(DailyPrice.date.desc()).limit(2)
        pricing_result = await self.session.execute(pricing_stmt)
        prices = pricing_result.scalars().all()
        latest_price = prices[0] if prices else None
        previous_price = prices[1] if len(prices) > 1 else None

        change = None
        if latest_price and previous_price:
            change = float(latest_price.price_per_gb) - float(previous_price.price_per_gb)

        balance_usd = float(user.balance_usd or 0)
        dashboard = {
            "user": {
                "telegram_id": user.telegram_id,
                "first_name": user.first_name,
                "username": user.username,
                "photo_url": user.photo_url,
                "auth_date": user.auth_date,
            },
            "balance": {
                "usd": balance_usd,
                "converted_usdt": balance_usd * 0.9,
                "converted_uzs": balance_usd * UZS_PER_USD,
            },
            "traffic": {
                "sent_mb": user.sent_mb,
                "used_mb": user.used_mb,
                "remaining_mb": max(user.sent_mb - user.used_mb, 0),
            },
            "pricing": {
                "price_per_gb": float(latest_price.price_per_gb) if latest_price else 0,
                "message": latest_price.message if latest_price else None,
                "change": change,
            },
            "mini_stats": await self._mini_stats(user.id),
            "last_updated": datetime.now(timezone.utc),
        }
        return dashboard

    async def _mini_stats(self, user_id: int) -> dict:
        today_stmt = (
            select(func.coalesce(func.sum(Transaction.amount_usd), 0))
            .where(
                Transaction.user_id == user_id,
                Transaction.type == TransactionType.INCOME,
                func.date(Transaction.created_at) == func.current_date(),
            )
        )
        month_stmt = (
            select(func.coalesce(func.sum(Transaction.amount_usd), 0))
            .where(
                Transaction.user_id == user_id,
                Transaction.type == TransactionType.INCOME,
                func.date_trunc("month", Transaction.created_at)
                == func.date_trunc("month", func.current_timestamp()),
            )
        )

        today_value = (await self.session.execute(today_stmt)).scalar_one()
        month_value = (await self.session.execute(month_stmt)).scalar_one()

        active_sessions_stmt = (
            select(func.coalesce(func.sum(TrafficSession.earned_usd), 0))
            .where(TrafficSession.user_id == user_id, TrafficSession.status == "active")
        )
        week_stmt = (
            select(func.coalesce(func.sum(Transaction.amount_usd), 0))
            .where(
                Transaction.user_id == user_id,
                Transaction.type == TransactionType.INCOME,
                Transaction.created_at
                >= func.current_timestamp() - func.make_interval(days=7),
            )
        )

        active_value = (await self.session.execute(active_sessions_stmt)).scalar_one()
        week_value = (await self.session.execute(week_stmt)).scalar_one()

        return {
            "today_earn": float(today_value or 0),
            "week_earn": float(week_value or 0),
            "month_earn": float(month_value or 0),
            "active_sessions_estimate": float(active_value or 0),
        }
