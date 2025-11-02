from datetime import datetime, timedelta
from typing import List

from sqlalchemy import func
from sqlalchemy.orm import Session

from app.db.models.finance import Transaction, WithdrawRequest
from app.db.models.traffic import TrafficSession
from app.db.models.user import User
from app.schemas.admin import AdminDashboardMetric, ChartPoint, DashboardChartsResponse


class AdminService:
    @staticmethod
    def dashboard_summary(db: Session) -> AdminDashboardMetric:
        users_count = db.query(func.count(User.id)).scalar() or 0
        total_balance = db.query(func.sum(User.balance_usd)).scalar() or 0
        active_sessions = (
            db.query(func.count(TrafficSession.id)).filter(TrafficSession.status == "active").scalar() or 0
        )
        active_apis = 0  # Placeholder for API manager module
        today = datetime.utcnow().date()
        start_of_day = datetime.combine(today, datetime.min.time())
        today_withdraws = (
            db.query(func.sum(WithdrawRequest.amount_usd))
            .filter(WithdrawRequest.created_at >= start_of_day)
            .scalar()
            or 0
        )
        today_revenue = (
            db.query(func.sum(Transaction.amount_usd))
            .filter(Transaction.type == "income", Transaction.created_at >= start_of_day)
            .scalar()
            or 0
        )
        return AdminDashboardMetric(
            users=int(users_count),
            total_balance=float(total_balance),
            active_sessions=int(active_sessions),
            active_apis=int(active_apis),
            today_withdraws=float(today_withdraws),
            today_revenue=float(today_revenue),
        )

    @staticmethod
    def dashboard_charts(db: Session) -> DashboardChartsResponse:
        last_seven = datetime.utcnow() - timedelta(days=7)
        new_users = (
            db.query(func.date(User.created_at), func.count(User.id))
            .filter(User.created_at >= last_seven)
            .group_by(func.date(User.created_at))
            .all()
        )
        revenue = (
            db.query(func.date(Transaction.created_at), func.sum(Transaction.amount_usd))
            .filter(Transaction.type == "income", Transaction.created_at >= last_seven)
            .group_by(func.date(Transaction.created_at))
            .all()
        )
        traffic = (
            db.query(func.date(TrafficSession.start_time), func.sum(TrafficSession.used_mb))
            .filter(TrafficSession.start_time >= last_seven)
            .group_by(func.date(TrafficSession.start_time))
            .all()
        )

        def to_points(rows) -> List[ChartPoint]:
            return [ChartPoint(label=str(row[0]), value=float(row[1] or 0)) for row in rows]

        return DashboardChartsResponse(
            new_users=to_points(new_users),
            traffic_usage=to_points(traffic),
            revenue=to_points(revenue),
        )

