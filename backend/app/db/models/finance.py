from __future__ import annotations

from datetime import datetime
from typing import Dict, Optional

from sqlalchemy import JSON, Boolean, DateTime, ForeignKey, Integer, Numeric, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class Transaction(Base):
    __tablename__ = "transactions"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"))
    telegram_id: Mapped[int] = mapped_column(Integer, index=True)

    type: Mapped[str] = mapped_column(String(32))  # income | withdraw | refund
    amount_usd: Mapped[float] = mapped_column(Numeric(14, 6), default=0)
    amount_usdt: Mapped[Optional[float]] = mapped_column(Numeric(14, 6))
    currency: Mapped[str] = mapped_column(String(10), default="USD")
    status: Mapped[str] = mapped_column(String(32), default="completed")
    wallet_address: Mapped[Optional[str]] = mapped_column(String(255))
    provider_payout_id: Mapped[Optional[str]] = mapped_column(String(128))
    tx_hash: Mapped[Optional[str]] = mapped_column(String(255))
    note: Mapped[Optional[str]] = mapped_column(Text)

    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow)

    user: Mapped["User"] = relationship(back_populates="transactions")


class WithdrawRequest(Base):
    __tablename__ = "withdraw_requests"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"))
    telegram_id: Mapped[int] = mapped_column(Integer, index=True)
    amount_usd: Mapped[float] = mapped_column(Numeric(14, 6))
    amount_usdt: Mapped[Optional[float]] = mapped_column(Numeric(14, 6))
    wallet_address: Mapped[str] = mapped_column(String(255))
    network: Mapped[str] = mapped_column(String(32), default="BEP20")
    status: Mapped[str] = mapped_column(String(32), default="pending")
    payout_id: Mapped[Optional[str]] = mapped_column(String(128))
    tx_hash: Mapped[Optional[str]] = mapped_column(String(255))
    provider_response: Mapped[Optional[Dict[str, str]]] = mapped_column(JSON)
    idempotency_key: Mapped[Optional[str]] = mapped_column(String(255), unique=True)
    reserved_balance: Mapped[bool] = mapped_column(Boolean, default=False)
    fee_usd: Mapped[Optional[float]] = mapped_column(Numeric(12, 6))
    note: Mapped[Optional[str]] = mapped_column(Text)

    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow)
    processed_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))

    user: Mapped["User"] = relationship(back_populates="withdraw_requests")


class BalanceHistory(Base):
    __tablename__ = "balance_history"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"))
    previous_balance: Mapped[float] = mapped_column(Numeric(18, 6), default=0)
    new_balance: Mapped[float] = mapped_column(Numeric(18, 6), default=0)
    delta: Mapped[float] = mapped_column(Numeric(18, 6), default=0)
    reason: Mapped[str] = mapped_column(String(255))
    metadata: Mapped[Optional[Dict[str, str]]] = mapped_column(JSON)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow)

    user: Mapped["User"] = relationship(back_populates="balance_history")


from app.db.models.user import User  # noqa: E402  # isort: skip

