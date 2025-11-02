from sqlalchemy.orm import DeclarativeBase


class Base(DeclarativeBase):
    pass


# Import all models for Alembic discovery
from app.db.models.user import User  # noqa: E402,F401
from app.db.models.traffic import TrafficSession, TrafficLog, SessionReport  # noqa: E402,F401
from app.db.models.pricing import DailyPrice, PricingLog  # noqa: E402,F401
from app.db.models.notifications import DeviceRegistry, NotificationLog  # noqa: E402,F401
from app.db.models.finance import Transaction, WithdrawRequest, BalanceHistory  # noqa: E402,F401
from app.db.models.support import SupportRequest  # noqa: E402,F401
from app.db.models.content import Announcement, PromoCode  # noqa: E402,F401

