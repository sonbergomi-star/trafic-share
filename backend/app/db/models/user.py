from __future__ import annotations

from datetime import datetime
from typing import List, Optional

from sqlalchemy import Boolean, Column, DateTime, Float, Integer, Numeric, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    telegram_id: Mapped[int] = mapped_column(Integer, unique=True, nullable=False, index=True)
    username: Mapped[Optional[str]] = mapped_column(String(255), index=True)
    first_name: Mapped[Optional[str]] = mapped_column(String(255))
    photo_url: Mapped[Optional[str]] = mapped_column(Text)
    auth_date: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))

    jwt_token: Mapped[Optional[str]] = mapped_column(Text)

    balance_usd: Mapped[float] = mapped_column(Numeric(18, 6), default=0)
    sent_mb: Mapped[float] = mapped_column(Float, default=0)
    used_mb: Mapped[float] = mapped_column(Float, default=0)

    device_token: Mapped[Optional[str]] = mapped_column(String(255))
    notifications_enabled: Mapped[bool] = mapped_column(Boolean, default=True)
    session_notifications_enabled: Mapped[bool] = mapped_column(Boolean, default=True)
    system_notifications_enabled: Mapped[bool] = mapped_column(Boolean, default=True)
    last_seen: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))

    last_login_ip: Mapped[Optional[str]] = mapped_column(String(64))
    last_login_device: Mapped[Optional[str]] = mapped_column(String(128))

    role: Mapped[str] = mapped_column(String(32), default="user")
    is_banned: Mapped[bool] = mapped_column(Boolean, default=False)
    two_factor_enabled: Mapped[bool] = mapped_column(Boolean, default=False)
    language: Mapped[str] = mapped_column(String(10), default="uz")
    single_device_mode: Mapped[bool] = mapped_column(Boolean, default=False)
    battery_saver: Mapped[bool] = mapped_column(Boolean, default=False)
    theme: Mapped[str] = mapped_column(String(10), default="dark")

    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow
    )

    transactions: Mapped[List["Transaction"]] = relationship(back_populates="user", cascade="all, delete-orphan")
    withdraw_requests: Mapped[List["WithdrawRequest"]] = relationship(
        back_populates="user", cascade="all, delete-orphan"
    )
    traffic_sessions: Mapped[List["TrafficSession"]] = relationship(
        back_populates="user", cascade="all, delete-orphan"
    )
    support_requests: Mapped[List["SupportRequest"]] = relationship(
        back_populates="user", cascade="all, delete-orphan"
    )
    balance_history: Mapped[List["BalanceHistory"]] = relationship(
        back_populates="user", cascade="all, delete-orphan"
    )
    device_registry: Mapped[Optional["DeviceRegistry"]] = relationship(
        back_populates="user", uselist=False, cascade="all, delete-orphan"
    )

    def __repr__(self) -> str:  # pragma: no cover - debug helper
        return f"User(id={self.id}, telegram_id={self.telegram_id}, username={self.username!r})"


# Circular imports
from app.db.models.finance import BalanceHistory, Transaction, WithdrawRequest  # noqa: E402  # isort: skip
from app.db.models.notifications import DeviceRegistry  # noqa: E402  # isort: skip
from app.db.models.support import SupportRequest  # noqa: E402  # isort: skip
from app.db.models.traffic import TrafficSession  # noqa: E402  # isort: skip

