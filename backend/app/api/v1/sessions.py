from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import desc
from app.core.database import get_db
from app.api.v1.dependencies import get_current_user
from app.models.session import TrafficSession, SessionStatus
from datetime import datetime, timedelta

router = APIRouter()


@router.get("")
async def get_sessions(
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db),
    limit: int = 20,
    offset: int = 0
):
    """Get user sessions"""
    sessions = db.query(TrafficSession).filter(
        TrafficSession.telegram_id == current_user.telegram_id
    ).order_by(desc(TrafficSession.created_at)).offset(offset).limit(limit).all()
    
    result = []
    for session in sessions:
        duration = None
        if session.end_time and session.start_time:
            delta = session.end_time - session.start_time
            hours, remainder = divmod(delta.total_seconds(), 3600)
            minutes, seconds = divmod(remainder, 60)
            duration = f"{int(hours):02d}:{int(minutes):02d}:{int(seconds):02d}"
        
        result.append({
            "id": session.id,
            "start_time": session.start_time.isoformat() if session.start_time else None,
            "end_time": session.end_time.isoformat() if session.end_time else None,
            "duration": duration,
            "sent_mb": float(session.sent_mb),
            "used_mb": float(session.used_mb),
            "earned_usd": float(session.estimated_earnings),
            "status": session.status.value,
            "ip_address": session.ip_address,
            "location": session.location,
            "device": session.device
        })
    
    return result


@router.get("/{session_id}")
async def get_session(
    session_id: int,
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get session details"""
    session = db.query(TrafficSession).filter(
        TrafficSession.id == session_id,
        TrafficSession.telegram_id == current_user.telegram_id
    ).first()
    
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    
    return {
        "id": session.id,
        "start_time": session.start_time.isoformat() if session.start_time else None,
        "end_time": session.end_time.isoformat() if session.end_time else None,
        "sent_mb": float(session.sent_mb),
        "used_mb": float(session.used_mb),
        "earned_usd": float(session.estimated_earnings),
        "status": session.status.value,
        "ip_address": session.ip_address,
        "location": session.location,
        "device": session.device
    }


@router.get("/summary")
async def get_summary(
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get session summary statistics"""
    today_start = datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)
    week_ago = datetime.utcnow() - timedelta(days=7)
    
    today_sessions = db.query(TrafficSession).filter(
        TrafficSession.telegram_id == current_user.telegram_id,
        TrafficSession.start_time >= today_start
    ).all()
    
    week_sessions = db.query(TrafficSession).filter(
        TrafficSession.telegram_id == current_user.telegram_id,
        TrafficSession.start_time >= week_ago
    ).all()
    
    today_mb = sum(float(s.used_mb) for s in today_sessions)
    week_mb = sum(float(s.used_mb) for s in week_sessions)
    today_earnings = sum(float(s.estimated_earnings) for s in today_sessions)
    week_earnings = sum(float(s.estimated_earnings) for s in week_sessions)
    
    avg_per_session = week_earnings / len(week_sessions) if week_sessions else 0
    
    return {
        "today": {
            "sessions": len(today_sessions),
            "mb": today_mb,
            "earnings": today_earnings
        },
        "week": {
            "sessions": len(week_sessions),
            "mb": week_mb,
            "earnings": week_earnings
        },
        "average_per_session": avg_per_session
    }
