"""Notification log model."""

from __future__ import annotations

from sqlalchemy import Boolean, ForeignKey, Integer, JSON, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base
from app.models.base import TimestampMixin


class NotificationLog(TimestampMixin, Base):
    """Logs notifications sent to users."""

    __tablename__ = "notification_log"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"))
    device_id: Mapped[str | None] = mapped_column(String(128))
    notif_type: Mapped[str] = mapped_column(String(64))
    title: Mapped[str] = mapped_column(String(255))
    body: Mapped[str] = mapped_column(String(1024))
    payload: Mapped[dict] = mapped_column(JSON, default=dict)
    delivered: Mapped[bool] = mapped_column(Boolean, default=False)
    opened: Mapped[bool] = mapped_column(Boolean, default=False)

    user: Mapped["User"] = relationship(backref="notifications")
