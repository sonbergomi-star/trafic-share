from sqlalchemy import Column, BigInteger, String, DateTime, Boolean, ForeignKey
from sqlalchemy.sql import func
from app.core.database import Base


class UserSettings(Base):
    __tablename__ = "user_settings"
    
    id = Column(BigInteger, primary_key=True, index=True, autoincrement=True)
    user_id = Column(BigInteger, ForeignKey("users.id"), nullable=False, unique=True)
    telegram_id = Column(BigInteger, nullable=False, index=True)
    
    # Language
    language = Column(String(10), default='uz')  # uz/ru/en
    
    # Notifications
    push_notifications = Column(Boolean, default=True)
    session_updates = Column(Boolean, default=True)
    system_updates = Column(Boolean, default=True)
    
    # Security
    two_factor_enabled = Column(Boolean, default=False)
    single_device_mode = Column(Boolean, default=False)
    
    # App settings
    battery_saver = Column(Boolean, default=False)
    theme = Column(String(10), default='light')  # light/dark
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    last_update = Column(DateTime(timezone=True), onupdate=func.now())
