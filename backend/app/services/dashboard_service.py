from datetime import datetime, date, timedelta
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from typing import Dict, Any
import logging

from app.models.user import User
from app.models.session import Session
from app.models.pricing import DailyPrice
from app.models.transaction import WithdrawRequest

logger = logging.getLogger(__name__)


class DashboardService:
    """REAL Dashboard service with actual database calculations"""
    
    def __init__(self, db: AsyncSession):
        self.db = db
    
    async def get_dashboard_data(self, telegram_id: int) -> Dict[str, Any]:
        """Get REAL dashboard data from database"""
        
        # Get user
        user_result = await self.db.execute(
            select(User).where(User.telegram_id == telegram_id)
        )
        user = user_result.scalar_one_or_none()
        
        if not user:
            raise ValueError("User not found")
        
        # Get today's price - REAL query
        today = date.today()
        price_result = await self.db.execute(
            select(DailyPrice)
            .where(DailyPrice.date == today)
            .order_by(DailyPrice.created_at.desc())
            .limit(1)
        )
        daily_price = price_result.scalar_one_or_none()
        
        # If no price today, get latest
        if not daily_price:
            latest_price_result = await self.db.execute(
                select(DailyPrice)
                .order_by(DailyPrice.date.desc())
                .limit(1)
            )
            daily_price = latest_price_result.scalar_one_or_none()
        
        # Get active sessions - REAL count
        active_sessions_result = await self.db.execute(
            select(func.count(Session.id))
            .where(Session.telegram_id == telegram_id)
            .where(Session.is_active == True)
        )
        active_count = active_sessions_result.scalar() or 0
        
        # Get total sessions
        total_sessions_result = await self.db.execute(
            select(func.count(Session.id))
            .where(Session.telegram_id == telegram_id)
        )
        total_sessions = total_sessions_result.scalar() or 0
        
        # Get today's earnings - REAL calculation
        today_earnings = await self._get_today_earnings(telegram_id)
        
        # Get week earnings - REAL calculation
        week_earnings = await self._get_week_earnings(telegram_id)
        
        # Get month earnings - REAL calculation
        month_earnings = await self._get_month_earnings(telegram_id)
        
        # Pending withdrawals - REAL calculation
        pending_result = await self.db.execute(
            select(func.sum(WithdrawRequest.amount_usd))
            .where(WithdrawRequest.telegram_id == telegram_id)
            .where(WithdrawRequest.status.in_(['pending', 'processing']))
        )
        pending_amount = pending_result.scalar() or 0.0
        
        return {
            "user": {
                "telegram_id": user.telegram_id,
                "first_name": user.first_name,
                "last_name": user.last_name,
                "username": user.username,
                "balance_usd": float(user.balance_usd),
                "available_balance": float(user.balance_usd - pending_amount),
            },
            "traffic": {
                "sent_mb": float(user.sent_mb),
                "used_mb": float(user.used_mb),
                "sent_gb": float(user.sent_mb / 1024),
                "active_sessions": active_count,
                "total_sessions": total_sessions,
            },
            "earnings": {
                "today": float(today_earnings),
                "week": float(week_earnings),
                "month": float(month_earnings),
                "total": float(user.balance_usd),
            },
            "pricing": {
                "price_per_gb": float(daily_price.price_per_gb if daily_price else 1.50),
                "price_per_mb": float(daily_price.price_per_mb if daily_price else 0.0015),
                "message": daily_price.message if daily_price else "Default pricing",
                "date": today.isoformat(),
            },
            "quick_actions": {
                "can_start_session": active_count < 5,
                "can_withdraw": (user.balance_usd - pending_amount) >= 1.39,
                "pending_withdrawals": float(pending_amount),
            }
        }
    
    async def _get_today_earnings(self, telegram_id: int) -> float:
        """Get REAL today's earnings from completed sessions"""
        today_start = datetime.combine(date.today(), datetime.min.time())
        
        result = await self.db.execute(
            select(func.sum(Session.earned_usd))
            .where(Session.telegram_id == telegram_id)
            .where(Session.start_time >= today_start)
            .where(Session.status == 'completed')
        )
        earnings = result.scalar()
        
        return float(earnings or 0.0)
    
    async def _get_week_earnings(self, telegram_id: int) -> float:
        """Get REAL week's earnings"""
        today = date.today()
        week_start = today - timedelta(days=today.weekday())
        week_start_dt = datetime.combine(week_start, datetime.min.time())
        
        result = await self.db.execute(
            select(func.sum(Session.earned_usd))
            .where(Session.telegram_id == telegram_id)
            .where(Session.start_time >= week_start_dt)
            .where(Session.status == 'completed')
        )
        earnings = result.scalar()
        
        return float(earnings or 0.0)
    
    async def _get_month_earnings(self, telegram_id: int) -> float:
        """Get REAL month's earnings"""
        today = date.today()
        month_start = date(today.year, today.month, 1)
        month_start_dt = datetime.combine(month_start, datetime.min.time())
        
        result = await self.db.execute(
            select(func.sum(Session.earned_usd))
            .where(Session.telegram_id == telegram_id)
            .where(Session.start_time >= month_start_dt)
            .where(Session.status == 'completed')
        )
        earnings = result.scalar()
        
        return float(earnings or 0.0)
    
    async def refresh_balance(self, telegram_id: int) -> Dict[str, Any]:
        """REAL balance refresh from sessions and withdrawals"""
        
        user_result = await self.db.execute(
            select(User).where(User.telegram_id == telegram_id)
        )
        user = user_result.scalar_one_or_none()
        
        if not user:
            raise ValueError("User not found")
        
        # Calculate total earnings from completed sessions
        earnings_result = await self.db.execute(
            select(func.sum(Session.earned_usd))
            .where(Session.telegram_id == telegram_id)
            .where(Session.status == 'completed')
        )
        total_earnings = earnings_result.scalar() or 0.0
        
        # Calculate total withdrawn
        withdrawn_result = await self.db.execute(
            select(func.sum(WithdrawRequest.amount_usd))
            .where(WithdrawRequest.telegram_id == telegram_id)
            .where(WithdrawRequest.status == 'completed')
        )
        total_withdrawn = abs(withdrawn_result.scalar() or 0.0)
        
        # Calculate correct balance
        correct_balance = total_earnings - total_withdrawn
        old_balance = user.balance_usd
        delta = correct_balance - old_balance
        
        # Update if significantly different (more than 1 cent)
        if abs(delta) > 0.01:
            user.balance_usd = correct_balance
            await self.db.commit()
            logger.info(f"Balance corrected for user {telegram_id}: {old_balance:.2f} -> {correct_balance:.2f}")
        
        return {
            "status": "success",
            "old_balance_usd": float(old_balance),
            "new_balance_usd": float(correct_balance),
            "delta": float(delta),
            "total_earnings": float(total_earnings),
            "total_withdrawn": float(total_withdrawn),
        }
