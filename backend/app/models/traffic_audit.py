"""Filter audit logs."""

from __future__ import annotations

from sqlalchemy import ForeignKey, Integer, JSON, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base
from app.models.base import TimestampMixin


class TrafficFilterAudit(TimestampMixin, Base):
    """Stores audit information for traffic filter decisions."""

    __tablename__ = "traffic_filter_audit"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    session_id: Mapped[int | None] = mapped_column(
        ForeignKey("traffic_sessions.id", ondelete="SET NULL"), nullable=True
    )
    telegram_id: Mapped[int] = mapped_column()
    device_id: Mapped[str | None] = mapped_column(String(128))
    client_ip: Mapped[str | None] = mapped_column(String(64))
    asn: Mapped[str | None] = mapped_column(String(64))
    country: Mapped[str | None] = mapped_column(String(2))
    isp: Mapped[str | None] = mapped_column(String(128))
    is_proxy: Mapped[bool | None] = mapped_column()
    vpn_score: Mapped[float | None] = mapped_column()
    network_type_client: Mapped[str | None] = mapped_column(String(16))
    network_type_asn: Mapped[str | None] = mapped_column(String(32))
    check_sequence: Mapped[dict] = mapped_column(JSON, default=dict)
    final_decision: Mapped[str] = mapped_column(String(32))
    reasons: Mapped[dict] = mapped_column(JSON, default=dict)
    admin_override_by: Mapped[str | None] = mapped_column(String(64))

    session: Mapped["TrafficSession" | None] = relationship(back_populates="audit_logs")
