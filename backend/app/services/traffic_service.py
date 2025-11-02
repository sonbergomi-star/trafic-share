from __future__ import annotations

from datetime import datetime
from typing import Optional

from sqlalchemy.orm import Session

from app.core.config import get_settings
from app.db.models.finance import BalanceHistory, Transaction
from app.db.models.traffic import SessionReport, TrafficFilterAudit, TrafficSession
from app.db.models.user import User
from app.schemas.dashboard import StartTrafficRequest
from app.schemas.traffic import ReportIngestRequest
from app.services.pricing_service import PricingService


settings = get_settings()


class TrafficService:
    @staticmethod
    def start_session(user: User, payload: StartTrafficRequest, db: Session) -> TrafficSession:
        if user.is_banned:
            raise PermissionError("User is banned")

        is_admin = user.role == "admin" or user.telegram_id in settings.admin_id_set

        session = TrafficSession(
            user_id=user.id,
            telegram_id=user.telegram_id,
            status="active" if is_admin else "active",
            network_type_client=payload.network_type,
            filter_status="skipped" if is_admin else "passed",
            filter_reasons={"reasons": ["admin_bypass"]} if is_admin else {},
            user_role=user.role,
            validated_at=datetime.utcnow(),
        )

        db.add(session)
        db.commit()
        db.refresh(session)

        audit = TrafficFilterAudit(
            session_id=session.id,
            telegram_id=user.telegram_id,
            device_id=payload.device_id,
            final_decision="allow" if session.filter_status in ("passed", "skipped") else "deny",
            reasons=session.filter_reasons or {},
            check_sequence={"network_type": payload.network_type or "unknown"},
        )
        db.add(audit)
        db.commit()

        return session

    @staticmethod
    def stop_session(session_id: str, db: Session) -> TrafficSession:
        session = db.get(TrafficSession, session_id)
        if not session:
            raise ValueError("Session not found")

        if session.status not in ("active", "pending"):
            return session

        session.status = "completed"
        session.end_time = datetime.utcnow()

        earnings = PricingService.compute_earnings_mb(session.used_mb, db)
        session.earned_usd = earnings

        user = session.user
        previous_balance = float(user.balance_usd or 0)
        user.balance_usd = (user.balance_usd or 0) + earnings
        user.used_mb = (user.used_mb or 0) + session.used_mb
        user.sent_mb = (user.sent_mb or 0) + session.sent_mb

        transaction = Transaction(
            user_id=user.id,
            telegram_id=user.telegram_id,
            type="income",
            amount_usd=earnings,
            status="completed",
            note=f"Session {session.id} earnings",
        )
        db.add(transaction)

        history = BalanceHistory(
            user_id=user.id,
            previous_balance=previous_balance,
            new_balance=user.balance_usd,
            delta=earnings,
            reason=f"session:{session.id}",
        )
        db.add(history)

        db.commit()
        db.refresh(session)
        return session

    @staticmethod
    def ingest_report(payload: ReportIngestRequest, db: Session) -> SessionReport:
        session = db.get(TrafficSession, payload.session_id)
        if not session:
            raise ValueError("Session not found")

        session.sent_mb = (session.sent_mb or 0) + payload.delta_mb
        session.used_mb = payload.cumulative_mb
        session.current_speed = payload.speed or session.current_speed
        session.updated_at = datetime.utcnow()

        report = SessionReport(
            session_id=session.id,
            delta_mb=payload.delta_mb,
            cumulative_mb=payload.cumulative_mb,
            speed_mb_s=payload.speed,
            battery_level=payload.battery_level,
            network_type=payload.network_type,
            client_ip=payload.client_ip,
            metadata=payload.metadata or {},
        )
        db.add(report)
        db.commit()
        db.refresh(report)
        return report

