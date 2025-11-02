from __future__ import annotations

from datetime import datetime, date
from typing import Optional

from sqlalchemy import Date, DateTime, Float, Integer, String, Text, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class DailyPrice(Base):
    __tablename__ = "daily_price"
    __table_args__ = (UniqueConstraint("date"),)

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    date: Mapped[date] = mapped_column(Date, nullable=False)
    price_per_gb: Mapped[float] = mapped_column(Float, nullable=False)
    message: Mapped[Optional[str]] = mapped_column(Text)
    change_delta: Mapped[Optional[float]] = mapped_column(Float)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow)


class PricingLog(Base):
    __tablename__ = "pricing_logs"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    date: Mapped[date] = mapped_column(Date, nullable=False)
    price_per_mb: Mapped[float] = mapped_column(Float, nullable=False)
    source: Mapped[str] = mapped_column(String(50))
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow)

