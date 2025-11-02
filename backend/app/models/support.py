from sqlalchemy import Column, BigInteger, String, DateTime, Text
from sqlalchemy.sql import func
from app.core.database import Base


class SupportRequest(Base):
    __tablename__ = "support_requests"
    
    id = Column(BigInteger, primary_key=True, index=True, autoincrement=True)
    user_id = Column(BigInteger, nullable=False, index=True)
    telegram_id = Column(BigInteger, nullable=False)
    
    subject = Column(String(255), nullable=False)
    message = Column(Text, nullable=False)
    attachment_url = Column(String(500))
    
    status = Column(String(20), default='new')  # new/read/replied/closed
    
    admin_reply = Column(Text)
    admin_id = Column(BigInteger)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    replied_at = Column(DateTime(timezone=True))
