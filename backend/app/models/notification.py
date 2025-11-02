from sqlalchemy import Column, BigInteger, String, Boolean, Text, DateTime, JSON
from sqlalchemy.sql import func
from app.core.database import Base


class Notification(Base):
    """
    REAL notification model
    Stores all sent notifications
    """
    __tablename__ = "notifications"
    
    id = Column(BigInteger, primary_key=True, index=True, autoincrement=True)
    telegram_id = Column(BigInteger, nullable=False, index=True)
    
    title = Column(String(255), nullable=False)
    body = Column(Text, nullable=False)
    type = Column(String(50), nullable=False, index=True)  # balance_updated, session_completed, etc.
    
    is_read = Column(Boolean, default=False)
    data = Column(JSON, nullable=True)  # Extra data payload
    
    sent_at = Column(DateTime(timezone=True), nullable=True)
    read_at = Column(DateTime(timezone=True), nullable=True)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())


class FCMToken(Base):
    """
    REAL FCM device token model
    Stores Firebase Cloud Messaging tokens
    """
    __tablename__ = "fcm_tokens"
    
    id = Column(BigInteger, primary_key=True, index=True, autoincrement=True)
    telegram_id = Column(BigInteger, nullable=False, index=True)
    
    token = Column(String(255), unique=True, nullable=False)  # FCM token
    device_info = Column(Text, nullable=True)  # Device details
    
    is_active = Column(Boolean, default=True)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    last_used = Column(DateTime(timezone=True), server_default=func.now())
