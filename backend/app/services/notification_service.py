from datetime import datetime
from typing import List, Dict, Any, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
import httpx
import logging

from app.models.user import User
from app.models.notification import NotificationLog
from app.core.config import settings

logger = logging.getLogger(__name__)


class NotificationService:
    """Push notification service using FCM"""
    
    def __init__(self, db: AsyncSession):
        self.db = db
        self.fcm_url = "https://fcm.googleapis.com/fcm/send"
        self.fcm_key = settings.FCM_SERVER_KEY
    
    async def send_to_user(
        self,
        telegram_id: int,
        title: str,
        body: str,
        notif_type: str,
        data: Optional[Dict[str, Any]] = None
    ) -> bool:
        """Send push notification to specific user"""
        
        # Get user device token
        result = await self.db.execute(
            select(User).where(User.telegram_id == telegram_id)
        )
        user = result.scalar_one_or_none()
        
        if not user or not user.device_token:
            logger.warning(f"User {telegram_id} has no device token")
            return False
        
        if not user.notifications_enabled:
            logger.info(f"User {telegram_id} has notifications disabled")
            return False
        
        # Send FCM notification
        success = await self._send_fcm_notification(
            device_token=user.device_token,
            title=title,
            body=body,
            data=data or {}
        )
        
        # Log notification
        log = NotificationLog(
            telegram_id=telegram_id,
            device_id=user.device_token[:20],  # Store partial token
            notif_type=notif_type,
            title=title,
            body=body,
            delivered=success,
        )
        self.db.add(log)
        await self.db.commit()
        
        return success
    
    async def send_to_multiple(
        self,
        telegram_ids: List[int],
        title: str,
        body: str,
        notif_type: str,
        data: Optional[Dict[str, Any]] = None
    ) -> Dict[str, int]:
        """Send notification to multiple users"""
        
        sent = 0
        failed = 0
        
        for telegram_id in telegram_ids:
            try:
                success = await self.send_to_user(
                    telegram_id=telegram_id,
                    title=title,
                    body=body,
                    notif_type=notif_type,
                    data=data
                )
                if success:
                    sent += 1
                else:
                    failed += 1
            except Exception as e:
                logger.error(f"Error sending notification to {telegram_id}: {e}")
                failed += 1
        
        return {"sent": sent, "failed": failed}
    
    async def send_to_all_active_users(
        self,
        title: str,
        body: str,
        notif_type: str,
        data: Optional[Dict[str, Any]] = None
    ) -> Dict[str, int]:
        """Send notification to all active users"""
        
        # Get all users with notifications enabled
        result = await self.db.execute(
            select(User)
            .where(User.notifications_enabled == True)
            .where(User.device_token.isnot(None))
            .where(User.is_active == True)
        )
        users = result.scalars().all()
        
        telegram_ids = [user.telegram_id for user in users]
        
        return await self.send_to_multiple(
            telegram_ids=telegram_ids,
            title=title,
            body=body,
            notif_type=notif_type,
            data=data
        )
    
    async def _send_fcm_notification(
        self,
        device_token: str,
        title: str,
        body: str,
        data: Dict[str, Any]
    ) -> bool:
        """Send FCM notification via HTTP"""
        
        if not self.fcm_key:
            logger.warning("FCM server key not configured")
            return False
        
        headers = {
            "Authorization": f"key={self.fcm_key}",
            "Content-Type": "application/json",
        }
        
        payload = {
            "to": device_token,
            "notification": {
                "title": title,
                "body": body,
                "sound": "default",
                "badge": "1",
            },
            "data": data,
            "priority": "high",
        }
        
        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    self.fcm_url,
                    json=payload,
                    headers=headers,
                    timeout=30.0
                )
                
                if response.status_code == 200:
                    logger.info(f"FCM notification sent successfully")
                    return True
                else:
                    logger.error(f"FCM error: {response.status_code} - {response.text}")
                    return False
        
        except Exception as e:
            logger.error(f"FCM request failed: {e}")
            return False
    
    async def register_device(
        self,
        telegram_id: int,
        device_token: str,
        notifications_enabled: bool = True
    ) -> bool:
        """Register or update device token"""
        
        result = await self.db.execute(
            select(User).where(User.telegram_id == telegram_id)
        )
        user = result.scalar_one_or_none()
        
        if not user:
            logger.warning(f"User {telegram_id} not found")
            return False
        
        user.device_token = device_token
        user.notifications_enabled = notifications_enabled
        
        await self.db.commit()
        
        return True
    
    # Predefined notification types
    
    async def notify_balance_updated(
        self,
        telegram_id: int,
        amount: float,
        new_balance: float
    ):
        """Notify user about balance update"""
        return await self.send_to_user(
            telegram_id=telegram_id,
            title="?? Balans yangilandi!",
            body=f"+${amount:.2f} qo'shildi. Yangi balans: ${new_balance:.2f}",
            notif_type="balance_updated",
            data={"amount": str(amount), "new_balance": str(new_balance)}
        )
    
    async def notify_withdraw_status(
        self,
        telegram_id: int,
        amount: float,
        status: str,
        message: str
    ):
        """Notify user about withdraw status"""
        emoji = {
            "pending": "?",
            "processing": "??",
            "completed": "?",
            "failed": "?"
        }.get(status, "??")
        
        return await self.send_to_user(
            telegram_id=telegram_id,
            title=f"{emoji} Pul yechish - {status}",
            body=f"${amount:.2f} - {message}",
            notif_type="withdraw_status",
            data={"amount": str(amount), "status": status}
        )
    
    async def notify_session_completed(
        self,
        telegram_id: int,
        duration: str,
        mb_sent: float,
        earned: float
    ):
        """Notify user about completed session"""
        return await self.send_to_user(
            telegram_id=telegram_id,
            title="?? Sessiya tugadi",
            body=f"Davomiyligi: {duration}. Yuborilgan: {mb_sent:.0f}MB. Daromad: ${earned:.3f}",
            notif_type="session_completed",
            data={
                "duration": duration,
                "mb_sent": str(mb_sent),
                "earned": str(earned)
            }
        )
    
    async def notify_daily_price(
        self,
        price_per_gb: float,
        message: str
    ):
        """Notify all users about new daily price"""
        return await self.send_to_all_active_users(
            title="?? Kunlik narx yangilandi!",
            body=f"Bugungi narx: ${price_per_gb:.2f}/GB. {message}",
            notif_type="daily_price",
            data={"price_per_gb": str(price_per_gb)}
        )
