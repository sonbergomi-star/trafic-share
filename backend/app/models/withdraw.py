from sqlalchemy import Column, BigInteger, String, Numeric, Boolean, DateTime, Text, Enum as SQLEnum, JSON
from sqlalchemy.sql import func
import enum
from app.core.database import Base


class WithdrawStatus(str, enum.Enum):
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class WithdrawRequest(Base):
    __tablename__ = "withdraw_requests"
    
    id = Column(BigInteger, primary_key=True, autoincrement=True)
    telegram_id = Column(BigInteger, nullable=False, index=True)
    
    amount_usd = Column(Numeric(14, 6), nullable=False)
    amount_usdt = Column(Numeric(14, 6), nullable=True)
    wallet_address = Column(Text, nullable=False)
    network = Column(String(20), default="BEP20", nullable=False)
    
    status = Column(SQLEnum(WithdrawStatus), default=WithdrawStatus.PENDING, nullable=False, index=True)
    
    payout_id = Column(String(255), nullable=True)
    tx_hash = Column(String(255), nullable=True)
    provider_response = Column(JSON, nullable=True)
    
    idempotency_key = Column(String(255), unique=True, nullable=True, index=True)
    reserved_balance = Column(Boolean, default=False, nullable=False)
    fee_usd = Column(Numeric(14, 6), nullable=True)
    note = Column(Text, nullable=True)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    processed_at = Column(DateTime(timezone=True), nullable=True)


class PayoutAudit(Base):
    __tablename__ = "payout_audit"
    
    id = Column(BigInteger, primary_key=True, autoincrement=True)
    withdraw_request_id = Column(BigInteger, nullable=True, index=True)
    
    provider_name = Column(String(50), nullable=False)
    request_payload = Column(JSON, nullable=True)
    response_payload = Column(JSON, nullable=True)
    status_code = Column(Integer, nullable=True)
    error_message = Column(Text, nullable=True)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
