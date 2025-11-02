from datetime import datetime, timedelta

from sqlalchemy import func
from sqlalchemy.orm import Session

from app.db.models.traffic import TrafficSession
from app.schemas.session import SessionItem, SessionListResponse, SessionSummary


class SessionService:
    @staticmethod
    def list_sessions(telegram_id: int, limit: int, offset: int, db: Session) -> SessionListResponse:
        query = db.query(TrafficSession).filter(TrafficSession.telegram_id == telegram_id).order_by(TrafficSession.start_time.desc())
        total = query.count()
        rows = query.offset(offset).limit(limit).all()

        def format_duration(row: TrafficSession) -> str | None:
            if not row.end_time or not row.start_time:
                return None
            delta = row.end_time - row.start_time
            hours, remainder = divmod(int(delta.total_seconds()), 3600)
            minutes, seconds = divmod(remainder, 60)
            return f"{hours:02d}:{minutes:02d}:{seconds:02d}"

        items = [
            SessionItem(
                id=row.id,
                start_time=row.start_time,
                end_time=row.end_time,
                duration=format_duration(row),
                sent_mb=row.sent_mb,
                earned_usd=row.earned_usd,
                status=row.status,
                ip_address=row.ip_address,
                location=row.ip_country,
                device=row.network_type_client,
            )
            for row in rows
        ]
        return SessionListResponse(items=items, total=total)

    @staticmethod
    def summary(telegram_id: int, db: Session) -> SessionSummary:
        today = datetime.utcnow().date()
        week = datetime.utcnow().date() - timedelta(days=7)

        today_stats = (
            db.query(
                func.count(TrafficSession.id),
                func.sum(TrafficSession.sent_mb),
                func.sum(TrafficSession.earned_usd),
            )
            .filter(TrafficSession.telegram_id == telegram_id, func.date(TrafficSession.start_time) == today)
            .first()
        )

        week_stats = (
            db.query(
                func.count(TrafficSession.id),
                func.sum(TrafficSession.sent_mb),
                func.sum(TrafficSession.earned_usd),
            )
            .filter(TrafficSession.telegram_id == telegram_id, func.date(TrafficSession.start_time) >= week)
            .first()
        )

        total_sessions = week_stats[0] or 0
        avg_per_session = (week_stats[2] / total_sessions) if total_sessions else None

        return SessionSummary(
            today_sessions=int(today_stats[0] or 0),
            today_mb=float(today_stats[1] or 0),
            today_earnings=float(today_stats[2] or 0),
            week_sessions=int(week_stats[0] or 0),
            week_mb=float(week_stats[1] or 0),
            week_earnings=float(week_stats[2] or 0),
            average_per_session=float(avg_per_session) if avg_per_session else None,
        )

