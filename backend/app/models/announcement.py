from sqlalchemy import Column, BigInteger, String, DateTime, Float, Boolean, Text
from sqlalchemy.sql import func
from app.core.database import Base


class Announcement(Base):
    __tablename__ = "announcements"
    
    id = Column(BigInteger, primary_key=True, index=True, autoincrement=True)
    title = Column(String(255), nullable=False)
    description = Column(Text)
    image_url = Column(String(500))
    link = Column(String(500))
    
    is_active = Column(Boolean, default=True)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())


class PromoCode(Base):
    __tablename__ = "promo_codes"
    
    id = Column(BigInteger, primary_key=True, index=True, autoincrement=True)
    code = Column(String(64), unique=True, nullable=False, index=True)
    bonus_percent = Column(Float, nullable=False)
    bonus_amount_usd = Column(Float)
    
    description = Column(Text)
    
    expires_at = Column(DateTime(timezone=True))
    is_active = Column(Boolean, default=True)
    
    # Usage tracking
    max_uses = Column(BigInteger)
    current_uses = Column(BigInteger, default=0)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
