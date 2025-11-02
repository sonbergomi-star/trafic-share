"""Support request model."""

from __future__ import annotations

from enum import Enum

from sqlalchemy import Enum as SAEnum
from sqlalchemy import ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base
from app.models.base import TimestampMixin


class SupportStatus(str, Enum):
    NEW = "new"
    READ = "read"
    REPLIED = "replied"
    CLOSED = "closed"


class SupportRequest(TimestampMixin, Base):
    """Stores support tickets submitted by users."""

    __tablename__ = "support_requests"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), index=True)
    subject: Mapped[str] = mapped_column(String(255))
    message: Mapped[str] = mapped_column(Text)
    attachment_url: Mapped[str | None] = mapped_column(String(255))
    status: Mapped[SupportStatus] = mapped_column(SAEnum(SupportStatus), default=SupportStatus.NEW)
    admin_reply: Mapped[str | None] = mapped_column(Text)

    user: Mapped["User"] = relationship(backref="support_requests")
