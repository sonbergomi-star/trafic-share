"""Announcement model."""

from __future__ import annotations

from sqlalchemy import Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base
from app.models.base import TimestampMixin


class Announcement(TimestampMixin, Base):
    """Admin announcements for news feed."""

    __tablename__ = "announcements"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    title: Mapped[str] = mapped_column(String(255))
    description: Mapped[str] = mapped_column(Text)
    image_url: Mapped[str | None] = mapped_column(String(255))
    link: Mapped[str | None] = mapped_column(String(255))
