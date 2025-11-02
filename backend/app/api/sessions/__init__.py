from fastapi import APIRouter, Depends, HTTPException, WebSocket, WebSocketDisconnect
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, desc
from pydantic import BaseModel
from datetime import datetime
import uuid
import asyncio
import json

from app.core.database import get_db
from app.models.session import Session
from app.models.user import User
from app.services.traffic_service import TrafficService
from app.services.filter_service import FilterService
from app.core.config import settings


router = APIRouter()


class StartSessionRequest(BaseModel):
    telegram_id: int
    device_id: str
    network_type: str = "wifi"
    client_local_ip: str | None = None
    battery_level: float | None = None


class ReportTrafficRequest(BaseModel):
    session_id: str
    cumulative_mb: float
    delta_mb: float
    speed_mb_s: float
    battery_level: float | None = None
    network_type: str | None = None


@router.post("/start")
async def start_session(request: StartSessionRequest, db: AsyncSession = Depends(get_db)):
    """
    Start a new traffic session with filters
    """
    # Get user to check if admin
    user_result = await db.execute(
        select(User).where(User.telegram_id == request.telegram_id)
    )
    user = user_result.scalar_one_or_none()
    
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    is_admin = request.telegram_id in settings.admin_ids_list
    
    # Apply filters (VPN/Proxy detection, region check, etc.)
    filter_service = FilterService()
    
    # For now, use a mock IP (in production, get from request headers)
    client_ip = "8.8.8.8"  # Mock US IP
    
    filter_result = await filter_service.check_can_start_session(
        telegram_id=request.telegram_id,
        ip_address=client_ip,
        network_type=request.network_type,
        is_admin=is_admin
    )
    
    if not filter_result["allowed"]:
        raise HTTPException(
            status_code=403,
            detail={
                "status": "blocked",
                "reasons": filter_result["reasons"],
                "message": filter_result["message"]
            }
        )
    
    # Start session
    traffic_service = TrafficService(db)
    result = await traffic_service.start_session(
        telegram_id=request.telegram_id,
        device_id=request.device_id,
        network_type=request.network_type,
        ip_address=client_ip,
        device_info={
            "device": request.device_id,
            "battery_level": request.battery_level
        }
    )
    
    return result


@router.post("/stop")
async def stop_session(session_id: str, db: AsyncSession = Depends(get_db)):
    """
    Stop an active session
    """
    traffic_service = TrafficService(db)
    result = await traffic_service.stop_session(session_id)
    return result


@router.post("/report")
async def report_traffic(request: ReportTrafficRequest, db: AsyncSession = Depends(get_db)):
    """
    Report traffic data from client (heartbeat)
    """
    traffic_service = TrafficService(db)
    result = await traffic_service.report_traffic(
        session_id=request.session_id,
        cumulative_mb=request.cumulative_mb,
        delta_mb=request.delta_mb,
        speed_mb_s=request.speed_mb_s,
        battery_level=request.battery_level,
        network_type=request.network_type
    )
    return result


@router.post("/heartbeat")
async def heartbeat(session_id: str, db: AsyncSession = Depends(get_db)):
    """
    Session heartbeat - keep session alive
    """
    traffic_service = TrafficService(db)
    result = await traffic_service.heartbeat(session_id)
    return result


@router.get("/{telegram_id}")
async def get_sessions(telegram_id: int, limit: int = 20, db: AsyncSession = Depends(get_db)):
    """
    Get session history for user
    """
    result = await db.execute(
        select(Session)
        .where(Session.telegram_id == telegram_id)
        .order_by(desc(Session.created_at))
        .limit(limit)
    )
    sessions = result.scalars().all()
    
    return {
        "sessions": [
            {
                "id": s.id,
                "session_id": s.session_id,
                "start_time": s.start_time.isoformat(),
                "end_time": s.end_time.isoformat() if s.end_time else None,
                "duration": s.duration,
                "sent_mb": s.sent_mb,
                "used_mb": s.server_counted_mb,
                "earned_usd": s.earned_usd,
                "status": s.status,
                "ip_address": s.ip_address,
                "location": s.location,
                "device": s.device,
                "network_type": s.network_type_client,
            }
            for s in sessions
        ]
    }


@router.get("/active/{telegram_id}")
async def get_active_sessions(telegram_id: int, db: AsyncSession = Depends(get_db)):
    """
    Get user's active sessions
    """
    traffic_service = TrafficService(db)
    sessions = await traffic_service.get_active_sessions(telegram_id)
    return {"active_sessions": sessions}


# WebSocket endpoint for real-time updates
@router.websocket("/ws/{session_id}")
async def websocket_endpoint(websocket: WebSocket, session_id: str):
    """
    WebSocket for real-time session updates
    """
    await websocket.accept()
    
    try:
        while True:
            # Send periodic updates every 3 seconds
            await asyncio.sleep(3)
            
            # In production, fetch real session data from database
            # For now, send mock data
            data = {
                "session_id": session_id,
                "timestamp": datetime.utcnow().isoformat(),
                "sent_mb": 150.5,
                "speed_mb_s": 0.45,
                "estimated_earnings": 0.225,
            }
            
            await websocket.send_json(data)
    
    except WebSocketDisconnect:
        pass
