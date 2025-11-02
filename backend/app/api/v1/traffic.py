from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session
from datetime import datetime
from app.core.database import get_db
from app.api.v1.dependencies import get_current_user
from app.models.session import TrafficSession, SessionStatus, FilterStatus
from app.services.user_service import is_admin

router = APIRouter()


class TrafficStartRequest(BaseModel):
    device_id: str = None
    client_local_ip: str = None
    network_type: str = "unknown"  # mobile, wifi, unknown
    app_version: str = None
    os: str = None
    battery_level: int = None


class TrafficReportRequest(BaseModel):
    session_id: int
    device_id: str
    cumulative_mb: float
    delta_mb: float
    speed: float = None
    battery_level: int = None
    network_type: str = None
    timestamp: str = None


@router.post("/start")
async def start_traffic(
    request: TrafficStartRequest,
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Start traffic session"""
    # Check if user is admin (bypass filters)
    admin_bypass = is_admin(current_user.telegram_id)
    
    # TODO: Implement filter checks here
    # For now, if not admin, check filters
    if not admin_bypass:
        # Filter checks would go here
        pass
    
    # Create session
    session = TrafficSession(
        telegram_id=current_user.telegram_id,
        device_id=request.device_id,
        user_role="admin" if admin_bypass else "user",
        filter_status=FilterStatus.SKIPPED if admin_bypass else FilterStatus.PENDING,
        network_type_client=request.network_type,
        is_active=True,
        status=SessionStatus.ACTIVE
    )
    
    db.add(session)
    db.commit()
    db.refresh(session)
    
    return {
        "status": "ok",
        "session_id": session.id,
        "bypass": admin_bypass,
        "message": "Tunnel opened"
    }


@router.post("/stop")
async def stop_traffic(
    session_id: int,
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Stop traffic session"""
    session = db.query(TrafficSession).filter(
        TrafficSession.id == session_id,
        TrafficSession.telegram_id == current_user.telegram_id
    ).first()
    
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    
    session.end_time = datetime.utcnow()
    session.is_active = False
    session.status = SessionStatus.COMPLETED
    
    db.commit()
    
    return {"status": "success", "message": "Session stopped"}


@router.post("/report")
async def report_traffic(
    request: TrafficReportRequest,
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Report traffic usage"""
    from app.models.session import SessionReport
    
    session = db.query(TrafficSession).filter(
        TrafficSession.id == request.session_id,
        TrafficSession.telegram_id == current_user.telegram_id
    ).first()
    
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    
    # Update session metrics
    session.server_counted_mb += request.delta_mb
    session.last_report_at = datetime.utcnow()
    
    # Create report
    report = SessionReport(
        session_id=request.session_id,
        telegram_id=current_user.telegram_id,
        delta_mb=request.delta_mb,
        cumulative_mb=request.cumulative_mb,
        speed_mb_s=request.speed,
        battery_level=request.battery_level,
        network_type=request.network_type
    )
    
    db.add(report)
    db.commit()
    
    return {"status": "success"}
