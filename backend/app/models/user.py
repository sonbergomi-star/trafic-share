from sqlalchemy import Column, BigInteger, String, Numeric, Boolean, DateTime, Text
from sqlalchemy.sql import func
from app.core.database import Base


class User(Base):
    __tablename__ = "users"
    
    id = Column(BigInteger, primary_key=True, autoincrement=True)
    telegram_id = Column(BigInteger, unique=True, nullable=False, index=True)
    username = Column(String(255), nullable=True)
    first_name = Column(String(255), nullable=True)
    photo_url = Column(Text, nullable=True)
    auth_date = Column(DateTime(timezone=True), server_default=func.now())
    jwt_token = Column(Text, nullable=True)
    
    # Balance and traffic
    balance_usd = Column(Numeric(18, 6), default=0.00, nullable=False)
    sent_mb = Column(BigInteger, default=0, nullable=False)
    used_mb = Column(BigInteger, default=0, nullable=False)
    
    # Notifications
    device_token = Column(String(255), nullable=True)
    notifications_enabled = Column(Boolean, default=True, nullable=False)
    last_seen = Column(DateTime(timezone=True), nullable=True)
    
    # Security
    two_factor_enabled = Column(Boolean, default=False, nullable=False)
    last_login_ip = Column(String(64), nullable=True)
    last_login_device = Column(String(255), nullable=True)
    
    # Settings
    language = Column(String(10), default="uz", nullable=False)
    theme = Column(String(10), default="light", nullable=False)
    battery_saver = Column(Boolean, default=False, nullable=False)
    single_device_mode = Column(Boolean, default=False, nullable=False)
    
    # Status
    status = Column(String(20), default="active", nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
