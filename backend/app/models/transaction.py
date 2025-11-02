"""Transaction model."""

from __future__ import annotations

from enum import Enum

from sqlalchemy import Enum as SAEnum
from sqlalchemy import ForeignKey, Integer, Numeric, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base
from app.models.base import TimestampMixin


class TransactionType(str, Enum):
    INCOME = "income"
    WITHDRAW = "withdraw"
    REFUND = "refund"


class TransactionStatus(str, Enum):
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"


class Transaction(TimestampMixin, Base):
    """Tracks balance-affecting transactions."""

    __tablename__ = "transactions"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), index=True)
    type: Mapped[TransactionType] = mapped_column(SAEnum(TransactionType), nullable=False)
    amount_usd: Mapped[float] = mapped_column(Numeric(18, 6))
    amount_usdt: Mapped[float | None] = mapped_column(Numeric(18, 6))
    currency: Mapped[str] = mapped_column(String(8), default="USD")
    status: Mapped[TransactionStatus] = mapped_column(
        SAEnum(TransactionStatus), default=TransactionStatus.COMPLETED
    )
    note: Mapped[str | None] = mapped_column(Text)

    user: Mapped["User"] = relationship(back_populates="transactions")
