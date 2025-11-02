from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime


class SessionBase(BaseModel):
    """Base session schema"""
    session_id: str


class SessionCreate(BaseModel):
    """Session creation schema"""
    telegram_id: int
    ip_address: Optional[str] = None
    location: Optional[str] = None
    device_info: Optional[dict] = None


class SessionStart(BaseModel):
    """Session start request"""
    ip_address: Optional[str] = None
    location: Optional[str] = None
    device_info: Optional[str] = None
    network_type: Optional[str] = None


class SessionUpdate(BaseModel):
    """Session update schema"""
    sent_mb: Optional[float] = None
    earned_usd: Optional[float] = None
    status: Optional[str] = None


class SessionReport(BaseModel):
    """Session traffic report"""
    session_id: str
    cumulative_mb: float = Field(..., gt=0)
    delta_mb: float = Field(..., ge=0)


class SessionResponse(BaseModel):
    """Session response schema"""
    id: int
    session_id: str
    telegram_id: int
    start_time: Optional[datetime]
    end_time: Optional[datetime]
    duration: Optional[str]
    is_active: bool
    status: str
    ip_address: Optional[str]
    location: Optional[str]
    sent_mb: float
    local_counted_mb: float
    server_counted_mb: float
    earned_usd: float
    created_at: datetime
    
    class Config:
        from_attributes = True


class SessionStatsResponse(BaseModel):
    """Session statistics response"""
    total_sessions: int
    active_sessions: int
    completed_sessions: int
    total_mb_sent: float
    total_earned: float
    avg_duration: str
    success_rate: float
