from datetime import datetime, timedelta
from sqlalchemy import select
import logging

from app.tasks.celery_app import celery_app
from app.core.database import AsyncSessionLocal
from app.services.notification_service import NotificationService
from app.models.user import User
from app.models.session import Session

logger = logging.getLogger(__name__)


@celery_app.task(name="app.tasks.notification_tasks.send_notification")
def send_notification(telegram_id: int, title: str, body: str, data: dict = None):
    """Send notification to a single user (async task)"""
    
    import asyncio
    
    async def _send():
        async with AsyncSessionLocal() as db:
            notification_service = NotificationService(db)
            await notification_service.send_to_user(
                telegram_id=telegram_id,
                title=title,
                body=body,
                data=data or {}
            )
    
    loop = asyncio.get_event_loop()
    return loop.run_until_complete(_send())


@celery_app.task(name="app.tasks.notification_tasks.send_bulk_notification")
def send_bulk_notification(
    telegram_ids: list,
    title: str,
    body: str,
    data: dict = None
):
    """Send notification to multiple users (async task)"""
    
    import asyncio
    
    async def _send():
        async with AsyncSessionLocal() as db:
            notification_service = NotificationService(db)
            await notification_service.send_to_multiple(
                telegram_ids=telegram_ids,
                title=title,
                body=body,
                data=data or {}
            )
    
    loop = asyncio.get_event_loop()
    return loop.run_until_complete(_send())


@celery_app.task(name="app.tasks.notification_tasks.send_session_summaries")
def send_session_summaries():
    """Send session summaries to users with active sessions in the last 24h"""
    
    import asyncio
    
    async def _send_summaries():
        async with AsyncSessionLocal() as db:
            # Get users with sessions in last 24 hours
            yesterday = datetime.utcnow() - timedelta(hours=24)
            
            result = await db.execute(
                select(Session.telegram_id)
                .where(Session.start_time >= yesterday)
                .group_by(Session.telegram_id)
            )
            
            user_ids = [row[0] for row in result.all()]
            
            notification_service = NotificationService(db)
            
            for telegram_id in user_ids:
                # Get user's session stats for last 24h
                sessions_result = await db.execute(
                    select(Session)
                    .where(Session.telegram_id == telegram_id)
                    .where(Session.start_time >= yesterday)
                )
                sessions = sessions_result.scalars().all()
                
                total_mb = sum(s.sent_mb or 0 for s in sessions)
                total_earned = sum(s.earned_usd or 0 for s in sessions)
                
                # Send summary notification
                await notification_service.send_to_user(
                    telegram_id=telegram_id,
                    title="?? 24 soatlik hisobot",
                    body=f"Yuborilgan: {total_mb:.0f} MB\nDaromad: ${total_earned:.3f}",
                    data={
                        "type": "session_summary",
                        "total_mb": total_mb,
                        "total_earned": total_earned,
                        "session_count": len(sessions),
                    }
                )
            
            logger.info(f"Sent session summaries to {len(user_ids)} users")
    
    loop = asyncio.get_event_loop()
    return loop.run_until_complete(_send_summaries())


@celery_app.task(name="app.tasks.notification_tasks.send_balance_low_warning")
def send_balance_low_warning(telegram_id: int, balance: float):
    """Send warning when user balance is low"""
    
    import asyncio
    
    async def _send():
        async with AsyncSessionLocal() as db:
            notification_service = NotificationService(db)
            await notification_service.send_to_user(
                telegram_id=telegram_id,
                title="?? Balans pastligi",
                body=f"Balans: ${balance:.2f}. Yangi sessiyalar orqali daromad qiling!",
                data={"type": "balance_warning"}
            )
    
    loop = asyncio.get_event_loop()
    return loop.run_until_complete(_send())


@celery_app.task(name="app.tasks.notification_tasks.send_achievement_notification")
def send_achievement_notification(telegram_id: int, achievement: str, details: dict):
    """Send achievement notification to user"""
    
    import asyncio
    
    async def _send():
        async with AsyncSessionLocal() as db:
            notification_service = NotificationService(db)
            
            achievement_messages = {
                "first_session": "?? Birinchi sessiyangiz!",
                "100mb_shared": "?? 100 MB ulashdingiz!",
                "1gb_shared": "?? 1 GB ulashdingiz!",
                "first_dollar": "?? Birinchi dollar ishladingiz!",
                "10_sessions": "? 10 ta sessiya tamom!",
            }
            
            title = achievement_messages.get(achievement, "?? Yangi yutuq!")
            
            await notification_service.send_to_user(
                telegram_id=telegram_id,
                title=title,
                body="Tabriklaymiz! Davom eting!",
                data={"type": "achievement", "achievement": achievement, **details}
            )
    
    loop = asyncio.get_event_loop()
    return loop.run_until_complete(_send())
