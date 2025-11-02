from sqlalchemy import Column, BigInteger, String, Numeric, Boolean, DateTime, Text, Integer, ForeignKey, Enum as SQLEnum
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
import enum
from app.core.database import Base


class SessionStatus(str, enum.Enum):
    ACTIVE = "active"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class FilterStatus(str, enum.Enum):
    PENDING = "pending"
    PASSED = "passed"
    FAILED = "failed"
    SKIPPED = "skipped"


class TrafficSession(Base):
    __tablename__ = "traffic_sessions"
    
    id = Column(BigInteger, primary_key=True, autoincrement=True)
    telegram_id = Column(BigInteger, nullable=False, index=True)
    device_id = Column(String(255), nullable=True)
    
    start_time = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    end_time = Column(DateTime(timezone=True), nullable=True)
    is_active = Column(Boolean, default=True, nullable=False)
    
    # Traffic metrics
    local_counted_mb = Column(Numeric(10, 2), default=0.00, nullable=False)
    server_counted_mb = Column(Numeric(10, 2), default=0.00, nullable=False)
    sent_mb = Column(Numeric(10, 2), default=0.00, nullable=False)
    used_mb = Column(Numeric(10, 2), default=0.00, nullable=False)
    estimated_earnings = Column(Numeric(10, 6), default=0.00, nullable=False)
    
    status = Column(SQLEnum(SessionStatus), default=SessionStatus.ACTIVE, nullable=False)
    last_report_at = Column(DateTime(timezone=True), nullable=True)
    
    # Filter status
    user_role = Column(String(16), default="user", nullable=False)
    filter_status = Column(SQLEnum(FilterStatus), default=FilterStatus.PENDING, nullable=False)
    filter_reasons = Column(Text, nullable=True)  # JSON string
    ip_country = Column(String(2), nullable=True)
    ip_asn = Column(String(64), nullable=True)
    is_proxy = Column(Boolean, default=False, nullable=False)
    vpn_score = Column(Numeric(5, 2), nullable=True)
    network_type_client = Column(String(16), nullable=True)
    network_type_asn = Column(String(32), nullable=True)
    validated_at = Column(DateTime(timezone=True), nullable=True)
    
    # Location
    ip_address = Column(String(64), nullable=True)
    location = Column(String(255), nullable=True)
    device = Column(String(255), nullable=True)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    reports = relationship("SessionReport", back_populates="session", cascade="all, delete-orphan")


class SessionReport(Base):
    __tablename__ = "session_reports"
    
    id = Column(BigInteger, primary_key=True, autoincrement=True)
    session_id = Column(BigInteger, ForeignKey("traffic_sessions.id"), nullable=False, index=True)
    telegram_id = Column(BigInteger, nullable=False, index=True)
    
    timestamp = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    delta_mb = Column(Numeric(10, 2), default=0.00, nullable=False)
    cumulative_mb = Column(Numeric(10, 2), default=0.00, nullable=False)
    speed_mb_s = Column(Numeric(10, 4), nullable=True)
    
    battery_level = Column(Integer, nullable=True)
    network_type = Column(String(16), nullable=True)
    ip = Column(String(64), nullable=True)
    raw_meta = Column(Text, nullable=True)  # JSON string
    
    # Relationships
    session = relationship("TrafficSession", back_populates="reports")
