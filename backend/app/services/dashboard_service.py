from datetime import datetime, date, timedelta
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from typing import Dict, Any

from app.models.user import User
from app.models.session import Session
from app.models.pricing import DailyPrice, TrafficLog


class DashboardService:
    """Dashboard data aggregation service"""
    
    def __init__(self, db: AsyncSession):
        self.db = db
    
    async def get_dashboard_data(self, telegram_id: int) -> Dict[str, Any]:
        """Get complete dashboard data for user"""
        
        # Get user
        user_result = await self.db.execute(
            select(User).where(User.telegram_id == telegram_id)
        )
        user = user_result.scalar_one_or_none()
        
        if not user:
            raise ValueError("User not found")
        
        # Get today's price
        today = date.today()
        price_result = await self.db.execute(
            select(DailyPrice).where(DailyPrice.date == today)
        )
        daily_price = price_result.scalar_one_or_none()
        
        # Get active sessions count
        active_sessions = await self.db.execute(
            select(func.count(Session.id))
            .where(Session.telegram_id == telegram_id)
            .where(Session.is_active == True)
        )
        active_count = active_sessions.scalar()
        
        # Get today's earnings
        today_earnings = await self._get_today_earnings(telegram_id)
        
        # Get week earnings
        week_earnings = await self._get_week_earnings(telegram_id)
        
        return {
            "user": {
                "telegram_id": user.telegram_id,
                "first_name": user.first_name,
                "username": user.username,
                "photo_url": user.photo_url,
                "auth_date": user.auth_date.isoformat() if user.auth_date else None,
            },
            "balance": {
                "usd": round(user.balance_usd, 2),
                "sent_mb": round(user.sent_mb, 2),
                "used_mb": round(user.used_mb, 2),
            },
            "traffic": {
                "sent_mb": round(user.sent_mb, 2),
                "used_mb": round(user.used_mb, 2),
                "remaining_mb": round(user.sent_mb - user.used_mb, 2),
                "active_sessions": active_count,
            },
            "pricing": {
                "price_per_gb": daily_price.price_per_gb if daily_price else 1.50,
                "price_per_mb": daily_price.price_per_mb if daily_price else 0.0015,
                "message": daily_price.message if daily_price else "Current traffic price",
                "date": today.isoformat(),
            },
            "mini_stats": {
                "today_earning": round(today_earnings, 2),
                "week_earning": round(week_earnings, 2),
            }
        }
    
    async def _get_today_earnings(self, telegram_id: int) -> float:
        """Get today's earnings"""
        today = date.today()
        
        result = await self.db.execute(
            select(func.sum(Session.earned_usd))
            .where(Session.telegram_id == telegram_id)
            .where(func.date(Session.start_time) == today)
        )
        earnings = result.scalar()
        
        return float(earnings or 0.0)
    
    async def _get_week_earnings(self, telegram_id: int) -> float:
        """Get this week's earnings"""
        week_ago = date.today() - timedelta(days=7)
        
        result = await self.db.execute(
            select(func.sum(Session.earned_usd))
            .where(Session.telegram_id == telegram_id)
            .where(func.date(Session.start_time) >= week_ago)
        )
        earnings = result.scalar()
        
        return float(earnings or 0.0)
    
    async def refresh_balance(self, telegram_id: int) -> Dict[str, Any]:
        """Refresh user balance from pending transactions"""
        
        user_result = await self.db.execute(
            select(User).where(User.telegram_id == telegram_id)
        )
        user = user_result.scalar_one_or_none()
        
        if not user:
            raise ValueError("User not found")
        
        # In production, this would:
        # 1. Check pending_chunks
        # 2. Calculate new earnings
        # 3. Update balance
        # For now, just return current balance
        
        return {
            "status": "success",
            "new_balance_usd": round(user.balance_usd, 2),
            "delta": 0.0
        }
