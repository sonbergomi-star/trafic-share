from datetime import date
from typing import List

from app.schemas.base import ORMModel


class AnalyticsPoint(ORMModel):
    date: date
    sent_mb: float
    sold_mb: float
    profit_usd: float
    price_per_mb: float


class AnalyticsResponse(ORMModel):
    period: str
    points: List[AnalyticsPoint]

