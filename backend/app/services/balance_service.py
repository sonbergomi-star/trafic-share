from datetime import datetime

from sqlalchemy.orm import Session

from app.db.models.finance import Transaction
from app.db.models.user import User
from app.schemas.finance import BalanceOverview, RefreshBalanceResponse, TransactionSchema, TransactionsResponse
from app.schemas.user import UserBasic


class BalanceService:
    @staticmethod
    def get_transactions(user: User, limit: int, offset: int, db: Session) -> TransactionsResponse:
        query = db.query(Transaction).filter(Transaction.telegram_id == user.telegram_id).order_by(Transaction.created_at.desc())
        total = query.count()
        items = query.offset(offset).limit(limit).all()
        return TransactionsResponse(items=[TransactionSchema.model_validate(item) for item in items], total=total)

    @staticmethod
    def refresh_balance(user: User, delta_usd: float, db: Session) -> RefreshBalanceResponse:
        previous = float(user.balance_usd or 0)
        user.balance_usd = previous + delta_usd
        user.updated_at = datetime.utcnow()

        if delta_usd != 0:
            tx = Transaction(
                user_id=user.id,
                telegram_id=user.telegram_id,
                type="income" if delta_usd > 0 else "adjustment",
                amount_usd=delta_usd,
                status="completed",
                note="Manual refresh",
            )
            db.add(tx)

        db.commit()
        return RefreshBalanceResponse(status="success", new_balance_usd=float(user.balance_usd), delta=delta_usd)

    @staticmethod
    def overview(user: User, db: Session) -> BalanceOverview:
        today = datetime.utcnow().date()
        month_start = datetime.utcnow().date().replace(day=1)

        today_income = (
            db.query(Transaction)
            .filter(
                Transaction.telegram_id == user.telegram_id,
                Transaction.type == "income",
                Transaction.created_at >= datetime.combine(today, datetime.min.time()),
            )
            .all()
        )
        month_income = (
            db.query(Transaction)
            .filter(
                Transaction.telegram_id == user.telegram_id,
                Transaction.type == "income",
                Transaction.created_at >= datetime.combine(month_start, datetime.min.time()),
            )
            .all()
        )

        recent_transactions = (
            db.query(Transaction)
            .filter(Transaction.telegram_id == user.telegram_id)
            .order_by(Transaction.created_at.desc())
            .limit(10)
            .all()
        )

        return BalanceOverview(
            user=UserBasic.model_validate(user),
            balance_usd=float(user.balance_usd or 0),
            sent_mb=float(user.sent_mb or 0),
            used_mb=float(user.used_mb or 0),
            today_earn=sum(float(tx.amount_usd) for tx in today_income),
            month_earn=sum(float(tx.amount_usd) for tx in month_income),
            transactions=[TransactionSchema.model_validate(tx) for tx in recent_transactions],
        )

