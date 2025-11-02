from datetime import datetime
from typing import Dict, List, Optional

from pydantic import BaseModel

from app.schemas.base import ORMModel


class SessionReportSchema(ORMModel):
    id: int
    timestamp: datetime
    delta_mb: float
    cumulative_mb: float
    speed_mb_s: Optional[float]
    battery_level: Optional[int]
    network_type: Optional[str]
    client_ip: Optional[str]
    metadata: Dict[str, str]


class TrafficSessionSchema(ORMModel):
    id: str
    start_time: datetime
    end_time: Optional[datetime]
    status: str
    sent_mb: float
    used_mb: float
    earned_usd: float
    current_speed: Optional[float]
    network_type_client: Optional[str]
    network_type_asn: Optional[str]
    ip_address: Optional[str]
    ip_country: Optional[str]
    ip_region: Optional[str]
    filter_status: str
    filter_reasons: Optional[Dict[str, str]]
    validated_at: Optional[datetime]


class TrafficFilterAuditSchema(ORMModel):
    id: int
    telegram_id: int
    device_id: Optional[str]
    client_ip: Optional[str]
    asn: Optional[str]
    country: Optional[str]
    isp: Optional[str]
    is_proxy: Optional[bool]
    vpn_score: Optional[float]
    network_type_client: Optional[str]
    network_type_asn: Optional[str]
    check_sequence: Dict[str, str]
    final_decision: str
    reasons: Dict[str, str]
    admin_override_by: Optional[int]
    created_at: datetime


class TrafficSummary(ORMModel):
    sessions: List[TrafficSessionSchema]


class ReportIngestRequest(BaseModel):
    session_id: str
    device_id: str
    delta_mb: float
    cumulative_mb: float
    speed: Optional[float] = None
    battery_level: Optional[int] = None
    network_type: Optional[str] = None
    client_ip: Optional[str] = None
    metadata: Optional[Dict[str, str]] = None

