"""Promo code model."""

from __future__ import annotations

from datetime import datetime

from sqlalchemy import Boolean, DateTime, Integer, Numeric, String
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base
from app.models.base import TimestampMixin


class PromoCode(TimestampMixin, Base):
    """Represents a promo code with bonus percentage."""

    __tablename__ = "promo_codes"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    code: Mapped[str] = mapped_column(String(64), unique=True, index=True)
    bonus_percent: Mapped[float] = mapped_column(Numeric(5, 2))
    expires_at: Mapped[datetime | None] = mapped_column(DateTime)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
