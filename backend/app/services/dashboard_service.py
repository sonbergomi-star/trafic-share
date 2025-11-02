from datetime import datetime, timedelta
from decimal import Decimal

from sqlalchemy.orm import Session

from app.core.config import get_settings
from app.db.models.finance import Transaction
from app.db.models.pricing import DailyPrice
from app.db.models.traffic import TrafficSession
from app.db.models.user import User
from app.schemas.dashboard import BalanceInfo, DashboardResponse, DashboardUser, MiniStats, PricingInfo, TrafficInfo


settings = get_settings()


class DashboardService:
    usd_to_usdt_ratio = Decimal("1.0")
    usd_to_uzs_rate = Decimal("12500")

    @classmethod
    def get_dashboard(cls, telegram_id: int, db: Session) -> DashboardResponse:
        user = db.query(User).filter(User.telegram_id == telegram_id).one()

        active_session = (
            db.query(TrafficSession)
            .filter(TrafficSession.telegram_id == telegram_id, TrafficSession.status.in_(["active", "pending"]))
            .order_by(TrafficSession.start_time.desc())
            .first()
        )

        latest_price = db.query(DailyPrice).order_by(DailyPrice.date.desc()).first()
        balance = cls._build_balance(user)
        traffic = cls._build_traffic(user, active_session)
        pricing = cls._build_pricing(latest_price)
        stats = cls._build_mini_stats(user, db)

        return DashboardResponse(
            user=DashboardUser.model_validate(user),
            balance=balance,
            traffic=traffic,
            pricing=pricing,
            mini_stats=stats,
        )

    @classmethod
    def _build_balance(cls, user: User) -> BalanceInfo:
        usd = float(user.balance_usd or 0)
        usdt = float((Decimal(usd) * cls.usd_to_usdt_ratio).quantize(Decimal("0.000001")))
        uzs = float((Decimal(usd) * cls.usd_to_uzs_rate).quantize(Decimal("0.01")))
        return BalanceInfo(
            usd=usd,
            converted_usdt=usdt,
            converted_uzs=uzs,
            last_refreshed=user.updated_at,
        )

    @classmethod
    def _build_traffic(cls, user: User, session: TrafficSession | None) -> TrafficInfo:
        sent = float(user.sent_mb or 0)
        used = float(user.used_mb or 0)
        remaining = max(sent - used, 0)
        return TrafficInfo(
            sent_mb=sent,
            used_mb=used,
            remaining_mb=remaining,
            current_speed=session.current_speed if session else None,
            session_id=session.id if session else None,
            status=session.status if session else None,
        )

    @classmethod
    def _build_pricing(cls, price: DailyPrice | None) -> PricingInfo:
        if not price:
            return PricingInfo(date=None, price_per_gb=settings.default_price_per_gb, message=None, change=None)
        return PricingInfo(
            date=datetime.combine(price.date, datetime.min.time()),
            price_per_gb=price.price_per_gb,
            message=price.message,
            change=price.change_delta,
        )

    @classmethod
    def _build_mini_stats(cls, user: User, db: Session) -> MiniStats:
        today = datetime.utcnow() - timedelta(days=1)
        week = datetime.utcnow() - timedelta(days=7)

        today_earn = (
            db.query(Transaction)
            .filter(Transaction.telegram_id == user.telegram_id, Transaction.created_at >= today, Transaction.type == "income")
            .with_entities(Transaction.amount_usd)
        ).all()
        today_sum = sum(float(t.amount_usd) for t in today_earn)

        week_earn = (
            db.query(Transaction)
            .filter(Transaction.telegram_id == user.telegram_id, Transaction.created_at >= week, Transaction.type == "income")
            .with_entities(Transaction.amount_usd)
        ).all()
        week_sum = sum(float(t.amount_usd) for t in week_earn)

        month_start = datetime.utcnow() - timedelta(days=30)
        month_earn = (
            db.query(Transaction)
            .filter(Transaction.telegram_id == user.telegram_id, Transaction.created_at >= month_start, Transaction.type == "income")
            .with_entities(Transaction.amount_usd)
        ).all()
        month_sum = sum(float(t.amount_usd) for t in month_earn)

        average_speed = None
        if user.traffic_sessions:
            speeds = [s.current_speed for s in user.traffic_sessions if s.current_speed]
            if speeds:
                average_speed = sum(speeds) / len(speeds)

        return MiniStats(
            today_earn=round(today_sum, 2),
            week_earn=round(week_sum, 2),
            month_earn=round(month_sum, 2),
            average_speed=average_speed,
        )

