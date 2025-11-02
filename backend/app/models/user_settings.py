"""User settings."""

from __future__ import annotations

from sqlalchemy import Boolean, ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base
from app.models.base import TimestampMixin


class UserSettings(TimestampMixin, Base):
    """Stores customizable user settings."""

    __tablename__ = "user_settings"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), unique=True)
    language: Mapped[str] = mapped_column(String(10), default="uz")
    push_notifications: Mapped[bool] = mapped_column(Boolean, default=True)
    session_updates: Mapped[bool] = mapped_column(Boolean, default=True)
    system_updates: Mapped[bool] = mapped_column(Boolean, default=True)
    two_factor_enabled: Mapped[bool] = mapped_column(Boolean, default=False)
    single_device_mode: Mapped[bool] = mapped_column(Boolean, default=False)
    battery_saver: Mapped[bool] = mapped_column(Boolean, default=False)
    theme: Mapped[str] = mapped_column(String(16), default="light")

    user: Mapped["User"] = relationship(back_populates="settings")
