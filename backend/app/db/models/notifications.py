from __future__ import annotations

from datetime import datetime
from typing import Dict, Optional

from sqlalchemy import Boolean, DateTime, ForeignKey, Integer, JSON, String, Text, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class DeviceRegistry(Base):
    __tablename__ = "device_registry"
    __table_args__ = (UniqueConstraint("telegram_id", "device_id"),)

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"))
    telegram_id: Mapped[int] = mapped_column(Integer, index=True)
    device_id: Mapped[str] = mapped_column(String(128))
    platform: Mapped[str] = mapped_column(String(20))
    device_token: Mapped[str] = mapped_column(String(255))
    notifications_enabled: Mapped[bool] = mapped_column(Boolean, default=True)
    last_seen: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow)

    user: Mapped["User"] = relationship(back_populates="device_registry")


class NotificationLog(Base):
    __tablename__ = "notification_log"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    telegram_id: Mapped[int] = mapped_column(Integer, index=True)
    device_id: Mapped[Optional[str]] = mapped_column(String(128))
    notif_type: Mapped[str] = mapped_column(String(64))
    title: Mapped[Optional[str]] = mapped_column(String(255))
    body: Mapped[Optional[str]] = mapped_column(Text)
    payload: Mapped[Dict[str, str]] = mapped_column(JSON, default=dict)
    sent_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow)
    delivered: Mapped[bool] = mapped_column(Boolean, default=False)
    opened: Mapped[bool] = mapped_column(Boolean, default=False)
    error: Mapped[Optional[str]] = mapped_column(Text)


from app.db.models.user import User  # noqa: E402  # isort: skip

