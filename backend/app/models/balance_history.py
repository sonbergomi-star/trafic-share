"""Balance history snapshots."""

from __future__ import annotations

from sqlalchemy import ForeignKey, Integer, Numeric, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base
from app.models.base import TimestampMixin


class BalanceHistory(TimestampMixin, Base):
    """Records balance changes for audit purposes."""

    __tablename__ = "balance_history"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), index=True)
    previous_balance: Mapped[float] = mapped_column(Numeric(18, 6))
    new_balance: Mapped[float] = mapped_column(Numeric(18, 6))
    delta: Mapped[float] = mapped_column(Numeric(18, 6))
    reason: Mapped[str | None] = mapped_column(String(255))

    user: Mapped["User"] = relationship(backref="balance_history")
