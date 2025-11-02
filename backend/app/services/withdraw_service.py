"""Withdraw workflow service."""

from datetime import datetime, timezone
from typing import Optional

import redis.asyncio as aioredis
from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.models import Transaction, TransactionStatus, TransactionType, User, WithdrawRequest, WithdrawStatus
from app.schemas.withdraw import WithdrawRequestCreate


class WithdrawService:
    """Creates and manages withdraw requests."""

    def __init__(self, session: AsyncSession, redis: aioredis.Redis) -> None:
        self.session = session
        self.redis = redis

    async def create_withdraw(self, user: User, payload: WithdrawRequestCreate) -> WithdrawRequest:
        await self._enforce_limits(user)

        if payload.amount_usd < settings.min_withdraw_usd:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="below_minimum")
        if payload.amount_usd > settings.max_withdraw_usd:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="above_maximum")
        if float(user.balance_usd or 0) < payload.amount_usd:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="insufficient_balance")

        existing = None
        if payload.idempotency_key:
            existing_stmt = select(WithdrawRequest).where(
                WithdrawRequest.idempotency_key == payload.idempotency_key
            )
            existing = (await self.session.execute(existing_stmt)).scalar_one_or_none()
            if existing:
                return existing

        user.balance_usd = float(user.balance_usd or 0) - payload.amount_usd

        withdraw = WithdrawRequest(
            user_id=user.id,
            amount_usd=payload.amount_usd,
            wallet_address=payload.wallet_address,
            network=payload.network,
            status=WithdrawStatus.PENDING,
            idempotency_key=payload.idempotency_key,
            reserved_balance=True,
        )
        transaction = Transaction(
            user_id=user.id,
            type=TransactionType.WITHDRAW,
            amount_usd=payload.amount_usd,
            status=TransactionStatus.PENDING,
            note="Withdraw request created",
        )
        self.session.add_all([withdraw, transaction])
        await self.session.commit()
        new_count = await self.redis.incr(self._daily_key(user))
        if new_count == 1:
            await self.redis.expire(self._daily_key(user), 86400)
        return withdraw

    async def list_withdraws(self, user: User, limit: int = 10) -> list[WithdrawRequest]:
        stmt = (
            select(WithdrawRequest)
            .where(WithdrawRequest.user_id == user.id)
            .order_by(WithdrawRequest.created_at.desc())
            .limit(limit)
        )
        return (await self.session.execute(stmt)).scalars().all()

    async def _enforce_limits(self, user: User) -> None:
        key = self._daily_key(user)
        attempts = await self.redis.get(key)
        if attempts is not None and int(attempts) >= settings.daily_withdraw_limit:
            raise HTTPException(status_code=status.HTTP_429_TOO_MANY_REQUESTS, detail="daily_limit")

    def _daily_key(self, user: User) -> str:
        today = datetime.now(timezone.utc).date().isoformat()
        return f"withdraw:count:{user.telegram_id}:{today}"
