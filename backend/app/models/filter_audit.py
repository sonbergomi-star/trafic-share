from sqlalchemy import Column, BigInteger, String, DateTime, Text, Enum as SQLEnum, JSON
from sqlalchemy.sql import func
import enum
from app.core.database import Base


class FinalDecision(str, enum.Enum):
    ALLOW = "allow"
    DENY = "deny"
    PENDING_ADMIN = "pending_admin"


class FilterAudit(Base):
    __tablename__ = "filter_audit"
    
    id = Column(BigInteger, primary_key=True, autoincrement=True)
    session_id = Column(BigInteger, nullable=True, index=True)
    telegram_id = Column(BigInteger, nullable=False, index=True)
    device_id = Column(String(255), nullable=True)
    
    client_ip = Column(String(64), nullable=False)
    asn = Column(String(64), nullable=True)
    country = Column(String(2), nullable=True)
    isp = Column(String(255), nullable=True)
    
    is_proxy = Column(Boolean, default=False, nullable=False)
    vpn_score = Column(String(10), nullable=True)
    
    network_type_client = Column(String(16), nullable=True)
    network_type_asn = Column(String(32), nullable=True)
    
    check_sequence = Column(JSON, nullable=True)
    final_decision = Column(SQLEnum(FinalDecision), nullable=False)
    reasons = Column(JSON, nullable=True)
    
    admin_override_by = Column(BigInteger, nullable=True)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
