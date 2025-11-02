"""Daily pricing service."""

from datetime import date

import redis.asyncio as aioredis
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.models import DailyPrice
from app.schemas.pricing import DailyPriceCreate


class PricingService:
    """Handles pricing persistence and retrieval."""

    def __init__(self, session: AsyncSession, redis: aioredis.Redis | None) -> None:
        self.session = session
        self.redis = redis

    async def get_latest_price(self) -> DailyPrice | None:
        stmt = select(DailyPrice).order_by(DailyPrice.date.desc()).limit(1)
        result = await self.session.execute(stmt)
        price = result.scalar_one_or_none()
        return price

    async def create_price(self, payload: DailyPriceCreate) -> DailyPrice:
        stmt = select(DailyPrice).where(DailyPrice.date == payload.date)
        existing = (await self.session.execute(stmt)).scalar_one_or_none()
        if existing:
            existing.price_per_gb = payload.price_per_gb
            existing.message = payload.message
            await self.session.commit()
            if self.redis:
                await self.redis.delete("pricing:latest")
            return existing

        price = DailyPrice(
            date=payload.date,
            price_per_gb=payload.price_per_gb,
            message=payload.message,
        )
        self.session.add(price)
        await self.session.commit()
        if self.redis:
            await self.redis.delete("pricing:latest")
        return price

    async def price_change(self, current: DailyPrice, previous_date: date | None = None) -> float | None:
        if previous_date is None:
            previous_date = current.date
        stmt = (
            select(DailyPrice)
            .where(DailyPrice.date < previous_date)
            .order_by(DailyPrice.date.desc())
            .limit(1)
        )
        prev = (await self.session.execute(stmt)).scalar_one_or_none()
        if not prev:
            return None
        return float(current.price_per_gb) - float(prev.price_per_gb)
