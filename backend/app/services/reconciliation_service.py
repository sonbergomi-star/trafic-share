from datetime import datetime, timedelta
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_
from typing import Dict, Any, List
import logging

from app.models.session import Session, SessionReport
from app.models.user import User
from app.models.transaction import Transaction
from app.models.pricing import TrafficLog, DailyPrice
from app.utils.helpers import Helpers

logger = logging.getLogger(__name__)


class ReconciliationService:
    """
    Reconciliation service for verifying and correcting data consistency
    between client reports and server calculations
    """
    
    TOLERANCE_PERCENT = 1.0  # 1% tolerance
    TOLERANCE_MB = 5.0  # 5 MB tolerance
    
    def __init__(self, db: AsyncSession):
        self.db = db
    
    async def reconcile_session(self, session_id: str) -> Dict[str, Any]:
        """Reconcile a single session"""
        
        # Get session
        result = await self.db.execute(
            select(Session).where(Session.session_id == session_id)
        )
        session = result.scalar_one_or_none()
        
        if not session:
            raise ValueError("Session not found")
        
        # Get all reports for this session
        reports_result = await self.db.execute(
            select(SessionReport)
            .where(SessionReport.session_id == session.id)
            .order_by(SessionReport.timestamp)
        )
        reports = reports_result.scalars().all()
        
        # Calculate server-side total from reports
        server_total_mb = sum(report.delta_mb for report in reports)
        
        # Compare with client-reported cumulative
        client_total_mb = session.local_counted_mb
        
        # Calculate discrepancy
        discrepancy_mb = abs(server_total_mb - client_total_mb)
        discrepancy_percent = Helpers.calculate_percentage(
            discrepancy_mb,
            max(server_total_mb, client_total_mb)
        )
        
        # Check if within tolerance
        is_consistent = (
            discrepancy_mb <= self.TOLERANCE_MB or
            discrepancy_percent <= self.TOLERANCE_PERCENT
        )
        
        # Update session with reconciled data
        session.server_counted_mb = server_total_mb
        
        if not is_consistent:
            logger.warning(
                f"Session {session_id} has discrepancy: "
                f"client={client_total_mb}MB, server={server_total_mb}MB, "
                f"diff={discrepancy_mb}MB ({discrepancy_percent}%)"
            )
        
        await self.db.commit()
        
        return {
            "session_id": session_id,
            "is_consistent": is_consistent,
            "client_reported_mb": client_total_mb,
            "server_calculated_mb": server_total_mb,
            "discrepancy_mb": discrepancy_mb,
            "discrepancy_percent": discrepancy_percent,
            "report_count": len(reports),
        }
    
    async def reconcile_user_balance(self, telegram_id: int) -> Dict[str, Any]:
        """Reconcile user balance from all sources"""
        
        # Get user
        user_result = await self.db.execute(
            select(User).where(User.telegram_id == telegram_id)
        )
        user = user_result.scalar_one_or_none()
        
        if not user:
            raise ValueError("User not found")
        
        # Calculate balance from transactions
        transactions_result = await self.db.execute(
            select(func.sum(Transaction.amount_usd))
            .where(Transaction.telegram_id == telegram_id)
            .where(Transaction.status == 'completed')
        )
        calculated_balance = transactions_result.scalar() or 0.0
        
        # Calculate earnings from sessions
        sessions_result = await self.db.execute(
            select(func.sum(Session.earned_usd))
            .where(Session.telegram_id == telegram_id)
            .where(Session.status == 'completed')
        )
        session_earnings = sessions_result.scalar() or 0.0
        
        # Current balance in DB
        current_balance = user.balance_usd
        
        # Expected balance (earnings minus withdrawals)
        withdrawals_result = await self.db.execute(
            select(func.sum(Transaction.amount_usd))
            .where(Transaction.telegram_id == telegram_id)
            .where(Transaction.type == 'withdraw')
            .where(Transaction.status == 'completed')
        )
        total_withdrawals = abs(withdrawals_result.scalar() or 0.0)
        
        expected_balance = session_earnings - total_withdrawals
        
        # Calculate discrepancy
        discrepancy = abs(current_balance - expected_balance)
        
        return {
            "telegram_id": telegram_id,
            "current_balance": current_balance,
            "expected_balance": expected_balance,
            "discrepancy": discrepancy,
            "is_consistent": discrepancy < 0.01,  # 1 cent tolerance
            "breakdown": {
                "session_earnings": session_earnings,
                "total_withdrawals": total_withdrawals,
                "other_transactions": calculated_balance - session_earnings + total_withdrawals,
            }
        }
    
    async def reconcile_daily_stats(self, target_date: date) -> Dict[str, Any]:
        """Reconcile daily statistics for all users"""
        
        start_datetime = datetime.combine(target_date, datetime.min.time())
        end_datetime = datetime.combine(target_date, datetime.max.time())
        
        # Get all users with sessions on this day
        result = await self.db.execute(
            select(
                Session.telegram_id,
                func.sum(Session.sent_mb).label('sent_mb'),
                func.sum(Session.server_counted_mb).label('sold_mb'),
                func.sum(Session.earned_usd).label('profit_usd'),
            )
            .where(Session.start_time >= start_datetime)
            .where(Session.start_time <= end_datetime)
            .where(Session.status == 'completed')
            .group_by(Session.telegram_id)
        )
        
        user_stats = result.all()
        
        # Get daily price
        price_result = await self.db.execute(
            select(DailyPrice).where(DailyPrice.date == target_date)
        )
        daily_price = price_result.scalar_one_or_none()
        price_per_mb = daily_price.price_per_mb if daily_price else 0.0015
        
        # Create or update traffic logs
        records_created = 0
        records_updated = 0
        
        for stat in user_stats:
            # Check if log exists
            log_result = await self.db.execute(
                select(TrafficLog)
                .where(TrafficLog.telegram_id == stat.telegram_id)
                .where(TrafficLog.date == target_date)
                .where(TrafficLog.period == 'daily')
            )
            log = log_result.scalar_one_or_none()
            
            if log:
                log.sent_mb = float(stat.sent_mb or 0)
                log.sold_mb = float(stat.sold_mb or 0)
                log.profit_usd = float(stat.profit_usd or 0)
                log.price_per_mb = price_per_mb
                records_updated += 1
            else:
                log = TrafficLog(
                    telegram_id=stat.telegram_id,
                    sent_mb=float(stat.sent_mb or 0),
                    sold_mb=float(stat.sold_mb or 0),
                    profit_usd=float(stat.profit_usd or 0),
                    price_per_mb=price_per_mb,
                    period='daily',
                    date=target_date,
                )
                self.db.add(log)
                records_created += 1
        
        await self.db.commit()
        
        return {
            "date": target_date.isoformat(),
            "users_processed": len(user_stats),
            "records_created": records_created,
            "records_updated": records_updated,
            "total_profit_usd": sum(float(s.profit_usd or 0) for s in user_stats),
        }
    
    async def reconcile_weekly_stats(self) -> Dict[str, Any]:
        """Reconcile weekly statistics"""
        
        # Get current week
        today = date.today()
        week_start = today - timedelta(days=today.weekday())
        week_end = week_start + timedelta(days=6)
        
        # Get all daily logs for the week
        result = await self.db.execute(
            select(
                TrafficLog.telegram_id,
                func.sum(TrafficLog.sent_mb).label('sent_mb'),
                func.sum(TrafficLog.sold_mb).label('sold_mb'),
                func.sum(TrafficLog.profit_usd).label('profit_usd'),
                func.avg(TrafficLog.price_per_mb).label('avg_price'),
            )
            .where(TrafficLog.date >= week_start)
            .where(TrafficLog.date <= week_end)
            .where(TrafficLog.period == 'daily')
            .group_by(TrafficLog.telegram_id)
        )
        
        weekly_stats = result.all()
        
        # Create or update weekly logs
        records_processed = 0
        
        for stat in weekly_stats:
            # Check if weekly log exists
            log_result = await self.db.execute(
                select(TrafficLog)
                .where(TrafficLog.telegram_id == stat.telegram_id)
                .where(TrafficLog.date == week_start)
                .where(TrafficLog.period == 'weekly')
            )
            log = log_result.scalar_one_or_none()
            
            if log:
                log.sent_mb = float(stat.sent_mb or 0)
                log.sold_mb = float(stat.sold_mb or 0)
                log.profit_usd = float(stat.profit_usd or 0)
                log.price_per_mb = float(stat.avg_price or 0)
            else:
                log = TrafficLog(
                    telegram_id=stat.telegram_id,
                    sent_mb=float(stat.sent_mb or 0),
                    sold_mb=float(stat.sold_mb or 0),
                    profit_usd=float(stat.profit_usd or 0),
                    price_per_mb=float(stat.avg_price or 0),
                    period='weekly',
                    date=week_start,
                )
                self.db.add(log)
            
            records_processed += 1
        
        await self.db.commit()
        
        return {
            "week_start": week_start.isoformat(),
            "week_end": week_end.isoformat(),
            "users_processed": records_processed,
        }
    
    async def reconcile_monthly_stats(self) -> Dict[str, Any]:
        """Reconcile monthly statistics"""
        
        # Get current month
        today = date.today()
        month_start = date(today.year, today.month, 1)
        
        # Get next month start
        if today.month == 12:
            month_end = date(today.year + 1, 1, 1) - timedelta(days=1)
        else:
            month_end = date(today.year, today.month + 1, 1) - timedelta(days=1)
        
        # Get all daily logs for the month
        result = await self.db.execute(
            select(
                TrafficLog.telegram_id,
                func.sum(TrafficLog.sent_mb).label('sent_mb'),
                func.sum(TrafficLog.sold_mb).label('sold_mb'),
                func.sum(TrafficLog.profit_usd).label('profit_usd'),
                func.avg(TrafficLog.price_per_mb).label('avg_price'),
            )
            .where(TrafficLog.date >= month_start)
            .where(TrafficLog.date <= month_end)
            .where(TrafficLog.period == 'daily')
            .group_by(TrafficLog.telegram_id)
        )
        
        monthly_stats = result.all()
        
        # Create or update monthly logs
        records_processed = 0
        
        for stat in monthly_stats:
            log_result = await self.db.execute(
                select(TrafficLog)
                .where(TrafficLog.telegram_id == stat.telegram_id)
                .where(TrafficLog.date == month_start)
                .where(TrafficLog.period == 'monthly')
            )
            log = log_result.scalar_one_or_none()
            
            if log:
                log.sent_mb = float(stat.sent_mb or 0)
                log.sold_mb = float(stat.sold_mb or 0)
                log.profit_usd = float(stat.profit_usd or 0)
                log.price_per_mb = float(stat.avg_price or 0)
            else:
                log = TrafficLog(
                    telegram_id=stat.telegram_id,
                    sent_mb=float(stat.sent_mb or 0),
                    sold_mb=float(stat.sold_mb or 0),
                    profit_usd=float(stat.profit_usd or 0),
                    price_per_mb=float(stat.avg_price or 0),
                    period='monthly',
                    date=month_start,
                )
                self.db.add(log)
            
            records_processed += 1
        
        await self.db.commit()
        
        return {
            "month": f"{today.year}-{today.month:02d}",
            "month_start": month_start.isoformat(),
            "month_end": month_end.isoformat(),
            "users_processed": records_processed,
        }
    
    async def find_orphaned_sessions(self) -> List[Dict]:
        """Find sessions that are stuck in 'active' state"""
        
        # Sessions active for more than 2 hours without heartbeat
        timeout_threshold = datetime.utcnow() - timedelta(hours=2)
        
        result = await self.db.execute(
            select(Session)
            .where(Session.is_active == True)
            .where(
                or_(
                    Session.last_report_at < timeout_threshold,
                    and_(
                        Session.last_report_at.is_(None),
                        Session.start_time < timeout_threshold
                    )
                )
            )
        )
        
        orphaned_sessions = result.scalars().all()
        
        return [
            {
                "session_id": s.session_id,
                "telegram_id": s.telegram_id,
                "start_time": s.start_time.isoformat(),
                "last_report_at": s.last_report_at.isoformat() if s.last_report_at else None,
                "hours_since_start": (datetime.utcnow() - s.start_time).total_seconds() / 3600,
            }
            for s in orphaned_sessions
        ]
    
    async def close_orphaned_sessions(self) -> Dict[str, Any]:
        """Close orphaned sessions"""
        
        orphaned = await self.find_orphaned_sessions()
        closed_count = 0
        
        for session_info in orphaned:
            # Get session
            result = await self.db.execute(
                select(Session).where(Session.session_id == session_info['session_id'])
            )
            session = result.scalar_one_or_none()
            
            if session:
                session.is_active = False
                session.status = 'failed'
                session.end_time = datetime.utcnow()
                
                # Calculate duration
                if session.start_time:
                    duration = Helpers.calculate_duration(session.start_time, session.end_time)
                    session.duration = duration
                
                closed_count += 1
        
        await self.db.commit()
        
        return {
            "orphaned_found": len(orphaned),
            "sessions_closed": closed_count,
            "timestamp": datetime.utcnow().isoformat(),
        }
    
    async def verify_earnings_calculation(self, session_id: str) -> Dict[str, Any]:
        """Verify earnings calculation for a session"""
        
        result = await self.db.execute(
            select(Session).where(Session.session_id == session_id)
        )
        session = result.scalar_one_or_none()
        
        if not session:
            raise ValueError("Session not found")
        
        # Get pricing for session date
        if session.start_time:
            session_date = session.start_time.date()
            price_result = await self.db.execute(
                select(DailyPrice).where(DailyPrice.date == session_date)
            )
            daily_price = price_result.scalar_one_or_none()
            price_per_mb = daily_price.price_per_mb if daily_price else 0.0015
        else:
            price_per_mb = 0.0015
        
        # Calculate expected earnings
        expected_earnings = session.server_counted_mb * price_per_mb
        current_earnings = session.earned_usd or 0.0
        
        discrepancy = abs(expected_earnings - current_earnings)
        
        # Update if discrepancy is significant
        if discrepancy > 0.01:  # More than 1 cent
            session.earned_usd = expected_earnings
            await self.db.commit()
            logger.info(f"Corrected earnings for session {session_id}: {current_earnings} -> {expected_earnings}")
        
        return {
            "session_id": session_id,
            "current_earnings": current_earnings,
            "expected_earnings": expected_earnings,
            "discrepancy": discrepancy,
            "corrected": discrepancy > 0.01,
            "price_per_mb": price_per_mb,
            "traffic_mb": session.server_counted_mb,
        }
    
    async def run_full_reconciliation(self) -> Dict[str, Any]:
        """Run full reconciliation process"""
        
        logger.info("Starting full reconciliation process...")
        
        # 1. Close orphaned sessions
        orphaned_result = await self.close_orphaned_sessions()
        
        # 2. Reconcile today's stats
        today = date.today()
        daily_result = await self.reconcile_daily_stats(today)
        
        # 3. Reconcile weekly stats
        weekly_result = await self.reconcile_weekly_stats()
        
        # 4. Reconcile monthly stats  
        monthly_result = await self.reconcile_monthly_stats()
        
        logger.info("Full reconciliation completed")
        
        return {
            "status": "completed",
            "timestamp": datetime.utcnow().isoformat(),
            "orphaned_sessions": orphaned_result,
            "daily_reconciliation": daily_result,
            "weekly_reconciliation": weekly_result,
            "monthly_reconciliation": monthly_result,
        }
