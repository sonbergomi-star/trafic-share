"""Base declarative metadata import for Alembic."""

from sqlalchemy.orm import DeclarativeBase


class Base(DeclarativeBase):
    """Declarative base class for all models."""

    pass
