"""Daily price announcement model."""

from __future__ import annotations

from datetime import date

from sqlalchemy import Date, Integer, Numeric, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base
from app.models.base import TimestampMixin


class DailyPrice(TimestampMixin, Base):
    """Represents a daily traffic price announcement."""

    __tablename__ = "daily_price"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    date: Mapped[date] = mapped_column(Date, unique=True, index=True)
    price_per_gb: Mapped[float] = mapped_column(Numeric(8, 4))
    message: Mapped[str | None] = mapped_column(Text)

