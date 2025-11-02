"""Balance and transaction handling."""

from datetime import datetime, timezone

from fastapi import HTTPException, status
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import BalanceHistory, Transaction, TransactionStatus, TransactionType, User


class BalanceService:
    """Provides balance snapshots and refresh flows."""

    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def get_balance_snapshot(self, user: User) -> dict:
        transactions_stmt = (
            select(Transaction)
            .where(Transaction.user_id == user.id)
            .order_by(Transaction.created_at.desc())
            .limit(10)
        )
        transactions = (await self.session.execute(transactions_stmt)).scalars().all()

        return {
            "user": {
                "telegram_id": user.telegram_id,
                "first_name": user.first_name,
                "username": user.username,
                "photo_url": user.photo_url,
                "auth_date": user.auth_date,
            },
            "balance": {
                "usd": float(user.balance_usd or 0),
                "sent_mb": user.sent_mb,
                "used_mb": user.used_mb,
                "pending_usd": 0,
                "last_refreshed": datetime.now(timezone.utc),
            },
            "today_earn": await self._today_income(user.id),
            "month_earn": await self._month_income(user.id),
            "transactions": [
                {
                    "id": tx.id,
                    "type": tx.type.value,
                    "amount_usd": float(tx.amount_usd),
                    "status": tx.status.value,
                    "created_at": tx.created_at,
                    "note": tx.note,
                }
                for tx in transactions
            ],
        }

    async def refresh_balance(self, user: User) -> dict:
        # For MVP we simply return existing balance and simulate delta
        delta = 0.0
        await self._record_history(user, delta)
        return {
            "status": "success",
            "new_balance_usd": float(user.balance_usd or 0),
            "delta": delta,
            "refreshed_at": datetime.now(timezone.utc),
        }

    async def apply_income(self, user: User, amount_usd: float, note: str | None = None) -> None:
        if amount_usd <= 0:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="invalid_amount")

        previous_balance = float(user.balance_usd or 0)
        user.balance_usd = previous_balance + amount_usd

        tx = Transaction(
            user_id=user.id,
            type=TransactionType.INCOME,
            amount_usd=amount_usd,
            status=TransactionStatus.COMPLETED,
            note=note,
        )
        self.session.add(tx)
        await self._record_history(user, amount_usd, previous_balance)
        await self.session.commit()

    async def _record_history(
        self,
        user: User,
        delta: float,
        previous_balance: float | None = None,
    ) -> None:
        if delta == 0:
            return
        prev = previous_balance if previous_balance is not None else float(user.balance_usd) - delta
        record = BalanceHistory(
            user_id=user.id,
            previous_balance=prev,
            new_balance=float(user.balance_usd),
            delta=delta,
            reason="auto_refresh",
        )
        self.session.add(record)

    async def _today_income(self, user_id: int) -> float:
        stmt = (
            select(func.coalesce(func.sum(Transaction.amount_usd), 0))
            .where(Transaction.user_id == user_id)
            .where(Transaction.type == TransactionType.INCOME)
            .where(func.date(Transaction.created_at) == func.current_date())
        )
        return float((await self.session.execute(stmt)).scalar_one() or 0)

    async def _month_income(self, user_id: int) -> float:
        stmt = (
            select(func.coalesce(func.sum(Transaction.amount_usd), 0))
            .where(Transaction.user_id == user_id)
            .where(Transaction.type == TransactionType.INCOME)
            .where(
                func.date_trunc("month", Transaction.created_at)
                == func.date_trunc("month", func.current_timestamp())
            )
        )
        return float((await self.session.execute(stmt)).scalar_one() or 0)
