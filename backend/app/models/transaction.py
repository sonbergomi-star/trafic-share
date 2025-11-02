from sqlalchemy import Column, BigInteger, String, Numeric, DateTime, Text, Enum as SQLEnum
from sqlalchemy.sql import func
import enum
from app.core.database import Base


class TransactionType(str, enum.Enum):
    INCOME = "income"
    WITHDRAW = "withdraw"
    REFUND = "refund"
    ADJUSTMENT = "adjustment"


class TransactionStatus(str, enum.Enum):
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"


class Transaction(Base):
    __tablename__ = "transactions"
    
    id = Column(BigInteger, primary_key=True, autoincrement=True)
    telegram_id = Column(BigInteger, nullable=False, index=True)
    
    type = Column(SQLEnum(TransactionType), nullable=False)
    amount_usd = Column(Numeric(14, 6), nullable=False)
    amount_usdt = Column(Numeric(14, 6), nullable=True)
    currency = Column(String(10), default="USD", nullable=False)
    
    status = Column(SQLEnum(TransactionStatus), default=TransactionStatus.PENDING, nullable=False)
    
    # Withdraw specific
    wallet_address = Column(Text, nullable=True)
    provider_payout_id = Column(String(255), nullable=True)
    tx_hash = Column(String(255), nullable=True)
    
    note = Column(Text, nullable=True)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())


class BalanceHistory(Base):
    __tablename__ = "balance_history"
    
    id = Column(BigInteger, primary_key=True, autoincrement=True)
    telegram_id = Column(BigInteger, nullable=False, index=True)
    
    previous_balance = Column(Numeric(18, 6), nullable=False)
    new_balance = Column(Numeric(18, 6), nullable=False)
    delta = Column(Numeric(18, 6), nullable=False)
    reason = Column(String(255), nullable=True)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
