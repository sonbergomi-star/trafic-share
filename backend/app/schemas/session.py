"""Session schemas."""

from datetime import datetime
from typing import Optional

from pydantic import BaseModel


class SessionStartRequest(BaseModel):
    device_id: str
    client_local_ip: Optional[str]
    network_type: Optional[str]
    app_version: Optional[str]
    os: Optional[str]
    battery_level: Optional[int]


class SessionStopRequest(BaseModel):
    session_id: str


class SessionReportIn(BaseModel):
    session_id: str
    device_id: str
    sequence_number: int
    delta_mb: float
    cumulative_mb: float
    speed_mb_s: float
    battery_level: Optional[int]
    network_type: Optional[str]
    timestamp: datetime
    extra: Optional[dict] = None


class SessionReportResponse(BaseModel):
    status: str
    processed_at: datetime


class SessionDetail(BaseModel):
    session_id: str
    start_time: datetime
    end_time: Optional[datetime]
    sent_mb: float
    used_mb: float
    earned_usd: float
    status: str


class SessionListResponse(BaseModel):
    sessions: list[SessionDetail]
    total: int
