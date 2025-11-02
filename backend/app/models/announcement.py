from sqlalchemy import Column, BigInteger, String, Text, Boolean, DateTime
from sqlalchemy.sql import func
from app.core.database import Base


class Announcement(Base):
    """
    REAL announcement/news model
    """
    __tablename__ = "announcements"
    
    id = Column(BigInteger, primary_key=True, index=True, autoincrement=True)
    
    title = Column(String(255), nullable=False)
    body = Column(Text, nullable=False)
    
    announcement_type = Column(String(50), default="news")  # news, update, promo
    priority = Column(String(20), default="normal")  # low, normal, high
    
    is_active = Column(Boolean, default=True)
    is_pinned = Column(Boolean, default=False)
    
    created_by_admin = Column(BigInteger, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
