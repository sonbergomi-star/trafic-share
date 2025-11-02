from datetime import datetime, timedelta
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update
import uuid
from typing import Optional, Dict, Any

from app.models.session import Session, SessionReport
from app.models.user import User
from app.core.config import settings


class TrafficService:
    """Traffic management service"""
    
    def __init__(self, db: AsyncSession):
        self.db = db
    
    async def start_session(
        self,
        telegram_id: int,
        device_id: str,
        network_type: str,
        ip_address: Optional[str] = None,
        device_info: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Start a new traffic session"""
        
        # Get user
        result = await self.db.execute(
            select(User).where(User.telegram_id == telegram_id)
        )
        user = result.scalar_one_or_none()
        
        if not user:
            raise ValueError("User not found")
        
        # Check if user already has active session
        active_session_result = await self.db.execute(
            select(Session)
            .where(Session.telegram_id == telegram_id)
            .where(Session.is_active == True)
        )
        active_session = active_session_result.scalar_one_or_none()
        
        if active_session:
            return {
                "status": "error",
                "message": "Already have active session",
                "session_id": active_session.session_id
            }
        
        # Create new session
        session_id = str(uuid.uuid4())
        new_session = Session(
            session_id=session_id,
            user_id=user.id,
            telegram_id=telegram_id,
            device_id=device_id,
            network_type_client=network_type,
            ip_address=ip_address,
            device=device_info.get('device') if device_info else None,
            battery_level=device_info.get('battery_level') if device_info else None,
            status='active',
            is_active=True,
            start_time=datetime.utcnow(),
            filter_status='passed',  # Assume passed for now
        )
        
        self.db.add(new_session)
        await self.db.commit()
        await self.db.refresh(new_session)
        
        return {
            "status": "ok",
            "session_id": session_id,
            "message": "Session started successfully"
        }
    
    async def stop_session(self, session_id: str) -> Dict[str, Any]:
        """Stop an active session"""
        
        result = await self.db.execute(
            select(Session).where(Session.session_id == session_id)
        )
        session = result.scalar_one_or_none()
        
        if not session:
            raise ValueError("Session not found")
        
        if not session.is_active:
            return {
                "status": "error",
                "message": "Session already stopped"
            }
        
        # Calculate duration
        end_time = datetime.utcnow()
        duration = end_time - session.start_time
        duration_str = str(duration).split('.')[0]  # HH:MM:SS format
        
        # Update session
        session.is_active = False
        session.status = 'completed'
        session.end_time = end_time
        session.duration = duration_str
        
        # Calculate earnings (simple calculation)
        # In production, this should use actual pricing and traffic data
        if session.server_counted_mb > 0:
            # Assuming $0.0015 per MB (will be replaced with real pricing)
            session.earned_usd = session.server_counted_mb * 0.0015
        
        # Update user stats
        user_result = await self.db.execute(
            select(User).where(User.id == session.user_id)
        )
        user = user_result.scalar_one_or_none()
        
        if user:
            user.sent_mb += session.sent_mb
            user.used_mb += session.server_counted_mb
            user.balance_usd += session.earned_usd
        
        await self.db.commit()
        
        return {
            "status": "ok",
            "message": "Session stopped successfully",
            "duration": duration_str,
            "earned_usd": session.earned_usd,
            "sent_mb": session.sent_mb,
        }
    
    async def report_traffic(
        self,
        session_id: str,
        cumulative_mb: float,
        delta_mb: float,
        speed_mb_s: float,
        battery_level: Optional[float] = None,
        network_type: Optional[str] = None
    ) -> Dict[str, Any]:
        """Report traffic data from client"""
        
        result = await self.db.execute(
            select(Session).where(Session.session_id == session_id)
        )
        session = result.scalar_one_or_none()
        
        if not session:
            raise ValueError("Session not found")
        
        if not session.is_active:
            return {
                "status": "error",
                "message": "Session is not active"
            }
        
        # Update session
        session.local_counted_mb = cumulative_mb
        session.server_counted_mb += delta_mb
        session.sent_mb = cumulative_mb
        session.last_report_at = datetime.utcnow()
        
        if battery_level:
            session.battery_level = battery_level
        
        # Create session report
        report = SessionReport(
            session_id=session.id,
            telegram_id=session.telegram_id,
            cumulative_mb=cumulative_mb,
            delta_mb=delta_mb,
            speed_mb_s=speed_mb_s,
            battery_level=battery_level,
            network_type=network_type,
            timestamp=datetime.utcnow()
        )
        
        self.db.add(report)
        await self.db.commit()
        
        return {
            "status": "ok",
            "server_counted_mb": session.server_counted_mb,
            "estimated_earnings": session.server_counted_mb * 0.0015
        }
    
    async def get_active_sessions(self, telegram_id: int) -> list:
        """Get user's active sessions"""
        
        result = await self.db.execute(
            select(Session)
            .where(Session.telegram_id == telegram_id)
            .where(Session.is_active == True)
        )
        sessions = result.scalars().all()
        
        return [
            {
                "session_id": s.session_id,
                "start_time": s.start_time.isoformat(),
                "sent_mb": s.sent_mb,
                "estimated_earnings": s.server_counted_mb * 0.0015,
                "network_type": s.network_type_client,
                "device": s.device,
            }
            for s in sessions
        ]
    
    async def heartbeat(self, session_id: str) -> Dict[str, Any]:
        """Session heartbeat - keep session alive"""
        
        result = await self.db.execute(
            select(Session).where(Session.session_id == session_id)
        )
        session = result.scalar_one_or_none()
        
        if not session:
            raise ValueError("Session not found")
        
        session.last_report_at = datetime.utcnow()
        await self.db.commit()
        
        return {
            "status": "ok",
            "session_active": session.is_active
        }
