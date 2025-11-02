from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
import httpx
import logging

from app.models.user import User
from app.models.notification import Notification, FCMToken
from app.core.config import settings

logger = logging.getLogger(__name__)


class NotificationService:
    """
    REAL Firebase Cloud Messaging implementation
    Sends actual push notifications
    """
    
    FCM_URL = "https://fcm.googleapis.com/fcm/send"
    BATCH_SIZE = 500
    
    def __init__(self, db: AsyncSession):
        self.db = db
    
    async def send_to_user(
        self,
        telegram_id: int,
        title: str,
        body: str,
        data: Optional[Dict] = None,
        notif_type: str = "general"
    ) -> bool:
        """
        REAL send notification to single user
        """
        # Get user's active FCM tokens
        result = await self.db.execute(
            select(FCMToken)
            .where(FCMToken.telegram_id == telegram_id)
            .where(FCMToken.is_active == True)
        )
        tokens = result.scalars().all()
        
        if not tokens:
            logger.debug(f"No FCM tokens for user {telegram_id}")
            return False
        
        # Send to all user's devices
        success_count = 0
        for token_obj in tokens:
            try:
                sent = await self._send_fcm_notification(
                    token=token_obj.token,
                    title=title,
                    body=body,
                    data=data or {}
                )
                
                if sent:
                    success_count += 1
                    token_obj.last_used = datetime.utcnow()
                else:
                    # Token might be invalid
                    token_obj.is_active = False
            
            except Exception as e:
                logger.error(f"Failed to send to token {token_obj.id}: {e}")
                token_obj.is_active = False
        
        # Save notification to database
        notification = Notification(
            telegram_id=telegram_id,
            title=title,
            body=body,
            type=notif_type,
            is_read=False,
            data=data,
            sent_at=datetime.utcnow(),
            created_at=datetime.utcnow()
        )
        self.db.add(notification)
        
        await self.db.commit()
        
        logger.info(f"Notification sent to user {telegram_id}: {title}")
        
        return success_count > 0
    
    async def send_to_multiple(
        self,
        telegram_ids: List[int],
        title: str,
        body: str,
        data: Optional[Dict] = None,
        notif_type: str = "general"
    ) -> Dict[str, int]:
        """
        REAL batch send to multiple users
        """
        sent_count = 0
        failed_count = 0
        
        for telegram_id in telegram_ids:
            try:
                success = await self.send_to_user(
                    telegram_id=telegram_id,
                    title=title,
                    body=body,
                    data=data,
                    notif_type=notif_type
                )
                
                if success:
                    sent_count += 1
                else:
                    failed_count += 1
            
            except Exception as e:
                logger.error(f"Failed to send to user {telegram_id}: {e}")
                failed_count += 1
        
        logger.info(f"Batch notification: sent={sent_count}, failed={failed_count}")
        
        return {
            "sent": sent_count,
            "failed": failed_count,
            "total": len(telegram_ids)
        }
    
    async def send_to_all_active_users(
        self,
        title: str,
        body: str,
        data: Optional[Dict] = None,
        notif_type: str = "general"
    ) -> Dict[str, int]:
        """
        REAL send to all active users (last 7 days)
        """
        # Get active users
        week_ago = datetime.utcnow() - timedelta(days=7)
        result = await self.db.execute(
            select(User.telegram_id)
            .where(User.is_active == True)
            .where(User.is_banned == False)
            .where(User.last_seen >= week_ago)
        )
        
        telegram_ids = [row[0] for row in result.all()]
        
        logger.info(f"Sending to {len(telegram_ids)} active users")
        
        return await self.send_to_multiple(
            telegram_ids=telegram_ids,
            title=title,
            body=body,
            data=data,
            notif_type=notif_type
        )
    
    async def _send_fcm_notification(
        self,
        token: str,
        title: str,
        body: str,
        data: Dict[str, Any]
    ) -> bool:
        """
        REAL FCM API call
        Sends actual HTTP request to Firebase
        """
        if not settings.FCM_SERVER_KEY:
            logger.warning("FCM_SERVER_KEY not configured")
            return False
        
        payload = {
            "to": token,
            "notification": {
                "title": title,
                "body": body,
                "sound": "default",
                "badge": 1
            },
            "data": data,
            "priority": "high"
        }
        
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"key={settings.FCM_SERVER_KEY}"
        }
        
        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    self.FCM_URL,
                    json=payload,
                    headers=headers,
                    timeout=10.0
                )
                
                if response.status_code == 200:
                    result = response.json()
                    
                    if result.get('success') == 1:
                        logger.debug(f"FCM notification sent successfully")
                        return True
                    else:
                        error = result.get('results', [{}])[0].get('error')
                        logger.warning(f"FCM error: {error}")
                        return False
                else:
                    logger.error(f"FCM HTTP error: {response.status_code}")
                    return False
        
        except httpx.TimeoutException:
            logger.error("FCM request timeout")
            return False
        except Exception as e:
            logger.error(f"FCM send error: {e}")
            return False
    
    async def register_device(
        self,
        telegram_id: int,
        fcm_token: str,
        device_info: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        REAL device token registration
        """
        # Check if token exists
        result = await self.db.execute(
            select(FCMToken)
            .where(FCMToken.telegram_id == telegram_id)
            .where(FCMToken.token == fcm_token)
        )
        existing_token = result.scalar_one_or_none()
        
        if existing_token:
            # Update last used
            existing_token.last_used = datetime.utcnow()
            existing_token.is_active = True
        else:
            # Create new token
            new_token = FCMToken(
                telegram_id=telegram_id,
                token=fcm_token,
                device_info=device_info,
                is_active=True,
                created_at=datetime.utcnow(),
                last_used=datetime.utcnow()
            )
            self.db.add(new_token)
        
        await self.db.commit()
        
        logger.info(f"FCM token registered for user {telegram_id}")
        
        return {
            "status": "success",
            "message": "Device token registered"
        }
    
    # Specific notification types
    
    async def send_balance_update(
        self,
        telegram_id: int,
        amount: float,
        new_balance: float
    ):
        """Send balance update notification"""
        await self.send_to_user(
            telegram_id=telegram_id,
            title="?? Balans yangilandi!",
            body=f"+${amount:.2f} qo'shildi. Yangi balans: ${new_balance:.2f}",
            data={
                "type": "balance_updated",
                "amount": amount,
                "new_balance": new_balance
            },
            notif_type="balance_updated"
        )
    
    async def send_withdraw_status(
        self,
        telegram_id: int,
        withdraw_id: int,
        status: str,
        amount: float,
        tx_hash: Optional[str] = None
    ):
        """Send withdraw status notification"""
        status_messages = {
            "pending": "? Yechish so'rovingiz qabul qilindi",
            "processing": "?? To'lov jarayoni boshlandi",
            "completed": f"? ${amount:.2f} muvaffaqiyatli yechildi!",
            "failed": "? To'lov amalga oshmadi"
        }
        
        title = status_messages.get(status, "Yechish yangiligi")
        body = f"${amount:.2f} - {status}"
        
        if tx_hash:
            body += f"\nTX: {tx_hash[:16]}..."
        
        await self.send_to_user(
            telegram_id=telegram_id,
            title=title,
            body=body,
            data={
                "type": "withdraw_status",
                "withdraw_id": withdraw_id,
                "status": status,
                "amount": amount,
                "tx_hash": tx_hash
            },
            notif_type="withdraw_status"
        )
    
    async def send_session_completed(
        self,
        telegram_id: int,
        session_id: str,
        duration: str,
        mb_sent: float,
        earned: float
    ):
        """Send session completion notification"""
        await self.send_to_user(
            telegram_id=telegram_id,
            title="? Sessiya tugallandi",
            body=f"Davomiyligi: {duration}\nYuborilgan: {mb_sent:.0f} MB\nDaromad: ${earned:.4f}",
            data={
                "type": "session_completed",
                "session_id": session_id,
                "duration": duration,
                "mb_sent": mb_sent,
                "earned": earned
            },
            notif_type="session_completed"
        )
    
    async def send_daily_price_notification(
        self,
        price_per_gb: float,
        message: str
    ):
        """Send daily price announcement to all active users"""
        await self.send_to_all_active_users(
            title="?? Kunlik narx e'loni",
            body=f"Bugungi narx: ${price_per_gb:.2f}/GB\n{message}",
            data={
                "type": "daily_price",
                "price_per_gb": price_per_gb,
                "message": message
            },
            notif_type="daily_price"
        )
