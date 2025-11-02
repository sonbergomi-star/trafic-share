"""Session report model."""

from __future__ import annotations

from datetime import datetime

from sqlalchemy import Float, ForeignKey, Integer, JSON, Numeric, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base
from app.models.base import TimestampMixin


class SessionReport(TimestampMixin, Base):
    """Telemetry report messages associated with a session."""

    __tablename__ = "session_reports"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    session_id: Mapped[int] = mapped_column(ForeignKey("traffic_sessions.id", ondelete="CASCADE"))
    recorded_at: Mapped[datetime] = mapped_column()
    sequence_number: Mapped[int] = mapped_column(Integer, default=0)

    delta_mb: Mapped[float] = mapped_column(Float)
    cumulative_mb: Mapped[float] = mapped_column(Float)
    speed_mbps: Mapped[float] = mapped_column(Float)
    battery_level: Mapped[int] = mapped_column(Integer)
    network_type: Mapped[str] = mapped_column(String(32))
    data: Mapped[dict] = mapped_column(JSON, default=dict)

    session: Mapped["TrafficSession"] = relationship(back_populates="reports")
