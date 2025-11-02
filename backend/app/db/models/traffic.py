from __future__ import annotations

import uuid
from datetime import datetime
from typing import Any, Dict, List, Optional

from sqlalchemy import JSON, Boolean, Date, DateTime, Float, ForeignKey, Integer, Numeric, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base

TRAFFIC_STATUSES = ("active", "completed", "failed", "cancelled", "pending")
FILTER_STATUSES = ("pending", "passed", "failed", "skipped")


class TrafficSession(Base):
    __tablename__ = "traffic_sessions"

    id: Mapped[str] = mapped_column(String(64), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"))
    telegram_id: Mapped[int] = mapped_column(Integer, index=True)

    start_time: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow)
    end_time: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))
    status: Mapped[str] = mapped_column(String(32), default="pending")

    sent_mb: Mapped[float] = mapped_column(Float, default=0)
    used_mb: Mapped[float] = mapped_column(Float, default=0)
    earned_usd: Mapped[float] = mapped_column(Numeric(18, 6), default=0)

    current_speed: Mapped[float] = mapped_column(Float, default=0)
    network_type_client: Mapped[Optional[str]] = mapped_column(String(16))
    network_type_asn: Mapped[Optional[str]] = mapped_column(String(32))

    ip_address: Mapped[Optional[str]] = mapped_column(String(64))
    ip_country: Mapped[Optional[str]] = mapped_column(String(2))
    ip_region: Mapped[Optional[str]] = mapped_column(String(64))
    ip_asn: Mapped[Optional[str]] = mapped_column(String(64))
    isp: Mapped[Optional[str]] = mapped_column(String(128))
    is_proxy: Mapped[Optional[bool]] = mapped_column(Boolean)
    vpn_score: Mapped[Optional[float]] = mapped_column(Float)

    filter_status: Mapped[str] = mapped_column(String(32), default="pending")
    filter_reasons: Mapped[Optional[Dict[str, Any]]] = mapped_column(JSON, default=dict)
    user_role: Mapped[str] = mapped_column(String(16), default="user")
    validated_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))

    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow)

    user: Mapped["User"] = relationship(back_populates="traffic_sessions")
    reports: Mapped[List["SessionReport"]] = relationship(back_populates="session", cascade="all, delete-orphan")
    audits: Mapped[List["TrafficFilterAudit"]] = relationship(
        back_populates="session", cascade="all, delete-orphan"
    )

    def add_reason(self, reason: str) -> None:
        reasons = self.filter_reasons or {}
        if "reasons" not in reasons:
            reasons["reasons"] = []
        if reason not in reasons["reasons"]:
            reasons["reasons"].append(reason)
        self.filter_reasons = reasons


class SessionReport(Base):
    __tablename__ = "session_reports"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    session_id: Mapped[str] = mapped_column(ForeignKey("traffic_sessions.id", ondelete="CASCADE"))
    timestamp: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow)
    delta_mb: Mapped[float] = mapped_column(Float, default=0)
    cumulative_mb: Mapped[float] = mapped_column(Float, default=0)
    speed_mb_s: Mapped[Optional[float]] = mapped_column(Float)
    battery_level: Mapped[Optional[int]] = mapped_column(Integer)
    network_type: Mapped[Optional[str]] = mapped_column(String(16))
    client_ip: Mapped[Optional[str]] = mapped_column(String(64))
    metadata: Mapped[Dict[str, Any]] = mapped_column(JSON, default=dict)

    session: Mapped[TrafficSession] = relationship(back_populates="reports")


class TrafficLog(Base):
    __tablename__ = "traffic_logs"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    telegram_id: Mapped[int] = mapped_column(Integer, index=True)
    period: Mapped[str] = mapped_column(String(16), index=True)
    date: Mapped[datetime] = mapped_column(Date)

    sent_mb: Mapped[float] = mapped_column(Float, default=0)
    used_mb: Mapped[float] = mapped_column(Float, default=0)
    profit_usd: Mapped[float] = mapped_column(Numeric(18, 6), default=0)
    price_per_mb: Mapped[float] = mapped_column(Float, default=0)

    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow)


class TrafficFilterAudit(Base):
    __tablename__ = "traffic_filter_audit"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    session_id: Mapped[Optional[str]] = mapped_column(ForeignKey("traffic_sessions.id", ondelete="SET NULL"))
    telegram_id: Mapped[int] = mapped_column(Integer, index=True)
    device_id: Mapped[Optional[str]] = mapped_column(String(128))
    client_ip: Mapped[Optional[str]] = mapped_column(String(64))
    asn: Mapped[Optional[str]] = mapped_column(String(64))
    country: Mapped[Optional[str]] = mapped_column(String(2))
    isp: Mapped[Optional[str]] = mapped_column(String(128))
    is_proxy: Mapped[Optional[bool]] = mapped_column(Boolean)
    vpn_score: Mapped[Optional[float]] = mapped_column(Float)
    network_type_client: Mapped[Optional[str]] = mapped_column(String(16))
    network_type_asn: Mapped[Optional[str]] = mapped_column(String(32))
    check_sequence: Mapped[Dict[str, Any]] = mapped_column(JSON, default=dict)
    final_decision: Mapped[str] = mapped_column(String(32))
    reasons: Mapped[Dict[str, Any]] = mapped_column(JSON, default=dict)
    admin_override_by: Mapped[Optional[int]] = mapped_column(Integer)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow)

    session: Mapped[Optional[TrafficSession]] = relationship(back_populates="audits")


# Circular import guard
from app.db.models.user import User  # noqa: E402  # isort: skip

