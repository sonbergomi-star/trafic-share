from sqlalchemy import Column, BigInteger, String, DateTime, Float, ForeignKey, JSON, Text
from sqlalchemy.sql import func
from app.core.database import Base


class Session(Base):
    __tablename__ = "sessions"
    
    id = Column(BigInteger, primary_key=True, index=True, autoincrement=True)
    session_id = Column(String(255), unique=True, nullable=False, index=True)
    user_id = Column(BigInteger, ForeignKey("users.id"), nullable=False)
    telegram_id = Column(BigInteger, nullable=False, index=True)
    device_id = Column(String(255))
    
    # Session timing
    start_time = Column(DateTime(timezone=True), server_default=func.now())
    end_time = Column(DateTime(timezone=True))
    duration = Column(String(20))  # HH:MM:SS format
    
    # Traffic data
    sent_mb = Column(Float, default=0.0)
    sold_mb = Column(Float, default=0.0)
    local_counted_mb = Column(Float, default=0.0)
    server_counted_mb = Column(Float, default=0.0)
    
    # Earnings
    earned_usd = Column(Float, default=0.0)
    estimated_earnings = Column(Float, default=0.0)
    
    # Network info
    ip_address = Column(String(64))
    ip_country = Column(String(2))
    ip_asn = Column(String(64))
    location = Column(String(255))
    network_type_client = Column(String(16))  # mobile/wifi/unknown
    network_type_asn = Column(String(32))
    
    # VPN/Proxy detection
    is_proxy = Column(Boolean, default=False)
    vpn_score = Column(Float, default=0.0)
    
    # Filter status
    filter_status = Column(String(32), default='pending')  # pending/passed/failed/skipped
    filter_reasons = Column(JSON)
    validated_at = Column(DateTime(timezone=True))
    
    # Status
    status = Column(String(20), default='active')  # active/completed/failed/cancelled
    is_active = Column(Boolean, default=True)
    
    # Device info
    device = Column(String(255))
    battery_level = Column(Float)
    
    last_report_at = Column(DateTime(timezone=True))
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())


class SessionReport(Base):
    __tablename__ = "session_reports"
    
    id = Column(BigInteger, primary_key=True, index=True, autoincrement=True)
    session_id = Column(BigInteger, ForeignKey("sessions.id"), nullable=False)
    telegram_id = Column(BigInteger, nullable=False)
    
    timestamp = Column(DateTime(timezone=True), server_default=func.now())
    cumulative_mb = Column(Float, default=0.0)
    delta_mb = Column(Float, default=0.0)
    speed_mb_s = Column(Float, default=0.0)
    battery_level = Column(Float)
    network_type = Column(String(16))
    ip = Column(String(64))
    raw_meta = Column(JSON)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
