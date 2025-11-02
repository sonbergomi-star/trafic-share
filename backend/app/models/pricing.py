from sqlalchemy import Column, BigInteger, String, DateTime, Float, Date, Text
from sqlalchemy.sql import func
from app.core.database import Base


class DailyPrice(Base):
    __tablename__ = "daily_price"
    
    id = Column(BigInteger, primary_key=True, index=True, autoincrement=True)
    date = Column(Date, unique=True, nullable=False, index=True)
    price_per_gb = Column(Float, nullable=False)
    price_per_mb = Column(Float, nullable=False)
    message = Column(Text)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())


class PricingLog(Base):
    __tablename__ = "pricing_logs"
    
    id = Column(BigInteger, primary_key=True, index=True, autoincrement=True)
    date = Column(Date, nullable=False, index=True)
    price_per_mb = Column(Float, nullable=False)
    price_per_gb = Column(Float, nullable=False)
    source = Column(String(50), default='admin')
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())


class TrafficLog(Base):
    __tablename__ = "traffic_logs"
    
    id = Column(BigInteger, primary_key=True, index=True, autoincrement=True)
    telegram_id = Column(BigInteger, nullable=False, index=True)
    
    sent_mb = Column(Float, default=0.0)
    sold_mb = Column(Float, default=0.0)
    profit_usd = Column(Float, default=0.0)
    price_per_mb = Column(Float, default=0.0)
    
    period = Column(String(20), nullable=False)  # daily/weekly/monthly
    date = Column(Date, nullable=False, index=True)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
