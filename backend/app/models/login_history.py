"""Login history model."""

from __future__ import annotations

from sqlalchemy import ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base
from app.models.base import TimestampMixin


class LoginHistory(TimestampMixin, Base):
    """Tracks recent user login events."""

    __tablename__ = "login_history"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), index=True)
    city: Mapped[str | None] = mapped_column(String(64))
    device: Mapped[str | None] = mapped_column(String(128))
    ip_address: Mapped[str | None] = mapped_column(String(64))

    user: Mapped["User"] = relationship(backref="login_history")
