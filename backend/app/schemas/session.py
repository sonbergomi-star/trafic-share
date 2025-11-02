from datetime import datetime
from typing import List, Optional

from app.schemas.base import ORMModel


class SessionItem(ORMModel):
    id: str
    start_time: datetime
    end_time: Optional[datetime]
    duration: Optional[str]
    sent_mb: float
    earned_usd: float
    status: str
    ip_address: Optional[str]
    location: Optional[str]
    device: Optional[str]


class SessionListResponse(ORMModel):
    items: List[SessionItem]
    total: int


class SessionSummary(ORMModel):
    today_sessions: int
    today_mb: float
    today_earnings: float
    week_sessions: int
    week_mb: float
    week_earnings: float
    average_per_session: Optional[float]

