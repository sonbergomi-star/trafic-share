from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_
from datetime import datetime, timedelta, date
from typing import Dict, Any, List
import logging

from app.models.user import User
from app.models.session import Session
from app.models.transaction import Transaction
from app.models.withdraw_request import WithdrawRequest

logger = logging.getLogger(__name__)


class AdminService:
    """
    REAL admin service with full statistics
    """
    
    def __init__(self, db: AsyncSession):
        self.db = db
    
    async def get_dashboard_stats(self) -> Dict[str, Any]:
        """
        REAL admin dashboard statistics
        """
        # Total users
        users_result = await self.db.execute(
            select(func.count(User.id))
        )
        total_users = users_result.scalar()
        
        # Active users (last 7 days)
        week_ago = datetime.utcnow() - timedelta(days=7)
        active_users_result = await self.db.execute(
            select(func.count(User.id))
            .where(User.last_seen >= week_ago)
            .where(User.is_active == True)
        )
        active_users = active_users_result.scalar()
        
        # Total sessions
        sessions_result = await self.db.execute(
            select(func.count(Session.id))
        )
        total_sessions = sessions_result.scalar()
        
        # Active sessions now
        active_sessions_result = await self.db.execute(
            select(func.count(Session.id))
            .where(Session.status == "active")
        )
        active_sessions = active_sessions_result.scalar()
        
        # Total MB processed
        total_mb_result = await self.db.execute(
            select(func.sum(Session.server_counted_mb))
            .where(Session.status == "completed")
        )
        total_mb = total_mb_result.scalar() or 0.0
        
        # Total earnings distributed
        earnings_result = await self.db.execute(
            select(func.sum(Transaction.amount_usd))
            .where(Transaction.type == "income")
            .where(Transaction.status == "completed")
        )
        total_earnings = earnings_result.scalar() or 0.0
        
        # Pending withdrawals
        pending_withdrawals_result = await self.db.execute(
            select(func.count(WithdrawRequest.id), func.sum(WithdrawRequest.amount_usd))
            .where(WithdrawRequest.status.in_(["pending", "processing"]))
        )
        pending_withdraw_row = pending_withdrawals_result.first()
        pending_withdraw_count = pending_withdraw_row[0] or 0
        pending_withdraw_amount = pending_withdraw_row[1] or 0.0
        
        # Today's stats
        today_start = datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)
        
        today_sessions_result = await self.db.execute(
            select(func.count(Session.id))
            .where(Session.started_at >= today_start)
        )
        today_sessions = today_sessions_result.scalar()
        
        today_mb_result = await self.db.execute(
            select(func.sum(Session.server_counted_mb))
            .where(Session.started_at >= today_start)
            .where(Session.status.in_(["active", "completed"]))
        )
        today_mb = today_mb_result.scalar() or 0.0
        
        # Top users by earnings
        top_users_result = await self.db.execute(
            select(
                User.telegram_id,
                User.first_name,
                User.username,
                User.balance_usd,
                func.sum(Session.estimated_earnings).label("total_earned")
            )
            .join(Session, Session.telegram_id == User.telegram_id)
            .where(Session.status == "completed")
            .group_by(User.telegram_id, User.first_name, User.username, User.balance_usd)
            .order_by(func.sum(Session.estimated_earnings).desc())
            .limit(10)
        )
        top_users = [
            {
                "telegram_id": row[0],
                "first_name": row[1],
                "username": row[2],
                "balance_usd": float(row[3] or 0),
                "total_earned": float(row[4] or 0)
            }
            for row in top_users_result.all()
        ]
        
        return {
            "users": {
                "total": total_users,
                "active_last_7_days": active_users
            },
            "sessions": {
                "total": total_sessions,
                "active_now": active_sessions,
                "today": today_sessions
            },
            "traffic": {
                "total_mb": float(total_mb),
                "total_gb": float(total_mb / 1024),
                "today_mb": float(today_mb),
                "today_gb": float(today_mb / 1024)
            },
            "financials": {
                "total_earnings_distributed": float(total_earnings),
                "pending_withdrawals": {
                    "count": pending_withdraw_count,
                    "amount": float(pending_withdraw_amount)
                }
            },
            "top_users": top_users
        }
    
    async def get_user_details(self, telegram_id: int) -> Dict[str, Any]:
        """
        REAL detailed user information for admin
        """
        # Get user
        result = await self.db.execute(
            select(User).where(User.telegram_id == telegram_id)
        )
        user = result.scalar_one_or_none()
        
        if not user:
            raise ValueError(f"User {telegram_id} not found")
        
        # Get sessions count
        sessions_result = await self.db.execute(
            select(func.count(Session.id))
            .where(Session.telegram_id == telegram_id)
        )
        total_sessions = sessions_result.scalar()
        
        # Get total MB
        mb_result = await self.db.execute(
            select(func.sum(Session.server_counted_mb))
            .where(Session.telegram_id == telegram_id)
            .where(Session.status == "completed")
        )
        total_mb = mb_result.scalar() or 0.0
        
        # Get total earnings
        earnings_result = await self.db.execute(
            select(func.sum(Session.estimated_earnings))
            .where(Session.telegram_id == telegram_id)
            .where(Session.status == "completed")
        )
        total_earnings = earnings_result.scalar() or 0.0
        
        # Get withdrawals
        withdrawals_result = await self.db.execute(
            select(
                func.count(WithdrawRequest.id),
                func.sum(WithdrawRequest.amount_usd)
            )
            .where(WithdrawRequest.telegram_id == telegram_id)
            .where(WithdrawRequest.status == "completed")
        )
        withdraw_row = withdrawals_result.first()
        total_withdrawals = withdraw_row[0] or 0
        total_withdrawn = withdraw_row[1] or 0.0
        
        return {
            "user": {
                "telegram_id": user.telegram_id,
                "username": user.username,
                "first_name": user.first_name,
                "photo_url": user.photo_url,
                "is_active": user.is_active,
                "is_banned": user.is_banned,
                "balance_usd": float(user.balance_usd or 0),
                "created_at": user.created_at.isoformat() if user.created_at else None,
                "last_seen": user.last_seen.isoformat() if user.last_seen else None
            },
            "stats": {
                "total_sessions": total_sessions,
                "total_mb": float(total_mb),
                "total_gb": float(total_mb / 1024),
                "total_earnings": float(total_earnings),
                "total_withdrawals": total_withdrawals,
                "total_withdrawn": float(total_withdrawn)
            }
        }
    
    async def ban_user(self, telegram_id: int, reason: str = None) -> Dict[str, Any]:
        """
        REAL ban user (admin action)
        """
        result = await self.db.execute(
            select(User).where(User.telegram_id == telegram_id)
        )
        user = result.scalar_one_or_none()
        
        if not user:
            raise ValueError(f"User {telegram_id} not found")
        
        user.is_banned = True
        user.ban_reason = reason
        
        # Stop all active sessions
        await self.db.execute(
            select(Session)
            .where(Session.telegram_id == telegram_id)
            .where(Session.status == "active")
        )
        active_sessions = await self.db.execute(
            select(Session)
            .where(Session.telegram_id == telegram_id)
            .where(Session.status == "active")
        )
        
        for session in active_sessions.scalars():
            session.status = "stopped"
            session.stopped_at = datetime.utcnow()
        
        await self.db.commit()
        
        logger.info(f"User {telegram_id} banned. Reason: {reason}")
        
        return {
            "status": "banned",
            "telegram_id": telegram_id,
            "reason": reason
        }
    
    async def unban_user(self, telegram_id: int) -> Dict[str, Any]:
        """
        REAL unban user (admin action)
        """
        result = await self.db.execute(
            select(User).where(User.telegram_id == telegram_id)
        )
        user = result.scalar_one_or_none()
        
        if not user:
            raise ValueError(f"User {telegram_id} not found")
        
        user.is_banned = False
        user.ban_reason = None
        
        await self.db.commit()
        
        logger.info(f"User {telegram_id} unbanned")
        
        return {
            "status": "unbanned",
            "telegram_id": telegram_id
        }
