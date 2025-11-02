from datetime import datetime, date, timedelta
from sqlalchemy import select, delete
import logging

from app.tasks.celery_app import celery_app
from app.core.database import AsyncSessionLocal
from app.services.reconciliation_service import ReconciliationService
from app.services.notification_service import NotificationService
from app.services.pricing_service import PricingService
from app.models.user import User
from app.models.session import Session, SessionReport
from app.models.notification import Notification

logger = logging.getLogger(__name__)


@celery_app.task(name="app.tasks.periodic_tasks.close_orphaned_sessions")
def close_orphaned_sessions():
    """Close sessions that are stuck in active state"""
    
    import asyncio
    
    async def _close_orphaned():
        async with AsyncSessionLocal() as db:
            reconciliation_service = ReconciliationService(db)
            result = await reconciliation_service.close_orphaned_sessions()
            logger.info(f"Closed {result['sessions_closed']} orphaned sessions")
            return result
    
    loop = asyncio.get_event_loop()
    return loop.run_until_complete(_close_orphaned())


@celery_app.task(name="app.tasks.periodic_tasks.reconcile_daily_stats")
def reconcile_daily_stats():
    """Reconcile daily statistics"""
    
    import asyncio
    
    async def _reconcile_daily():
        async with AsyncSessionLocal() as db:
            reconciliation_service = ReconciliationService(db)
            yesterday = date.today() - timedelta(days=1)
            result = await reconciliation_service.reconcile_daily_stats(yesterday)
            logger.info(f"Reconciled daily stats for {yesterday}: {result}")
            return result
    
    loop = asyncio.get_event_loop()
    return loop.run_until_complete(_reconcile_daily())


@celery_app.task(name="app.tasks.periodic_tasks.reconcile_weekly_stats")
def reconcile_weekly_stats():
    """Reconcile weekly statistics"""
    
    import asyncio
    
    async def _reconcile_weekly():
        async with AsyncSessionLocal() as db:
            reconciliation_service = ReconciliationService(db)
            result = await reconciliation_service.reconcile_weekly_stats()
            logger.info(f"Reconciled weekly stats: {result}")
            return result
    
    loop = asyncio.get_event_loop()
    return loop.run_until_complete(_reconcile_weekly())


@celery_app.task(name="app.tasks.periodic_tasks.reconcile_monthly_stats")
def reconcile_monthly_stats():
    """Reconcile monthly statistics"""
    
    import asyncio
    
    async def _reconcile_monthly():
        async with AsyncSessionLocal() as db:
            reconciliation_service = ReconciliationService(db)
            result = await reconciliation_service.reconcile_monthly_stats()
            logger.info(f"Reconciled monthly stats: {result}")
            return result
    
    loop = asyncio.get_event_loop()
    return loop.run_until_complete(_reconcile_monthly())


@celery_app.task(name="app.tasks.periodic_tasks.send_daily_price_notifications")
def send_daily_price_notifications():
    """Send daily price update notifications to all active users"""
    
    import asyncio
    
    async def _send_notifications():
        async with AsyncSessionLocal() as db:
            # Get today's price
            pricing_service = PricingService(db)
            price_data = await pricing_service.get_current_price()
            
            if not price_data:
                logger.warning("No price data available for today")
                return
            
            price_per_gb = price_data['price_per_gb']
            message = price_data.get('message', '')
            
            # Send notifications
            notification_service = NotificationService(db)
            await notification_service.send_daily_price_notification(
                price_per_gb=price_per_gb,
                message=message
            )
            
            logger.info(f"Sent daily price notifications: ${price_per_gb}/GB")
    
    loop = asyncio.get_event_loop()
    return loop.run_until_complete(_send_notifications())


@celery_app.task(name="app.tasks.periodic_tasks.cleanup_old_data")
def cleanup_old_data():
    """Clean up old data (logs, expired sessions, etc.)"""
    
    import asyncio
    
    async def _cleanup():
        async with AsyncSessionLocal() as db:
            # Delete old notifications (older than 30 days)
            cutoff_date = datetime.utcnow() - timedelta(days=30)
            
            deleted_notifications = await db.execute(
                delete(Notification).where(Notification.created_at < cutoff_date)
            )
            
            # Delete old session reports (older than 90 days)
            report_cutoff = datetime.utcnow() - timedelta(days=90)
            deleted_reports = await db.execute(
                delete(SessionReport).where(SessionReport.timestamp < report_cutoff)
            )
            
            await db.commit()
            
            result = {
                "deleted_notifications": deleted_notifications.rowcount,
                "deleted_reports": deleted_reports.rowcount,
            }
            
            logger.info(f"Cleanup completed: {result}")
            return result
    
    loop = asyncio.get_event_loop()
    return loop.run_until_complete(_cleanup())


@celery_app.task(name="app.tasks.periodic_tasks.generate_analytics_reports")
def generate_analytics_reports():
    """Generate daily analytics reports for admins"""
    
    import asyncio
    
    async def _generate_reports():
        async with AsyncSessionLocal() as db:
            from app.services.analytics_service import AnalyticsService
            
            analytics_service = AnalyticsService(db)
            platform_stats = await analytics_service.get_platform_analytics()
            
            logger.info(f"Platform stats: {platform_stats}")
            
            # TODO: Send report to admin via Telegram
            
            return platform_stats
    
    loop = asyncio.get_event_loop()
    return loop.run_until_complete(_generate_reports())
