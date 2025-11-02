"""Traffic session orchestration service."""

import uuid
from datetime import datetime, timezone
from typing import Optional

import redis.asyncio as aioredis
from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.models import (
    TrafficFilterAudit,
    TrafficFilterStatus,
    TrafficSession,
    TrafficSessionStatus,
    User,
)
from app.schemas.session import SessionReportIn, SessionStartRequest


class TrafficService:
    """Handles session start, stop, and telemetry logic."""

    def __init__(self, session: AsyncSession, redis: aioredis.Redis) -> None:
        self.session = session
        self.redis = redis

    async def start_session(
        self,
        user: User,
        payload: SessionStartRequest,
        client_ip: Optional[str],
    ) -> dict:
        """Start a traffic session after applying filters."""

        if await self._is_rate_limited(user):
            raise HTTPException(status_code=status.HTTP_429_TOO_MANY_REQUESTS, detail="rate_limited")

        bypass = user.role.value == "admin"
        decision = {
            "status": "passed" if bypass else "passed",
            "reasons": [],
            "final_decision": "allow" if bypass else "allow",
        }

        if not bypass:
            decision = await self._run_filters(user, payload, client_ip)
            if decision["final_decision"] == "deny":
                await self._write_audit(user, payload, client_ip, decision)
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail={"status": "blocked", "reasons": decision["reasons"]},
                )

        session_id = f"sess_{uuid.uuid4().hex[:12]}"
        now = datetime.now(timezone.utc)
        db_session = TrafficSession(
            session_id=session_id,
            user_id=user.id,
            user_role=user.role.value,
            start_time=now,
            status=TrafficSessionStatus.ACTIVE,
            filter_status=TrafficFilterStatus.SKIPPED if bypass else TrafficFilterStatus.PASSED,
            filter_reasons={"reasons": decision["reasons"]} if decision["reasons"] else None,
            device_id=payload.device_id,
            client_ip=client_ip,
            network_type_client=payload.network_type,
            app_version=payload.app_version,
            os=payload.os,
            battery_level=payload.battery_level,
        )
        self.session.add(db_session)
        await self.session.flush()

        await self._write_audit(user, payload, client_ip, decision, db_session.id)
        await self._increment_attempt(user)
        await self.session.commit()

        return {"status": "ok", "session_id": session_id, "message": "Tunnel opened"}

    async def stop_session(self, user: User, session_id: str) -> dict:
        """Stop an active session and finalize metrics."""

        stmt = select(TrafficSession).where(
            TrafficSession.session_id == session_id,
            TrafficSession.user_id == user.id,
        )
        db_session = (await self.session.execute(stmt)).scalar_one_or_none()
        if db_session is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="session_not_found")

        if db_session.status != TrafficSessionStatus.ACTIVE:
            return {"status": "ok", "session_id": session_id}

        now = datetime.now(timezone.utc)
        db_session.end_time = now
        db_session.status = TrafficSessionStatus.COMPLETED
        if db_session.start_time:
            db_session.duration_seconds = int((now - db_session.start_time).total_seconds())

        await self.session.commit()
        return {"status": "ok", "session_id": session_id, "message": "Session stopped"}

    async def record_report(self, user: User, payload: SessionReportIn) -> dict:
        """Record telemetry report for a session."""

        stmt = select(TrafficSession).where(
            TrafficSession.session_id == payload.session_id,
            TrafficSession.user_id == user.id,
        )
        db_session = (await self.session.execute(stmt)).scalar_one_or_none()
        if db_session is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="session_not_found")

        # Update aggregates
        db_session.sent_mb += payload.delta_mb
        db_session.used_mb = max(db_session.used_mb, payload.cumulative_mb)
        await self.session.commit()

        return {"status": "accepted", "processed_at": datetime.now(timezone.utc)}

    async def _run_filters(
        self, user: User, payload: SessionStartRequest, client_ip: Optional[str]
    ) -> dict:
        reasons: list[str] = []
        final_decision = "allow"

        if not client_ip:
            reasons.append("ip_unknown")
            final_decision = "deny"

        network_allowed = payload.network_type in settings.allowed_network_types
        if not network_allowed:
            reasons.append("network_not_allowed")
            final_decision = "deny"

        await self.redis.hset(
            "session_policy:last_seen",
            mapping={
                str(user.telegram_id): datetime.now(timezone.utc).isoformat(),
            },
        )
        return {"reasons": reasons, "final_decision": final_decision}

    async def _write_audit(
        self,
        user: User,
        payload: SessionStartRequest,
        client_ip: Optional[str],
        decision: dict,
        session_db_id: Optional[int] = None,
    ) -> None:
        audit = TrafficFilterAudit(
            session_id=session_db_id,
            telegram_id=user.telegram_id,
            device_id=payload.device_id,
            client_ip=client_ip,
            check_sequence={"network_type": payload.network_type},
            final_decision=decision.get("final_decision", "allow"),
            reasons={"codes": decision.get("reasons", [])},
        )
        self.session.add(audit)

    async def _increment_attempt(self, user: User) -> None:
        key = f"traffic:start_attempts:{user.telegram_id}:{datetime.now().date()}"
        current = await self.redis.incr(key)
        if current == 1:
            await self.redis.expire(key, 86400)

    async def _is_rate_limited(self, user: User) -> bool:
        key = f"traffic:start_attempts:{user.telegram_id}:{datetime.now().date()}"
        current = await self.redis.get(key)
        return current is not None and int(current) >= settings.max_start_attempts_per_day
