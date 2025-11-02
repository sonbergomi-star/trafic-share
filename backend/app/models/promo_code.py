from sqlalchemy import Column, BigInteger, String, Float, Boolean, DateTime, Integer
from sqlalchemy.sql import func
from app.core.database import Base


class PromoCode(Base):
    """
    REAL promo code model
    """
    __tablename__ = "promo_codes"
    
    id = Column(BigInteger, primary_key=True, index=True, autoincrement=True)
    
    code = Column(String(50), unique=True, nullable=False, index=True)  # PROMO2025
    bonus_usd = Column(Float, nullable=False)  # Bonus amount in USD
    
    max_uses = Column(Integer, default=0)  # 0 = unlimited
    current_uses = Column(Integer, default=0)
    
    is_active = Column(Boolean, default=True)
    
    created_by_admin = Column(BigInteger, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    expires_at = Column(DateTime(timezone=True), nullable=True)


class PromoCodeUsage(Base):
    """
    REAL promo code usage tracking
    """
    __tablename__ = "promo_code_usage"
    
    id = Column(BigInteger, primary_key=True, index=True, autoincrement=True)
    
    promo_code_id = Column(BigInteger, nullable=False, index=True)
    telegram_id = Column(BigInteger, nullable=False, index=True)
    
    bonus_usd = Column(Float, nullable=False)
    
    used_at = Column(DateTime(timezone=True), server_default=func.now())
