"""User model."""

from __future__ import annotations

from datetime import datetime
from enum import Enum
from typing import List, Optional

from sqlalchemy import BigInteger, Boolean, Float, Integer, Numeric, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base
from app.models.base import TimestampMixin


class UserRole(str, Enum):
    USER = "user"
    ADMIN = "admin"
    MODERATOR = "moderator"


class User(TimestampMixin, Base):
    """Telegram-authenticated user profile."""

    __tablename__ = "users"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    telegram_id: Mapped[int] = mapped_column(BigInteger, unique=True, index=True)
    username: Mapped[Optional[str]] = mapped_column(String(255))
    first_name: Mapped[Optional[str]] = mapped_column(String(255))
    photo_url: Mapped[Optional[str]] = mapped_column(Text)
    auth_date: Mapped[Optional[datetime]] = mapped_column()
    jwt_token: Mapped[Optional[str]] = mapped_column(Text)

    balance_usd: Mapped[float] = mapped_column(Numeric(18, 6), default=0)
    sent_mb: Mapped[float] = mapped_column(Float, default=0)
    used_mb: Mapped[float] = mapped_column(Float, default=0)

    device_token: Mapped[Optional[str]] = mapped_column(String(255))
    notifications_enabled: Mapped[bool] = mapped_column(Boolean, default=True)
    last_seen: Mapped[Optional[datetime]] = mapped_column()

    role: Mapped[UserRole] = mapped_column(default=UserRole.USER)
    two_factor_enabled: Mapped[bool] = mapped_column(Boolean, default=False)
    last_login_ip: Mapped[Optional[str]] = mapped_column(String(64))
    last_login_device: Mapped[Optional[str]] = mapped_column(String(128))

    traffic_sessions: Mapped[List["TrafficSession"]] = relationship(back_populates="user")
    transactions: Mapped[List["Transaction"]] = relationship(back_populates="user")
    withdraw_requests: Mapped[List["WithdrawRequest"]] = relationship(back_populates="user")
    settings: Mapped[Optional["UserSettings"]] = relationship(back_populates="user", uselist=False)

