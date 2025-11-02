from sqlalchemy import Column, BigInteger, Float, String, Text, DateTime
from sqlalchemy.sql import func
from app.core.database import Base


class BalanceHistory(Base):
    """
    REAL balance history snapshot model
    Tracks all balance changes
    """
    __tablename__ = "balance_history"
    
    id = Column(BigInteger, primary_key=True, index=True, autoincrement=True)
    telegram_id = Column(BigInteger, nullable=False, index=True)
    
    previous_balance = Column(Float, nullable=False)
    new_balance = Column(Float, nullable=False)
    delta = Column(Float, nullable=False)  # Change amount
    
    reason = Column(String(100), nullable=False)  # session_completed, withdraw, admin_adjust
    reference_id = Column(String(100), nullable=True)  # session_id, withdraw_id, etc.
    
    note = Column(Text, nullable=True)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
