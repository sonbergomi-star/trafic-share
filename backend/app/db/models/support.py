from __future__ import annotations

from datetime import datetime
from typing import Optional

from sqlalchemy import DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class SupportRequest(Base):
    __tablename__ = "support_requests"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"))
    telegram_id: Mapped[int] = mapped_column(Integer, index=True)
    subject: Mapped[str] = mapped_column(String(255))
    message: Mapped[str] = mapped_column(Text)
    attachment_url: Mapped[Optional[str]] = mapped_column(String(255))
    status: Mapped[str] = mapped_column(String(32), default="new")
    admin_reply: Mapped[Optional[str]] = mapped_column(Text)
    reply_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow)

    user: Mapped["User"] = relationship(back_populates="support_requests")


from app.db.models.user import User  # noqa: E402  # isort: skip

