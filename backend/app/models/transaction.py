from sqlalchemy import Column, BigInteger, String, DateTime, Float, Boolean, Text, JSON
from sqlalchemy.sql import func
from app.core.database import Base


class Transaction(Base):
    __tablename__ = "transactions"
    
    id = Column(BigInteger, primary_key=True, index=True, autoincrement=True)
    telegram_id = Column(BigInteger, nullable=False, index=True)
    
    type = Column(String(20), nullable=False)  # income/withdraw/refund
    amount_usd = Column(Float, nullable=False)
    amount_usdt = Column(Float)
    currency = Column(String(10), default='USD')
    
    status = Column(String(20), default='pending')  # pending/processing/completed/failed
    
    # Transaction details
    description = Column(Text)
    note = Column(Text)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())


class WithdrawRequest(Base):
    __tablename__ = "withdraw_requests"
    
    id = Column(BigInteger, primary_key=True, index=True, autoincrement=True)
    telegram_id = Column(BigInteger, nullable=False, index=True)
    
    # Amount
    amount_usd = Column(Float, nullable=False)
    amount_usdt = Column(Float)
    
    # Wallet
    wallet_address = Column(String(255), nullable=False)
    network = Column(String(20), default='BEP20')
    
    # Provider info
    payout_id = Column(String(255))
    tx_hash = Column(String(255))
    provider_response = Column(JSON)
    idempotency_key = Column(String(255), unique=True)
    
    # Status
    status = Column(String(20), default='pending')  # pending/processing/completed/failed/cancelled
    reserved_balance = Column(Boolean, default=False)
    
    # Fees
    fee_usd = Column(Float, default=0.0)
    
    # Notes
    note = Column(Text)
    admin_note = Column(Text)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    processed_at = Column(DateTime(timezone=True))
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
