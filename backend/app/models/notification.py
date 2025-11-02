from sqlalchemy import Column, BigInteger, String, DateTime, Boolean, Text
from sqlalchemy.sql import func
from app.core.database import Base


class NotificationLog(Base):
    __tablename__ = "notifications_log"
    
    id = Column(BigInteger, primary_key=True, index=True, autoincrement=True)
    telegram_id = Column(BigInteger, nullable=False, index=True)
    device_id = Column(String(255))
    
    notif_type = Column(String(50), nullable=False)  # daily_price/balance/session/system
    title = Column(String(255), nullable=False)
    body = Column(Text, nullable=False)
    
    sent_at = Column(DateTime(timezone=True), server_default=func.now())
    delivered = Column(Boolean, default=False)
    opened = Column(Boolean, default=False)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
