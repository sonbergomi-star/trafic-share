"""Analytics schemas."""

from datetime import date

from pydantic import BaseModel


class AnalyticsSummary(BaseModel):
    sent_mb: float
    sold_mb: float
    profit_usd: float
    price_per_mb: float
    date: date


class DailyStatsResponse(BaseModel):
    items: list[AnalyticsSummary]


class WeeklyStatsResponse(BaseModel):
    items: list[AnalyticsSummary]


class MonthlyStatsResponse(BaseModel):
    items: list[AnalyticsSummary]
