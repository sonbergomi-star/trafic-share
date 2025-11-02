"""Dashboard response schema."""

from datetime import datetime
from typing import Optional

from pydantic import BaseModel


class DashboardBalance(BaseModel):
    usd: float
    converted_usdt: float
    converted_uzs: Optional[float]


class DashboardTraffic(BaseModel):
    sent_mb: float
    used_mb: float
    remaining_mb: float


class DashboardPricing(BaseModel):
    price_per_gb: float
    message: Optional[str]
    change: Optional[float]


class DashboardMiniStats(BaseModel):
    today_earn: float
    week_earn: float
    month_earn: float


class DashboardResponse(BaseModel):
    user: dict
    balance: DashboardBalance
    traffic: DashboardTraffic
    pricing: DashboardPricing
    mini_stats: DashboardMiniStats
    last_updated: datetime
