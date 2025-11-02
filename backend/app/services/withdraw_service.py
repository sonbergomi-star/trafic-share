from datetime import datetime
from decimal import Decimal

from sqlalchemy.orm import Session

from app.core.config import get_settings
from app.core.security import generate_idempotency_key
from app.db.models.finance import Transaction, WithdrawRequest
from app.db.models.user import User
from app.schemas.finance import WithdrawDetail, WithdrawListResponse, WithdrawPayload, WithdrawResponse


settings = get_settings()


class WithdrawService:
    usd_to_usdt_ratio = Decimal("0.99")

    @classmethod
    def create_withdraw(cls, user: User, payload: WithdrawPayload, db: Session) -> WithdrawResponse:
        if payload.amount_usd < settings.min_withdraw_usd:
            raise ValueError("Amount below minimum withdraw threshold")
        if payload.amount_usd > settings.max_withdraw_usd:
            raise ValueError("Amount exceeds maximum withdraw threshold")
        if (user.balance_usd or 0) < payload.amount_usd:
            raise ValueError("Insufficient balance")

        idempotency_key = payload.idempotency_key or generate_idempotency_key(
            "withdraw", f"{user.telegram_id}:{payload.amount_usd}:{payload.wallet_address}"
        )

        existing = db.query(WithdrawRequest).filter(WithdrawRequest.idempotency_key == idempotency_key).one_or_none()
        if existing:
            return WithdrawResponse(status=existing.status, transaction_id=None, withdraw_id=existing.id, message="Duplicate request")

        amount_usdt = float((Decimal(payload.amount_usd) * cls.usd_to_usdt_ratio).quantize(Decimal("0.000001")))

        request = WithdrawRequest(
            user_id=user.id,
            telegram_id=user.telegram_id,
            amount_usd=payload.amount_usd,
            amount_usdt=amount_usdt,
            wallet_address=payload.wallet_address,
            network=payload.network,
            status="pending",
            idempotency_key=idempotency_key,
            reserved_balance=True,
        )

        user.balance_usd = (user.balance_usd or 0) - payload.amount_usd

        transaction = Transaction(
            user_id=user.id,
            telegram_id=user.telegram_id,
            type="withdraw",
            amount_usd=-payload.amount_usd,
            amount_usdt=-amount_usdt,
            status="pending",
            wallet_address=payload.wallet_address,
            note="Withdraw request",
        )

        db.add(request)
        db.add(transaction)
        db.commit()
        db.refresh(request)

        return WithdrawResponse(
            status=request.status,
            transaction_id=transaction.id,
            withdraw_id=request.id,
            message="Withdraw request queued",
        )

    @staticmethod
    def list_withdraws(user: User, limit: int, offset: int, db: Session) -> WithdrawListResponse:
        query = db.query(WithdrawRequest).filter(WithdrawRequest.telegram_id == user.telegram_id).order_by(WithdrawRequest.created_at.desc())
        total = query.count()
        rows = query.offset(offset).limit(limit).all()
        items = [WithdrawDetail.model_validate(row) for row in rows]
        return WithdrawListResponse(items=items, total=total)

