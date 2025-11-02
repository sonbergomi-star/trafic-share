from typing import Optional, Dict, Any, List
import httpx
import logging

from app.core.config import settings

logger = logging.getLogger(__name__)


class TelegramService:
    """Telegram Bot integration service"""
    
    def __init__(self):
        self.bot_token = settings.TELEGRAM_BOT_TOKEN
        self.api_url = f"https://api.telegram.org/bot{self.bot_token}"
    
    async def send_message(
        self,
        chat_id: int,
        text: str,
        parse_mode: str = "HTML",
        disable_notification: bool = False
    ) -> bool:
        """Send message via Telegram bot"""
        
        if not self.bot_token or self.bot_token == "YOUR_TELEGRAM_BOT_TOKEN_HERE":
            logger.warning("Telegram bot token not configured")
            return False
        
        url = f"{self.api_url}/sendMessage"
        
        payload = {
            "chat_id": chat_id,
            "text": text,
            "parse_mode": parse_mode,
            "disable_notification": disable_notification,
        }
        
        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(url, json=payload, timeout=30.0)
                
                if response.status_code == 200:
                    logger.info(f"Message sent to {chat_id}")
                    return True
                else:
                    logger.error(f"Telegram API error: {response.status_code} - {response.text}")
                    return False
        
        except Exception as e:
            logger.error(f"Failed to send Telegram message: {e}")
            return False
    
    async def send_photo(
        self,
        chat_id: int,
        photo_url: str,
        caption: Optional[str] = None
    ) -> bool:
        """Send photo via Telegram bot"""
        
        url = f"{self.api_url}/sendPhoto"
        
        payload = {
            "chat_id": chat_id,
            "photo": photo_url,
        }
        
        if caption:
            payload["caption"] = caption
        
        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(url, json=payload, timeout=30.0)
                return response.status_code == 200
        
        except Exception as e:
            logger.error(f"Failed to send Telegram photo: {e}")
            return False
    
    async def send_document(
        self,
        chat_id: int,
        document_url: str,
        caption: Optional[str] = None
    ) -> bool:
        """Send document via Telegram bot"""
        
        url = f"{self.api_url}/sendDocument"
        
        payload = {
            "chat_id": chat_id,
            "document": document_url,
        }
        
        if caption:
            payload["caption"] = caption
        
        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(url, json=payload, timeout=30.0)
                return response.status_code == 200
        
        except Exception as e:
            logger.error(f"Failed to send Telegram document: {e}")
            return False
    
    async def notify_admin_new_user(
        self,
        telegram_id: int,
        username: str,
        first_name: str
    ):
        """Notify admin about new user registration"""
        
        admin_ids = settings.admin_ids_list
        if not admin_ids:
            return
        
        message = f"""
?? <b>Yangi foydalanuvchi!</b>

?? Ism: {first_name}
?? Username: @{username or 'N/A'}
?? Telegram ID: {telegram_id}
?? Sana: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
"""
        
        for admin_id in admin_ids:
            await self.send_message(admin_id, message)
    
    async def notify_admin_support_request(
        self,
        ticket_id: int,
        telegram_id: int,
        username: str,
        subject: str,
        message: str,
        attachment_url: Optional[str] = None
    ):
        """Notify admin about new support request"""
        
        admin_ids = settings.admin_ids_list
        if not admin_ids:
            return
        
        notification = f"""
?? <b>Yangi support xabari</b>

?? Ticket ID: #{ticket_id}
?? Foydalanuvchi: @{username or 'N/A'}
?? Telegram ID: {telegram_id}
?? Mavzu: {subject}

?? Xabar:
{message}
"""
        
        for admin_id in admin_ids:
            if attachment_url:
                await self.send_photo(admin_id, attachment_url, notification)
            else:
                await self.send_message(admin_id, notification)
    
    async def notify_admin_withdraw_request(
        self,
        withdraw_id: int,
        telegram_id: int,
        username: str,
        amount_usd: float,
        wallet_address: str
    ):
        """Notify admin about new withdraw request"""
        
        admin_ids = settings.admin_ids_list
        if not admin_ids:
            return
        
        message = f"""
?? <b>Yangi yechish so'rovi</b>

?? Request ID: #{withdraw_id}
?? Foydalanuvchi: @{username or 'N/A'} ({telegram_id})
?? Summa: ${amount_usd:.2f}
?? Wallet: <code>{wallet_address}</code>
?? Network: BEP20
?? Sana: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

<i>Avtomatik processing boshlanadi...</i>
"""
        
        for admin_id in admin_ids:
            await self.send_message(admin_id, message)
    
    async def notify_admin_system_alert(
        self,
        alert_type: str,
        message: str,
        severity: str = "warning"
    ):
        """Send system alert to admins"""
        
        admin_ids = settings.admin_ids_list
        if not admin_ids:
            return
        
        emoji = {
            "info": "??",
            "warning": "??",
            "error": "?",
            "critical": "??"
        }.get(severity, "??")
        
        notification = f"""
{emoji} <b>Tizim xabari</b>

?? Turi: {alert_type}
?? Xabar: {message}
? Vaqt: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
"""
        
        for admin_id in admin_ids:
            await self.send_message(admin_id, notification)
    
    async def notify_user_welcome(self, telegram_id: int, first_name: str):
        """Send welcome message to new user"""
        
        message = f"""
?? Xush kelibsiz, {first_name}!

Siz Traffic Sharing Platform ga muvaffaqiyatli ro'yxatdan o'tdingiz.

?? Dashboard sahifasida trafik ulashishni boshlashingiz mumkin.
?? Daromadingiz avtomatik balansga tushadi.
?? Minimal yechish summasi: $1.39

Savollaringiz bo'lsa, Qo'llab-quvvatlash bo'limiga murojaat qiling.

Omad! ??
"""
        
        await self.send_message(telegram_id, message)
    
    async def notify_user_balance_updated(
        self,
        telegram_id: int,
        amount: float,
        new_balance: float
    ):
        """Notify user about balance update"""
        
        message = f"""
?? <b>Balans yangilandi!</b>

? Qo'shildi: ${amount:.2f}
?? Yangi balans: ${new_balance:.2f}

Tabriklaymiz! ??
"""
        
        await self.send_message(telegram_id, message)
    
    async def notify_user_withdraw_completed(
        self,
        telegram_id: int,
        amount_usd: float,
        tx_hash: str
    ):
        """Notify user about completed withdrawal"""
        
        message = f"""
? <b>To'lov muvaffaqiyatli yakunlandi!</b>

?? Summa: ${amount_usd:.2f} USDT
?? Network: BEP20
?? TX Hash: <code>{tx_hash}</code>

Hamyoningizni tekshiring!
"""
        
        await self.send_message(telegram_id, message)
    
    async def notify_user_session_started(
        self,
        telegram_id: int,
        session_id: str
    ):
        """Notify user about session start"""
        
        message = f"""
?? <b>Sessiya boshlandi!</b>

?? Session ID: {session_id[:8]}...
? Vaqt: {datetime.now().strftime('%H:%M:%S')}

Trafik ulashish faol. Dashboard'da kuzatishingiz mumkin.
"""
        
        await self.send_message(telegram_id, message)
    
    async def notify_user_session_completed(
        self,
        telegram_id: int,
        duration: str,
        mb_sent: float,
        earned: float
    ):
        """Notify user about completed session"""
        
        message = f"""
? <b>Sessiya tugallandi!</b>

? Davomiyligi: {duration}
?? Yuborilgan: {mb_sent:.0f} MB
?? Daromad: ${earned:.3f}

Balansga qo'shildi. Rahmat! ??
"""
        
        await self.send_message(telegram_id, message)


from datetime import datetime
