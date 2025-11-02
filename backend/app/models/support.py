from sqlalchemy import Column, BigInteger, String, DateTime, Text, Enum as SQLEnum
from sqlalchemy.sql import func
import enum
from app.core.database import Base


class SupportStatus(str, enum.Enum):
    NEW = "new"
    READ = "read"
    REPLIED = "replied"
    CLOSED = "closed"


class SupportRequest(Base):
    __tablename__ = "support_requests"
    
    id = Column(BigInteger, primary_key=True, autoincrement=True)
    telegram_id = Column(BigInteger, nullable=False, index=True)
    
    subject = Column(String(255), nullable=False)
    message = Column(Text, nullable=False)
    attachment_url = Column(String(255), nullable=True)
    
    status = Column(SQLEnum(SupportStatus), default=SupportStatus.NEW, nullable=False, index=True)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
