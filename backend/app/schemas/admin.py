from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel

from app.schemas.base import ORMModel


class AdminDashboardMetric(ORMModel):
    users: int
    total_balance: float
    active_sessions: int
    active_apis: int
    today_withdraws: float
    today_revenue: float


class ChartPoint(ORMModel):
    label: str
    value: float


class DashboardChartsResponse(ORMModel):
    new_users: List[ChartPoint]
    traffic_usage: List[ChartPoint]
    revenue: List[ChartPoint]


class AdminUserActionPayload(BaseModel):
    note: Optional[str] = None
    amount: Optional[float] = None


class AdminAPIKeyPayload(BaseModel):
    user_id: int
    limit_mb: float
    expires_at: Optional[datetime] = None
    name: Optional[str] = None
    api_type: str = "traffic"


class AdminAPIKeyResponse(ORMModel):
    api_key: str
    status: str
    expires_at: Optional[datetime]


class AdminLogEntry(ORMModel):
    timestamp: datetime
    level: str
    message: str
    user_id: Optional[int]
    ip: Optional[str]


class AdminLogsResponse(ORMModel):
    items: List[AdminLogEntry]

