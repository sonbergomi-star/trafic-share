from sqlalchemy import Column, BigInteger, String, DateTime, Float, Boolean, Text
from sqlalchemy.sql import func
from app.core.database import Base


class User(Base):
    __tablename__ = "users"
    
    id = Column(BigInteger, primary_key=True, index=True, autoincrement=True)
    telegram_id = Column(BigInteger, unique=True, nullable=False, index=True)
    username = Column(String(255))
    first_name = Column(String(255))
    photo_url = Column(Text)
    auth_date = Column(DateTime(timezone=True), server_default=func.now())
    jwt_token = Column(Text)
    
    # Balance and traffic
    balance_usd = Column(Float, default=0.0)
    sent_mb = Column(Float, default=0.0)
    used_mb = Column(Float, default=0.0)
    
    # Device and notifications
    device_token = Column(Text)
    notifications_enabled = Column(Boolean, default=True)
    last_seen = Column(DateTime(timezone=True))
    
    # Security
    two_factor_enabled = Column(Boolean, default=False)
    single_device_mode = Column(Boolean, default=False)
    last_login_ip = Column(String(64))
    last_login_device = Column(String(255))
    
    # Status
    is_active = Column(Boolean, default=True)
    is_banned = Column(Boolean, default=False)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
