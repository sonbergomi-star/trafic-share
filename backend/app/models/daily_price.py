from sqlalchemy import Column, BigInteger, String, Numeric, DateTime, Text, Date, UniqueConstraint
from sqlalchemy.sql import func
from app.core.database import Base


class DailyPrice(Base):
    __tablename__ = "daily_price"
    
    id = Column(BigInteger, primary_key=True, autoincrement=True)
    date = Column(Date, unique=True, nullable=False, index=True)
    price_per_gb = Column(Numeric(5, 2), nullable=False)
    message = Column(Text, nullable=True)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    __table_args__ = (UniqueConstraint('date', name='uq_daily_price_date'),)
