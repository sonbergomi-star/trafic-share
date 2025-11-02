from datetime import datetime, date, timedelta
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_, or_
from typing import Dict, Any, List, Optional
import logging

from app.models.user import User
from app.models.session import Session, SessionReport
from app.models.transaction import Transaction
from app.models.pricing import TrafficLog, DailyPrice
from app.utils.helpers import Helpers
from app.utils.formatters import Formatters

logger = logging.getLogger(__name__)


class AnalyticsService:
    """Analytics and reporting service"""
    
    def __init__(self, db: AsyncSession):
        self.db = db
    
    async def get_user_analytics(
        self,
        telegram_id: int,
        period: str = "week"
    ) -> Dict[str, Any]:
        """Get comprehensive user analytics"""
        
        start_date, end_date = self._get_date_range(period)
        
        # Get sessions in period
        sessions_result = await self.db.execute(
            select(Session)
            .where(Session.telegram_id == telegram_id)
            .where(Session.start_time >= start_date)
            .where(Session.start_time <= end_date)
        )
        sessions = sessions_result.scalars().all()
        
        # Calculate aggregates
        total_sessions = len(sessions)
        total_sent_mb = sum(s.sent_mb or 0 for s in sessions)
        total_used_mb = sum(s.server_counted_mb or 0 for s in sessions)
        total_earned = sum(s.earned_usd or 0 for s in sessions)
        
        # Calculate average session duration
        completed_sessions = [s for s in sessions if s.end_time and s.start_time]
        if completed_sessions:
            avg_duration_seconds = sum(
                (s.end_time - s.start_time).total_seconds()
                for s in completed_sessions
            ) / len(completed_sessions)
            avg_duration = Helpers.format_duration(int(avg_duration_seconds))
        else:
            avg_duration = "0s"
        
        # Calculate average speed
        avg_speed = Helpers.safe_divide(
            sum(s.server_counted_mb or 0 for s in completed_sessions),
            sum((s.end_time - s.start_time).total_seconds() for s in completed_sessions if s.end_time)
        )
        
        # Success rate
        completed_count = len([s for s in sessions if s.status == 'completed'])
        success_rate = Helpers.calculate_percentage(completed_count, total_sessions)
        
        return {
            "period": period,
            "start_date": start_date.isoformat(),
            "end_date": end_date.isoformat(),
            "summary": {
                "total_sessions": total_sessions,
                "completed_sessions": completed_count,
                "success_rate": success_rate,
                "total_sent_mb": round(total_sent_mb, 2),
                "total_used_mb": round(total_used_mb, 2),
                "total_earned_usd": round(total_earned, 2),
                "avg_duration": avg_duration,
                "avg_speed_mb_s": round(avg_speed, 2),
            },
            "daily_breakdown": await self._get_daily_breakdown(telegram_id, start_date, end_date)
        }
    
    async def _get_daily_breakdown(
        self,
        telegram_id: int,
        start_date: datetime,
        end_date: datetime
    ) -> List[Dict]:
        """Get daily breakdown of activity"""
        
        result = await self.db.execute(
            select(
                func.date(Session.start_time).label('date'),
                func.count(Session.id).label('sessions'),
                func.sum(Session.sent_mb).label('sent_mb'),
                func.sum(Session.server_counted_mb).label('used_mb'),
                func.sum(Session.earned_usd).label('earned'),
            )
            .where(Session.telegram_id == telegram_id)
            .where(Session.start_time >= start_date)
            .where(Session.start_time <= end_date)
            .group_by(func.date(Session.start_time))
            .order_by(func.date(Session.start_time))
        )
        
        rows = result.all()
        
        return [
            {
                "date": row.date.isoformat() if row.date else None,
                "sessions": row.sessions or 0,
                "sent_mb": float(row.sent_mb or 0),
                "used_mb": float(row.used_mb or 0),
                "earned_usd": float(row.earned or 0),
            }
            for row in rows
        ]
    
    async def get_platform_analytics(self) -> Dict[str, Any]:
        """Get platform-wide analytics (admin only)"""
        
        # Total users
        total_users_result = await self.db.execute(
            select(func.count(User.id))
        )
        total_users = total_users_result.scalar()
        
        # Active users (logged in last 7 days)
        week_ago = datetime.utcnow() - timedelta(days=7)
        active_users_result = await self.db.execute(
            select(func.count(User.id))
            .where(User.last_seen >= week_ago)
        )
        active_users = active_users_result.scalar()
        
        # Total balance
        total_balance_result = await self.db.execute(
            select(func.sum(User.balance_usd))
        )
        total_balance = total_balance_result.scalar() or 0
        
        # Active sessions
        active_sessions_result = await self.db.execute(
            select(func.count(Session.id))
            .where(Session.is_active == True)
        )
        active_sessions = active_sessions_result.scalar()
        
        # Today's statistics
        today = date.today()
        today_start = datetime.combine(today, datetime.min.time())
        
        today_sessions_result = await self.db.execute(
            select(
                func.count(Session.id).label('count'),
                func.sum(Session.sent_mb).label('sent_mb'),
                func.sum(Session.server_counted_mb).label('used_mb'),
                func.sum(Session.earned_usd).label('earned'),
            )
            .where(Session.start_time >= today_start)
        )
        today_stats = today_sessions_result.one()
        
        # Pending withdrawals
        pending_withdrawals_result = await self.db.execute(
            select(
                func.count(Transaction.id).label('count'),
                func.sum(Transaction.amount_usd).label('amount'),
            )
            .where(Transaction.type == 'withdraw')
            .where(Transaction.status.in_(['pending', 'processing']))
        )
        pending_withdrawals = pending_withdrawals_result.one()
        
        return {
            "users": {
                "total": total_users,
                "active_7_days": active_users,
                "active_percentage": Helpers.calculate_percentage(active_users, total_users),
            },
            "balance": {
                "total_usd": round(total_balance, 2),
                "formatted": Formatters.format_currency(total_balance),
            },
            "sessions": {
                "active_now": active_sessions,
                "today_count": today_stats.count or 0,
                "today_traffic_mb": float(today_stats.sent_mb or 0),
                "today_earned_usd": float(today_stats.earned or 0),
            },
            "withdrawals": {
                "pending_count": pending_withdrawals.count or 0,
                "pending_amount_usd": float(pending_withdrawals.amount or 0),
            },
            "timestamp": datetime.utcnow().isoformat(),
        }
    
    async def get_traffic_trends(
        self,
        days: int = 30
    ) -> Dict[str, Any]:
        """Get traffic trends over time"""
        
        start_date = date.today() - timedelta(days=days)
        
        result = await self.db.execute(
            select(
                TrafficLog.date,
                func.sum(TrafficLog.sent_mb).label('total_sent'),
                func.sum(TrafficLog.sold_mb).label('total_sold'),
                func.sum(TrafficLog.profit_usd).label('total_profit'),
                func.avg(TrafficLog.price_per_mb).label('avg_price'),
            )
            .where(TrafficLog.date >= start_date)
            .where(TrafficLog.period == 'daily')
            .group_by(TrafficLog.date)
            .order_by(TrafficLog.date)
        )
        
        rows = result.all()
        
        # Calculate trend (increasing/decreasing)
        if len(rows) >= 2:
            recent_avg = sum(row.total_profit for row in rows[-7:]) / min(7, len(rows[-7:]))
            previous_avg = sum(row.total_profit for row in rows[-14:-7]) / min(7, len(rows[-14:-7])) if len(rows) > 7 else recent_avg
            
            trend = "increasing" if recent_avg > previous_avg else "decreasing"
            trend_percentage = Helpers.calculate_percentage(abs(recent_avg - previous_avg), previous_avg) if previous_avg else 0
        else:
            trend = "stable"
            trend_percentage = 0
        
        return {
            "period_days": days,
            "start_date": start_date.isoformat(),
            "end_date": date.today().isoformat(),
            "trend": trend,
            "trend_percentage": trend_percentage,
            "daily_data": [
                {
                    "date": row.date.isoformat(),
                    "sent_mb": float(row.total_sent or 0),
                    "sold_mb": float(row.total_sold or 0),
                    "profit_usd": float(row.total_profit or 0),
                    "avg_price_per_mb": float(row.avg_price or 0),
                }
                for row in rows
            ]
        }
    
    async def get_user_ranking(
        self,
        period: str = "month",
        limit: int = 10
    ) -> List[Dict]:
        """Get top users by earnings"""
        
        start_date, end_date = self._get_date_range(period)
        
        result = await self.db.execute(
            select(
                User.telegram_id,
                User.username,
                User.first_name,
                func.sum(Session.earned_usd).label('total_earned'),
                func.sum(Session.sent_mb).label('total_sent'),
                func.count(Session.id).label('session_count'),
            )
            .join(Session, Session.telegram_id == User.telegram_id)
            .where(Session.start_time >= start_date)
            .where(Session.start_time <= end_date)
            .group_by(User.telegram_id, User.username, User.first_name)
            .order_by(func.sum(Session.earned_usd).desc())
            .limit(limit)
        )
        
        rows = result.all()
        
        return [
            {
                "rank": idx + 1,
                "telegram_id": row.telegram_id,
                "username": row.username,
                "first_name": row.first_name,
                "total_earned_usd": float(row.total_earned or 0),
                "total_sent_mb": float(row.total_sent or 0),
                "session_count": row.session_count,
            }
            for idx, row in enumerate(rows)
        ]
    
    async def get_hourly_distribution(
        self,
        telegram_id: Optional[int] = None
    ) -> Dict[str, Any]:
        """Get traffic distribution by hour of day"""
        
        query = select(
            func.extract('hour', Session.start_time).label('hour'),
            func.count(Session.id).label('sessions'),
            func.sum(Session.sent_mb).label('sent_mb'),
        ).group_by(func.extract('hour', Session.start_time))
        
        if telegram_id:
            query = query.where(Session.telegram_id == telegram_id)
        
        result = await self.db.execute(query.order_by('hour'))
        rows = result.all()
        
        # Fill in missing hours with zero
        hourly_data = {int(row.hour): {
            "sessions": row.sessions,
            "sent_mb": float(row.sent_mb or 0)
        } for row in rows}
        
        distribution = [
            {
                "hour": hour,
                "sessions": hourly_data.get(hour, {}).get("sessions", 0),
                "sent_mb": hourly_data.get(hour, {}).get("sent_mb", 0),
            }
            for hour in range(24)
        ]
        
        # Find peak hour
        peak_hour = max(distribution, key=lambda x: x['sessions'])
        
        return {
            "distribution": distribution,
            "peak_hour": peak_hour['hour'],
            "peak_sessions": peak_hour['sessions'],
        }
    
    def _get_date_range(self, period: str) -> tuple[datetime, datetime]:
        """Get date range for period"""
        end_date = datetime.utcnow()
        
        if period == "today":
            start_date = datetime.combine(date.today(), datetime.min.time())
        elif period == "week":
            start_date = end_date - timedelta(days=7)
        elif period == "month":
            start_date = end_date - timedelta(days=30)
        elif period == "year":
            start_date = end_date - timedelta(days=365)
        else:
            start_date = end_date - timedelta(days=7)  # Default to week
        
        return start_date, end_date
    
    async def generate_user_report(
        self,
        telegram_id: int,
        start_date: date,
        end_date: date
    ) -> Dict[str, Any]:
        """Generate comprehensive user report"""
        
        start_datetime = datetime.combine(start_date, datetime.min.time())
        end_datetime = datetime.combine(end_date, datetime.max.time())
        
        # Get user
        user_result = await self.db.execute(
            select(User).where(User.telegram_id == telegram_id)
        )
        user = user_result.scalar_one_or_none()
        
        if not user:
            raise ValueError("User not found")
        
        # Get analytics
        analytics = await self.get_user_analytics(telegram_id, "custom")
        
        # Get all sessions in period
        sessions_result = await self.db.execute(
            select(Session)
            .where(Session.telegram_id == telegram_id)
            .where(Session.start_time >= start_datetime)
            .where(Session.start_time <= end_datetime)
            .order_by(Session.start_time.desc())
        )
        sessions = sessions_result.scalars().all()
        
        # Get transactions in period
        transactions_result = await self.db.execute(
            select(Transaction)
            .where(Transaction.telegram_id == telegram_id)
            .where(Transaction.created_at >= start_datetime)
            .where(Transaction.created_at <= end_datetime)
            .order_by(Transaction.created_at.desc())
        )
        transactions = transactions_result.scalars().all()
        
        return {
            "report_generated": datetime.utcnow().isoformat(),
            "period": {
                "start": start_date.isoformat(),
                "end": end_date.isoformat(),
            },
            "user": {
                "telegram_id": user.telegram_id,
                "username": user.username,
                "first_name": user.first_name,
                "balance_usd": user.balance_usd,
            },
            "analytics": analytics,
            "sessions_count": len(sessions),
            "transactions_count": len(transactions),
        }
