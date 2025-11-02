"""Device registry model."""

from __future__ import annotations

from sqlalchemy import Boolean, ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base
from app.models.base import TimestampMixin


class DeviceRegistry(TimestampMixin, Base):
    """Stores registered devices for push notifications."""

    __tablename__ = "device_registry"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"))
    device_id: Mapped[str] = mapped_column(String(128), unique=True)
    device_token: Mapped[str] = mapped_column(String(512))
    platform: Mapped[str] = mapped_column(String(16))
    notifications_enabled: Mapped[bool] = mapped_column(Boolean, default=True)

    user: Mapped["User"] = relationship(backref="devices")
