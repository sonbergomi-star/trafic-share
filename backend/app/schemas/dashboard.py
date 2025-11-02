from datetime import datetime
from typing import Optional

from pydantic import BaseModel

from app.schemas.base import ORMModel


class DashboardUser(ORMModel):
    telegram_id: int
    first_name: Optional[str]
    username: Optional[str]
    photo_url: Optional[str]
    auth_date: Optional[datetime]


class BalanceInfo(ORMModel):
    usd: float
    converted_usdt: float
    converted_uzs: float
    last_refreshed: Optional[datetime]


class TrafficInfo(ORMModel):
    sent_mb: float
    used_mb: float
    remaining_mb: float
    current_speed: Optional[float]
    session_id: Optional[str]
    status: Optional[str]


class PricingInfo(ORMModel):
    date: Optional[datetime]
    price_per_gb: float
    message: Optional[str]
    change: Optional[float]


class MiniStats(ORMModel):
    today_earn: float
    week_earn: float
    month_earn: float
    average_speed: Optional[float]


class DashboardResponse(ORMModel):
    user: DashboardUser
    balance: BalanceInfo
    traffic: TrafficInfo
    pricing: PricingInfo
    mini_stats: MiniStats


class StartTrafficRequest(BaseModel):
    device_id: str
    client_local_ip: Optional[str] = None
    network_type: Optional[str] = None
    app_version: Optional[str] = None
    os: Optional[str] = None
    battery_level: Optional[int] = None


class StartTrafficResponse(ORMModel):
    status: str
    session_id: Optional[str]
    message: str
    bypass: Optional[bool]


class StopTrafficResponse(ORMModel):
    status: str
    session_id: Optional[str]
    sent_mb: float
    used_mb: float
    earned_usd: float


class StopTrafficRequest(BaseModel):
    session_id: str

