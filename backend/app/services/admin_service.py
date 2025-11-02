from datetime import datetime, date, timedelta
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, update, delete, and_, or_
from typing import Dict, Any, List, Optional
import logging

from app.models.user import User
from app.models.session import Session
from app.models.transaction import Transaction, WithdrawRequest
from app.models.support import SupportRequest
from app.models.announcement import Announcement, PromoCode
from app.models.pricing import DailyPrice
from app.core.config import settings
from app.services.notification_service import NotificationService
from app.services.telegram_service import TelegramService

logger = logging.getLogger(__name__)


class AdminService:
    """Admin panel service with full management capabilities"""
    
    def __init__(self, db: AsyncSession):
        self.db = db
        self.notification_service = NotificationService(db)
        self.telegram_service = TelegramService()
    
    def check_admin(self, telegram_id: int) -> bool:
        """Check if user is admin"""
        return telegram_id in settings.admin_ids_list
    
    # USER MANAGEMENT
    
    async def get_all_users(
        self,
        page: int = 1,
        per_page: int = 50,
        search: Optional[str] = None,
        status_filter: Optional[str] = None
    ) -> Dict[str, Any]:
        """Get all users with pagination and filters"""
        
        query = select(User)
        
        # Apply filters
        if search:
            query = query.where(
                or_(
                    User.username.ilike(f"%{search}%"),
                    User.first_name.ilike(f"%{search}%"),
                    User.telegram_id == int(search) if search.isdigit() else False
                )
            )
        
        if status_filter == "active":
            query = query.where(User.is_active == True)
        elif status_filter == "banned":
            query = query.where(User.is_banned == True)
        
        # Get total count
        count_result = await self.db.execute(
            select(func.count()).select_from(query.subquery())
        )
        total = count_result.scalar()
        
        # Get paginated results
        offset = (page - 1) * per_page
        query = query.offset(offset).limit(per_page).order_by(User.created_at.desc())
        
        result = await self.db.execute(query)
        users = result.scalars().all()
        
        return {
            "users": [
                {
                    "id": u.id,
                    "telegram_id": u.telegram_id,
                    "username": u.username,
                    "first_name": u.first_name,
                    "balance_usd": u.balance_usd,
                    "sent_mb": u.sent_mb,
                    "used_mb": u.used_mb,
                    "is_active": u.is_active,
                    "is_banned": u.is_banned,
                    "created_at": u.created_at.isoformat(),
                    "last_seen": u.last_seen.isoformat() if u.last_seen else None,
                }
                for u in users
            ],
            "pagination": {
                "page": page,
                "per_page": per_page,
                "total": total,
                "total_pages": (total + per_page - 1) // per_page,
            }
        }
    
    async def ban_user(
        self,
        telegram_id: int,
        reason: Optional[str] = None
    ) -> Dict[str, Any]:
        """Ban a user"""
        
        result = await self.db.execute(
            select(User).where(User.telegram_id == telegram_id)
        )
        user = result.scalar_one_or_none()
        
        if not user:
            raise ValueError("User not found")
        
        user.is_banned = True
        user.is_active = False
        
        # Close all active sessions
        await self.db.execute(
            update(Session)
            .where(Session.telegram_id == telegram_id)
            .where(Session.is_active == True)
            .values(is_active=False, status='cancelled')
        )
        
        await self.db.commit()
        
        # Notify user
        await self.telegram_service.send_message(
            chat_id=telegram_id,
            text=f"?? Hisobingiz bloklandi. Sabab: {reason or 'Tizim qoidalarini buzish'}"
        )
        
        return {
            "status": "success",
            "message": f"User {telegram_id} banned",
            "reason": reason
        }
    
    async def unban_user(self, telegram_id: int) -> Dict[str, Any]:
        """Unban a user"""
        
        result = await self.db.execute(
            select(User).where(User.telegram_id == telegram_id)
        )
        user = result.scalar_one_or_none()
        
        if not user:
            raise ValueError("User not found")
        
        user.is_banned = False
        user.is_active = True
        await self.db.commit()
        
        # Notify user
        await self.telegram_service.send_message(
            chat_id=telegram_id,
            text="? Hisobingiz qayta faollashtirildi. Xush kelibsiz!"
        )
        
        return {
            "status": "success",
            "message": f"User {telegram_id} unbanned"
        }
    
    async def adjust_user_balance(
        self,
        telegram_id: int,
        amount: float,
        reason: str,
        admin_id: int
    ) -> Dict[str, Any]:
        """Manually adjust user balance"""
        
        result = await self.db.execute(
            select(User).where(User.telegram_id == telegram_id)
        )
        user = result.scalar_one_or_none()
        
        if not user:
            raise ValueError("User not found")
        
        old_balance = user.balance_usd
        user.balance_usd += amount
        new_balance = user.balance_usd
        
        # Create transaction record
        transaction = Transaction(
            telegram_id=telegram_id,
            type='refund' if amount > 0 else 'penalty',
            amount_usd=amount,
            status='completed',
            description=f"Admin adjustment: {reason}",
            note=f"Adjusted by admin {admin_id}"
        )
        self.db.add(transaction)
        
        await self.db.commit()
        
        # Notify user
        await self.telegram_service.notify_user_balance_updated(
            telegram_id=telegram_id,
            amount=amount,
            new_balance=new_balance
        )
        
        logger.info(
            f"Admin {admin_id} adjusted balance for user {telegram_id}: "
            f"{old_balance} -> {new_balance} (delta: {amount})"
        )
        
        return {
            "status": "success",
            "old_balance": old_balance,
            "new_balance": new_balance,
            "delta": amount,
        }
    
    # WITHDRAW MANAGEMENT
    
    async def get_pending_withdrawals(self) -> List[Dict]:
        """Get all pending withdrawal requests"""
        
        result = await self.db.execute(
            select(WithdrawRequest)
            .where(WithdrawRequest.status.in_(['pending', 'processing']))
            .order_by(WithdrawRequest.created_at)
        )
        withdrawals = result.scalars().all()
        
        return [
            {
                "id": w.id,
                "telegram_id": w.telegram_id,
                "amount_usd": w.amount_usd,
                "amount_usdt": w.amount_usdt,
                "wallet_address": w.wallet_address,
                "status": w.status,
                "created_at": w.created_at.isoformat(),
                "payout_id": w.payout_id,
            }
            for w in withdrawals
        ]
    
    async def approve_withdrawal(
        self,
        withdraw_id: int,
        admin_id: int
    ) -> Dict[str, Any]:
        """Manually approve a withdrawal"""
        
        result = await self.db.execute(
            select(WithdrawRequest).where(WithdrawRequest.id == withdraw_id)
        )
        withdrawal = result.scalar_one_or_none()
        
        if not withdrawal:
            raise ValueError("Withdrawal not found")
        
        withdrawal.status = 'processing'
        withdrawal.admin_note = f"Approved by admin {admin_id}"
        await self.db.commit()
        
        # TODO: Trigger payment processing
        
        logger.info(f"Admin {admin_id} approved withdrawal {withdraw_id}")
        
        return {
            "status": "success",
            "message": "Withdrawal approved and queued for processing"
        }
    
    async def reject_withdrawal(
        self,
        withdraw_id: int,
        admin_id: int,
        reason: str
    ) -> Dict[str, Any]:
        """Reject a withdrawal and refund balance"""
        
        result = await self.db.execute(
            select(WithdrawRequest).where(WithdrawRequest.id == withdraw_id)
        )
        withdrawal = result.scalar_one_or_none()
        
        if not withdrawal:
            raise ValueError("Withdrawal not found")
        
        # Refund balance if reserved
        if withdrawal.reserved_balance:
            user_result = await self.db.execute(
                select(User).where(User.telegram_id == withdrawal.telegram_id)
            )
            user = user_result.scalar_one_or_none()
            
            if user:
                user.balance_usd += withdrawal.amount_usd
        
        withdrawal.status = 'cancelled'
        withdrawal.admin_note = f"Rejected by admin {admin_id}: {reason}"
        
        await self.db.commit()
        
        # Notify user
        await self.telegram_service.send_message(
            chat_id=withdrawal.telegram_id,
            text=f"? Yechish so'rovingiz rad etildi.\n\nSabab: {reason}\n\nBalans qaytarildi."
        )
        
        logger.info(f"Admin {admin_id} rejected withdrawal {withdraw_id}")
        
        return {
            "status": "success",
            "message": "Withdrawal rejected and balance refunded"
        }
    
    # SUPPORT MANAGEMENT
    
    async def get_support_requests(
        self,
        status_filter: Optional[str] = None
    ) -> List[Dict]:
        """Get support requests"""
        
        query = select(SupportRequest)
        
        if status_filter:
            query = query.where(SupportRequest.status == status_filter)
        
        result = await self.db.execute(
            query.order_by(SupportRequest.created_at.desc()).limit(100)
        )
        requests = result.scalars().all()
        
        return [
            {
                "id": r.id,
                "telegram_id": r.telegram_id,
                "subject": r.subject,
                "message": r.message,
                "status": r.status,
                "attachment_url": r.attachment_url,
                "admin_reply": r.admin_reply,
                "created_at": r.created_at.isoformat(),
                "replied_at": r.replied_at.isoformat() if r.replied_at else None,
            }
            for r in requests
        ]
    
    async def reply_to_support(
        self,
        request_id: int,
        admin_id: int,
        reply_message: str
    ) -> Dict[str, Any]:
        """Reply to support request"""
        
        result = await self.db.execute(
            select(SupportRequest).where(SupportRequest.id == request_id)
        )
        support_request = result.scalar_one_or_none()
        
        if not support_request:
            raise ValueError("Support request not found")
        
        support_request.admin_reply = reply_message
        support_request.admin_id = admin_id
        support_request.status = 'replied'
        support_request.replied_at = datetime.utcnow()
        
        await self.db.commit()
        
        # Notify user
        await self.telegram_service.send_message(
            chat_id=support_request.telegram_id,
            text=f"""
?? <b>Support javob olindi!</b>

?? Mavzu: {support_request.subject}

?? Admin javobi:
{reply_message}

Agar yana savolingiz bo'lsa, yangi xabar yuboring.
"""
        )
        
        logger.info(f"Admin {admin_id} replied to support request {request_id}")
        
        return {
            "status": "success",
            "message": "Reply sent to user"
        }
    
    # ANNOUNCEMENT MANAGEMENT
    
    async def create_announcement(
        self,
        admin_id: int,
        title: str,
        description: str,
        image_url: Optional[str] = None,
        link: Optional[str] = None,
        send_push: bool = False
    ) -> Dict[str, Any]:
        """Create new announcement"""
        
        announcement = Announcement(
            title=title,
            description=description,
            image_url=image_url,
            link=link,
            is_active=True,
        )
        
        self.db.add(announcement)
        await self.db.commit()
        await self.db.refresh(announcement)
        
        # Send push notification if requested
        if send_push:
            await self.notification_service.send_to_all_active_users(
                title=f"?? {title}",
                body=description[:100],
                notif_type="system_update",
                data={"announcement_id": announcement.id}
            )
        
        logger.info(f"Admin {admin_id} created announcement: {title}")
        
        return {
            "status": "success",
            "announcement_id": announcement.id,
            "push_sent": send_push
        }
    
    async def create_promo_code(
        self,
        admin_id: int,
        code: str,
        bonus_percent: float,
        description: Optional[str] = None,
        expires_at: Optional[datetime] = None,
        max_uses: Optional[int] = None
    ) -> Dict[str, Any]:
        """Create new promo code"""
        
        # Check if code already exists
        existing = await self.db.execute(
            select(PromoCode).where(PromoCode.code == code.upper())
        )
        if existing.scalar_one_or_none():
            raise ValueError("Promo code already exists")
        
        promo = PromoCode(
            code=code.upper(),
            bonus_percent=bonus_percent,
            description=description,
            expires_at=expires_at,
            max_uses=max_uses,
            is_active=True,
        )
        
        self.db.add(promo)
        await self.db.commit()
        await self.db.refresh(promo)
        
        logger.info(f"Admin {admin_id} created promo code: {code}")
        
        return {
            "status": "success",
            "promo_id": promo.id,
            "code": promo.code
        }
    
    # STATISTICS & REPORTS
    
    async def get_dashboard_stats(self) -> Dict[str, Any]:
        """Get admin dashboard statistics"""
        
        # Total users
        total_users = await self.db.execute(select(func.count(User.id)))
        
        # Active users (last 24 hours)
        day_ago = datetime.utcnow() - timedelta(hours=24)
        active_users = await self.db.execute(
            select(func.count(User.id)).where(User.last_seen >= day_ago)
        )
        
        # Total balance
        total_balance = await self.db.execute(select(func.sum(User.balance_usd)))
        
        # Active sessions
        active_sessions = await self.db.execute(
            select(func.count(Session.id)).where(Session.is_active == True)
        )
        
        # Today's earnings
        today_start = datetime.combine(date.today(), datetime.min.time())
        today_earnings = await self.db.execute(
            select(func.sum(Session.earned_usd))
            .where(Session.start_time >= today_start)
        )
        
        # Pending withdrawals
        pending_withdrawals = await self.db.execute(
            select(
                func.count(WithdrawRequest.id),
                func.sum(WithdrawRequest.amount_usd)
            )
            .where(WithdrawRequest.status.in_(['pending', 'processing']))
        )
        pending_data = pending_withdrawals.one()
        
        # Pending support requests
        pending_support = await self.db.execute(
            select(func.count(SupportRequest.id))
            .where(SupportRequest.status.in_(['new', 'read']))
        )
        
        return {
            "users": {
                "total": total_users.scalar(),
                "active_24h": active_users.scalar(),
            },
            "balance": {
                "total_usd": float(total_balance.scalar() or 0),
            },
            "sessions": {
                "active_now": active_sessions.scalar(),
            },
            "earnings": {
                "today_usd": float(today_earnings.scalar() or 0),
            },
            "withdrawals": {
                "pending_count": pending_data[0] or 0,
                "pending_amount_usd": float(pending_data[1] or 0),
            },
            "support": {
                "pending_count": pending_support.scalar(),
            },
            "timestamp": datetime.utcnow().isoformat(),
        }
    
    async def export_users_csv(self) -> str:
        """Export users data to CSV format"""
        
        result = await self.db.execute(select(User).order_by(User.created_at.desc()))
        users = result.scalars().all()
        
        # Create CSV content
        csv_lines = [
            "Telegram ID,Username,First Name,Balance USD,Sent MB,Used MB,Is Active,Is Banned,Created At"
        ]
        
        for user in users:
            line = f"{user.telegram_id},{user.username or ''},{user.first_name or ''},"
            line += f"{user.balance_usd},{user.sent_mb},{user.used_mb},"
            line += f"{user.is_active},{user.is_banned},{user.created_at.isoformat()}"
            csv_lines.append(line)
        
        return "\n".join(csv_lines)
    
    async def export_sessions_csv(
        self,
        start_date: Optional[date] = None,
        end_date: Optional[date] = None
    ) -> str:
        """Export sessions data to CSV format"""
        
        query = select(Session).order_by(Session.created_at.desc())
        
        if start_date:
            query = query.where(func.date(Session.start_time) >= start_date)
        if end_date:
            query = query.where(func.date(Session.start_time) <= end_date)
        
        result = await self.db.execute(query.limit(10000))
        sessions = result.scalars().all()
        
        # Create CSV content
        csv_lines = [
            "Session ID,Telegram ID,Start Time,End Time,Duration,Sent MB,Earned USD,Status,IP,Location"
        ]
        
        for session in sessions:
            line = f"{session.session_id},{session.telegram_id},"
            line += f"{session.start_time.isoformat() if session.start_time else ''},"
            line += f"{session.end_time.isoformat() if session.end_time else ''},"
            line += f"{session.duration or ''},{session.sent_mb},{session.earned_usd},"
            line += f"{session.status},{session.ip_address or ''},{session.location or ''}"
            csv_lines.append(line)
        
        return "\n".join(csv_lines)
    
    async def get_system_health(self) -> Dict[str, Any]:
        """Get system health metrics"""
        
        # Database connection pool
        # Active sessions
        active_sessions = await self.db.execute(
            select(func.count(Session.id)).where(Session.is_active == True)
        )
        
        # Recent errors (if you have error logging)
        # For now, return basic health
        
        return {
            "status": "healthy",
            "database": "connected",
            "active_sessions": active_sessions.scalar(),
            "timestamp": datetime.utcnow().isoformat(),
        }
