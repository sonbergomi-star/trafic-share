"""Pricing tasks."""

import asyncio
from datetime import date

from app.core.celery_app import celery_app
from app.db.session import async_session_factory
from app.schemas.pricing import DailyPriceCreate
from app.services.pricing_service import PricingService


@celery_app.task(name="app.tasks.pricing.publish")
def publish_daily_price(payload: dict) -> dict:
    async def _run() -> dict:
        async with async_session_factory() as session:
            service = PricingService(session, None)
            price = await service.create_price(DailyPriceCreate(**payload))
            return {"date": str(price.date), "price_per_gb": float(price.price_per_gb)}

    return asyncio.run(_run())
