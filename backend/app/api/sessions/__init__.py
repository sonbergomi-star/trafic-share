from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, desc
from pydantic import BaseModel
from datetime import datetime
import uuid

from app.core.database import get_db
from app.models.session import Session
from app.models.user import User


router = APIRouter()


class StartSessionRequest(BaseModel):
    telegram_id: int
    device_id: str
    network_type: str = "wifi"


@router.post("/start")
async def start_session(request: StartSessionRequest, db: AsyncSession = Depends(get_db)):
    """
    Start a new traffic session
    """
    # Get user
    result = await db.execute(
        select(User).where(User.telegram_id == request.telegram_id)
    )
    user = result.scalar_one_or_none()
    
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Create new session
    session_id = str(uuid.uuid4())
    session = Session(
        session_id=session_id,
        user_id=user.id,
        telegram_id=request.telegram_id,
        device_id=request.device_id,
        network_type_client=request.network_type,
        status="active",
        is_active=True,
    )
    
    db.add(session)
    await db.commit()
    await db.refresh(session)
    
    return {
        "status": "ok",
        "session_id": session.session_id,
        "message": "Session started successfully"
    }


@router.post("/stop")
async def stop_session(session_id: str, db: AsyncSession = Depends(get_db)):
    """
    Stop an active session
    """
    result = await db.execute(
        select(Session).where(Session.session_id == session_id)
    )
    session = result.scalar_one_or_none()
    
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    
    session.is_active = False
    session.status = "completed"
    session.end_time = datetime.utcnow()
    
    await db.commit()
    
    return {
        "status": "ok",
        "message": "Session stopped successfully"
    }


@router.get("/{telegram_id}")
async def get_sessions(telegram_id: int, db: AsyncSession = Depends(get_db)):
    """
    Get session history for user
    """
    result = await db.execute(
        select(Session)
        .where(Session.telegram_id == telegram_id)
        .order_by(desc(Session.created_at))
        .limit(20)
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
                "earned_usd": s.earned_usd,
                "status": s.status,
                "ip_address": s.ip_address,
                "location": s.location,
                "device": s.device,
            }
            for s in sessions
        ]
    }
