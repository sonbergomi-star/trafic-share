"""Pricing schemas."""

from datetime import date
from typing import Optional

from pydantic import BaseModel


class DailyPriceResponse(BaseModel):
    date: date
    price_per_gb: float
    message: Optional[str]
    change: Optional[float]


class DailyPriceCreate(BaseModel):
    date: date
    price_per_gb: float
    message: Optional[str]
