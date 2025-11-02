from datetime import date, datetime
from typing import Optional

from pydantic import BaseModel

from app.schemas.base import ORMModel


class DailyPriceResponse(ORMModel):
    date: date
    price_per_gb: float
    message: Optional[str]
    change: Optional[float]


class DailyPriceAdminPayload(BaseModel):
    date: Optional[date] = None
    price_per_gb: float
    message: Optional[str] = None


class PricingLogResponse(ORMModel):
    date: date
    price_per_mb: float
    source: str
    updated_at: datetime

