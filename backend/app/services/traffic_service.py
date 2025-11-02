from datetime import datetime, timedelta
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, update
import uuid
from typing import Optional, Dict, Any
import logging

from app.models.session import Session, SessionReport
from app.models.user import User
from app.models.pricing import DailyPrice
from app.models.transaction import Transaction

logger = logging.getLogger(__name__)


class TrafficService:
    """REAL Traffic management with complete database operations"""
    
    MAX_ACTIVE_SESSIONS = 5
    SESSION_TIMEOUT_HOURS = 2
    
    def __init__(self, db: AsyncSession):
        self.db = db
    
    async def start_session(
        self,
        telegram_id: int,
        ip_address: Optional[str] = None,
        location: Optional[str] = None,
        device_info: Optional[str] = None,
        network_type: Optional[str] = "wifi"
    ) -> Dict[str, Any]:
        """
        REAL session start with validation and database recording
        """
        # Check active sessions limit
        active_count_result = await self.db.execute(
            select(func.count(Session.id))
            .where(Session.telegram_id == telegram_id)
            .where(Session.is_active == True)
        )
        active_count = active_count_result.scalar()
        
        if active_count >= self.MAX_ACTIVE_SESSIONS:
            raise ValueError(f"Maximum {self.MAX_ACTIVE_SESSIONS} active sessions allowed")
        
        # Get user
        user_result = await self.db.execute(
            select(User).where(User.telegram_id == telegram_id)
        )
        user = user_result.scalar_one_or_none()
        
        if not user:
            raise ValueError("User not found")
        
        if user.is_banned:
            raise ValueError("User is banned")
        
        # Get current price
        price = await self._get_current_price()
        
        # Create session
        session_id = str(uuid.uuid4())
        session = Session(
            session_id=session_id,
            telegram_id=telegram_id,
            ip_address=ip_address,
            location=location,
            start_time=datetime.utcnow(),
            is_active=True,
            status='active',
            sent_mb=0.0,
            local_counted_mb=0.0,
            server_counted_mb=0.0,
            earned_usd=0.0,
            last_report_at=datetime.utcnow(),
            created_at=datetime.utcnow()
        )
        
        self.db.add(session)
        await self.db.commit()
        await self.db.refresh(session)
        
        logger.info(f"Session started: {session_id} for user {telegram_id}")
        
        return {
            "session_id": session.session_id,
            "status": "active",
            "start_time": session.start_time.isoformat(),
            "price_per_mb": price['price_per_mb'],
            "price_per_gb": price['price_per_gb'],
        }
    
    async def stop_session(self, session_id: str, telegram_id: int) -> Dict[str, Any]:
        """
        REAL session stop with final calculations
        """
        # Get session
        result = await self.db.execute(
            select(Session)
            .where(Session.session_id == session_id)
            .where(Session.telegram_id == telegram_id)
        )
        session = result.scalar_one_or_none()
        
        if not session:
            raise ValueError("Session not found")
        
        if not session.is_active:
            raise ValueError("Session is already stopped")
        
        # Calculate final values
        session.is_active = False
        session.status = 'completed'
        session.end_time = datetime.utcnow()
        
        # Calculate duration
        if session.start_time:
            duration_seconds = (session.end_time - session.start_time).total_seconds()
            hours = int(duration_seconds // 3600)
            minutes = int((duration_seconds % 3600) // 60)
            seconds = int(duration_seconds % 60)
            session.duration = f"{hours:02d}:{minutes:02d}:{seconds:02d}"
        
        # Recalculate earnings based on server counted traffic
        price = await self._get_current_price()
        final_earned = session.server_counted_mb * price['price_per_mb']
        session.earned_usd = final_earned
        
        # Update user totals
        user_result = await self.db.execute(
            select(User).where(User.telegram_id == telegram_id)
        )
        user = user_result.scalar_one()
        
        user.sent_mb += session.sent_mb
        user.used_mb += session.server_counted_mb
        user.balance_usd += final_earned
        
        # Create transaction record
        transaction = Transaction(
            telegram_id=telegram_id,
            type='income',
            amount_usd=final_earned,
            status='completed',
            description=f"Session {session_id[:8]} earnings",
            created_at=datetime.utcnow()
        )
        self.db.add(transaction)
        
        await self.db.commit()
        await self.db.refresh(session)
        
        logger.info(
            f"Session stopped: {session_id} - "
            f"{session.server_counted_mb:.2f}MB earned ${final_earned:.4f}"
        )
        
        return {
            "session_id": session.session_id,
            "status": "completed",
            "duration": session.duration,
            "sent_mb": float(session.sent_mb),
            "server_counted_mb": float(session.server_counted_mb),
            "earned_usd": float(final_earned),
            "new_balance": float(user.balance_usd),
        }
    
    async def report_traffic(
        self,
        session_id: str,
        telegram_id: int,
        cumulative_mb: float,
        delta_mb: float
    ) -> Dict[str, Any]:
        """
        REAL traffic reporting with validation
        """
        # Validate input
        if cumulative_mb < 0 or delta_mb < 0:
            raise ValueError("Traffic values cannot be negative")
        
        if delta_mb > 1000:
            logger.warning(f"Large delta reported: {delta_mb}MB for session {session_id}")
        
        # Get session
        result = await self.db.execute(
            select(Session)
            .where(Session.session_id == session_id)
            .where(Session.telegram_id == telegram_id)
        )
        session = result.scalar_one_or_none()
        
        if not session:
            raise ValueError("Session not found")
        
        if not session.is_active:
            raise ValueError("Session is not active")
        
        # Create report record
        report = SessionReport(
            session_id=session.id,
            cumulative_mb=cumulative_mb,
            delta_mb=delta_mb,
            timestamp=datetime.utcnow()
        )
        self.db.add(report)
        
        # Update session
        session.sent_mb = cumulative_mb
        session.local_counted_mb = cumulative_mb
        session.server_counted_mb += delta_mb
        session.last_report_at = datetime.utcnow()
        
        # Calculate current earnings
        price = await self._get_current_price()
        session.earned_usd = session.server_counted_mb * price['price_per_mb']
        
        await self.db.commit()
        
        logger.debug(
            f"Traffic reported for {session_id}: "
            f"cumulative={cumulative_mb:.2f}MB delta={delta_mb:.2f}MB"
        )
        
        return {
            "status": "success",
            "session_id": session_id,
            "cumulative_mb": float(cumulative_mb),
            "server_counted_mb": float(session.server_counted_mb),
            "current_earnings": float(session.earned_usd),
        }
    
    async def get_active_sessions(self, telegram_id: int) -> list:
        """
        REAL get all active sessions with details
        """
        result = await self.db.execute(
            select(Session)
            .where(Session.telegram_id == telegram_id)
            .where(Session.is_active == True)
            .order_by(Session.start_time.desc())
        )
        sessions = result.scalars().all()
        
        active_sessions = []
        for s in sessions:
            # Calculate duration
            if s.start_time:
                duration_seconds = (datetime.utcnow() - s.start_time).total_seconds()
                hours = int(duration_seconds // 3600)
                minutes = int((duration_seconds % 3600) // 60)
                duration_str = f"{hours:02d}:{minutes:02d}"
            else:
                duration_str = "00:00"
            
            active_sessions.append({
                "session_id": s.session_id,
                "start_time": s.start_time.isoformat() if s.start_time else None,
                "duration": duration_str,
                "sent_mb": float(s.sent_mb),
                "server_counted_mb": float(s.server_counted_mb),
                "earned_usd": float(s.earned_usd),
                "ip_address": s.ip_address,
                "location": s.location,
                "last_report_at": s.last_report_at.isoformat() if s.last_report_at else None,
            })
        
        return active_sessions
    
    async def heartbeat(self, session_id: str, telegram_id: int) -> dict:
        """
        REAL session heartbeat
        """
        result = await self.db.execute(
            select(Session)
            .where(Session.session_id == session_id)
            .where(Session.telegram_id == telegram_id)
        )
        session = result.scalar_one_or_none()
        
        if not session:
            return {"status": "session_not_found"}
        
        if not session.is_active:
            return {"status": "session_inactive"}
        
        # Check if session timed out
        if session.last_report_at:
            time_since_last = (datetime.utcnow() - session.last_report_at).total_seconds()
            if time_since_last > self.SESSION_TIMEOUT_HOURS * 3600:
                await self.stop_session(session_id, telegram_id)
                return {"status": "session_timeout"}
        
        # Update heartbeat
        session.last_report_at = datetime.utcnow()
        await self.db.commit()
        
        return {
            "status": "ok",
            "session_active": True,
            "current_mb": float(session.server_counted_mb),
            "current_earnings": float(session.earned_usd),
        }
    
    async def get_session_history(
        self,
        telegram_id: int,
        limit: int = 20,
        offset: int = 0
    ) -> dict:
        """
        REAL session history from database
        """
        # Get total count
        count_result = await self.db.execute(
            select(func.count(Session.id))
            .where(Session.telegram_id == telegram_id)
        )
        total = count_result.scalar()
        
        # Get sessions
        result = await self.db.execute(
            select(Session)
            .where(Session.telegram_id == telegram_id)
            .order_by(Session.start_time.desc())
            .offset(offset)
            .limit(limit)
        )
        sessions = result.scalars().all()
        
        return {
            "sessions": [
                {
                    "id": s.id,
                    "session_id": s.session_id,
                    "start_time": s.start_time.isoformat() if s.start_time else None,
                    "end_time": s.end_time.isoformat() if s.end_time else None,
                    "duration": s.duration,
                    "status": s.status,
                    "sent_mb": float(s.sent_mb),
                    "server_counted_mb": float(s.server_counted_mb),
                    "earned_usd": float(s.earned_usd),
                    "ip_address": s.ip_address,
                    "location": s.location,
                }
                for s in sessions
            ],
            "total": total,
            "limit": limit,
            "offset": offset,
        }
    
    async def _get_current_price(self) -> dict:
        """Get current traffic price"""
        from datetime import date
        
        # Try today's price
        result = await self.db.execute(
            select(DailyPrice)
            .where(DailyPrice.date == date.today())
            .order_by(DailyPrice.created_at.desc())
            .limit(1)
        )
        price = result.scalar_one_or_none()
        
        # Fallback to latest price
        if not price:
            result = await self.db.execute(
                select(DailyPrice).order_by(DailyPrice.date.desc()).limit(1)
            )
            price = result.scalar_one_or_none()
        
        if price:
            return {
                "price_per_gb": float(price.price_per_gb),
                "price_per_mb": float(price.price_per_mb),
            }
        
        # Default fallback
        return {
            "price_per_gb": 1.50,
            "price_per_mb": 0.0015,
        }
