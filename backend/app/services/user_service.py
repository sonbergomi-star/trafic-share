from sqlalchemy.orm import Session
from app.models.user import User
from app.models.transaction import Transaction, TransactionType, TransactionStatus
from typing import Optional


def get_user_by_telegram_id(db: Session, telegram_id: int) -> Optional[User]:
    """Get user by telegram_id"""
    return db.query(User).filter(User.telegram_id == telegram_id).first()


def get_user_by_id(db: Session, user_id: int) -> Optional[User]:
    """Get user by id"""
    return db.query(User).filter(User.id == user_id).first()


def is_admin(telegram_id: int) -> bool:
    """Check if user is admin"""
    from app.core.config import get_admin_ids
    return telegram_id in get_admin_ids()


def update_user_balance(db: Session, telegram_id: int, amount: float, reason: str = None):
    """Update user balance atomically"""
    user = get_user_by_telegram_id(db, telegram_id)
    if not user:
        return False
    
    old_balance = float(user.balance_usd)
    user.balance_usd += amount
    new_balance = float(user.balance_usd)
    
    # Create balance history record
    from app.models.transaction import BalanceHistory
    balance_history = BalanceHistory(
        telegram_id=telegram_id,
        previous_balance=old_balance,
        new_balance=new_balance,
        delta=amount,
        reason=reason
    )
    db.add(balance_history)
    
    # Create transaction record
    if amount > 0:
        transaction = Transaction(
            telegram_id=telegram_id,
            type=TransactionType.INCOME,
            amount_usd=amount,
            status=TransactionStatus.COMPLETED,
            note=reason
        )
        db.add(transaction)
    
    db.commit()
    return True
