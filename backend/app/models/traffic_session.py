"""Traffic session tracking."""

from __future__ import annotations

from datetime import datetime
from enum import Enum
from typing import Optional

from sqlalchemy import Boolean, Enum as SAEnum, Float, ForeignKey, Integer, JSON, Numeric, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base
from app.models.base import TimestampMixin


class TrafficSessionStatus(str, Enum):
    ACTIVE = "active"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class TrafficFilterStatus(str, Enum):
    PENDING = "pending"
    PASSED = "passed"
    FAILED = "failed"
    SKIPPED = "skipped"


class TrafficSession(TimestampMixin, Base):
    """Stores metadata for a user traffic sharing session."""

    __tablename__ = "traffic_sessions"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    session_id: Mapped[str] = mapped_column(String(64), unique=True, index=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"))
    user_role: Mapped[str] = mapped_column(String(16), default="user")

    start_time: Mapped[datetime] = mapped_column()
    end_time: Mapped[Optional[datetime]] = mapped_column()
    duration_seconds: Mapped[Optional[int]] = mapped_column(Integer)

    sent_mb: Mapped[float] = mapped_column(Float, default=0)
    used_mb: Mapped[float] = mapped_column(Float, default=0)
    earned_usd: Mapped[float] = mapped_column(Numeric(18, 6), default=0)

    status: Mapped[TrafficSessionStatus] = mapped_column(
        SAEnum(TrafficSessionStatus), default=TrafficSessionStatus.ACTIVE
    )

    filter_status: Mapped[TrafficFilterStatus] = mapped_column(
        SAEnum(TrafficFilterStatus), default=TrafficFilterStatus.PENDING
    )
    filter_reasons: Mapped[Optional[dict]] = mapped_column(JSON)
    ip_country: Mapped[Optional[str]] = mapped_column(String(2))
    ip_asn: Mapped[Optional[str]] = mapped_column(String(64))
    is_proxy: Mapped[Optional[bool]] = mapped_column(Boolean)
    vpn_score: Mapped[Optional[float]] = mapped_column(Float)
    network_type_client: Mapped[Optional[str]] = mapped_column(String(16))
    network_type_asn: Mapped[Optional[str]] = mapped_column(String(32))
    validated_at: Mapped[Optional[datetime]] = mapped_column()

    device_id: Mapped[Optional[str]] = mapped_column(String(128))
    client_ip: Mapped[Optional[str]] = mapped_column(String(64))
    app_version: Mapped[Optional[str]] = mapped_column(String(32))
    os: Mapped[Optional[str]] = mapped_column(String(32))
    battery_level: Mapped[Optional[int]] = mapped_column(Integer)

    pending_admin_ticket_id: Mapped[Optional[str]] = mapped_column(String(64))

    user: Mapped["User"] = relationship(back_populates="traffic_sessions")
    reports: Mapped[list["SessionReport"]] = relationship(back_populates="session")
    audit_logs: Mapped[list["TrafficFilterAudit"]] = relationship(back_populates="session")
