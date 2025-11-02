"""Withdraw request model."""

from __future__ import annotations

from datetime import datetime

from enum import Enum

from sqlalchemy import Boolean, Enum as SAEnum, ForeignKey, Integer, JSON, Numeric, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base
from app.models.base import TimestampMixin


class WithdrawStatus(str, Enum):
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELED = "canceled"


class WithdrawRequest(TimestampMixin, Base):
    """Stores withdraw requests awaiting payout."""

    __tablename__ = "withdraw_requests"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), index=True)
    amount_usd: Mapped[float] = mapped_column(Numeric(18, 6))
    amount_usdt: Mapped[float | None] = mapped_column(Numeric(18, 6))
    wallet_address: Mapped[str] = mapped_column(String(128))
    network: Mapped[str] = mapped_column(String(32), default="BEP20")
    status: Mapped[WithdrawStatus] = mapped_column(
        SAEnum(WithdrawStatus), default=WithdrawStatus.PENDING
    )
    payout_id: Mapped[str | None] = mapped_column(String(128))
    tx_hash: Mapped[str | None] = mapped_column(String(128))
    provider_response: Mapped[dict | None] = mapped_column(JSON)
    idempotency_key: Mapped[str | None] = mapped_column(String(128), unique=True)
    reserved_balance: Mapped[bool] = mapped_column(Boolean, default=False)
    fee_usd: Mapped[float | None] = mapped_column(Numeric(18, 6))
    note: Mapped[str | None] = mapped_column(Text)

    processed_at: Mapped[datetime | None] = mapped_column()

    user: Mapped["User"] = relationship(back_populates="withdraw_requests")
