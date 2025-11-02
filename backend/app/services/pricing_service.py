from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from datetime import date, datetime, timedelta
from typing import Dict, Any, List, Optional
import logging

from app.models.pricing import DailyPrice, TrafficLog
from app.models.user import User
from app.core.config import settings

logger = logging.getLogger(__name__)


class PricingService:
    """
    REAL pricing management service
    Handles daily price setting and history
    """
    
    def __init__(self, db: AsyncSession):
        self.db = db
    
    async def get_current_price(self) -> Dict[str, Any]:
        """
        REAL get current price from database
        """
        # Try today's price first
        result = await self.db.execute(
            select(DailyPrice)
            .where(DailyPrice.date == date.today())
            .order_by(DailyPrice.created_at.desc())
            .limit(1)
        )
        price = result.scalar_one_or_none()
        
        # Fallback to latest price
        if not price:
            result = await self.db.execute(
                select(DailyPrice)
                .order_by(DailyPrice.date.desc())
                .limit(1)
            )
            price = result.scalar_one_or_none()
        
        # Default if no price in DB
        if not price:
            return {
                "date": date.today().isoformat(),
                "price_per_gb": settings.DEFAULT_PRICE_PER_GB,
                "price_per_mb": settings.DEFAULT_PRICE_PER_GB / 1024,
                "message": "Default pricing",
                "change": 0.0
            }
        
        # Get yesterday's price for comparison
        yesterday = date.today() - timedelta(days=1)
        yesterday_result = await self.db.execute(
            select(DailyPrice)
            .where(DailyPrice.date == yesterday)
            .limit(1)
        )
        yesterday_price = yesterday_result.scalar_one_or_none()
        
        change = 0.0
        if yesterday_price:
            change = price.price_per_gb - yesterday_price.price_per_gb
        
        return {
            "date": price.date.isoformat(),
            "price_per_gb": float(price.price_per_gb),
            "price_per_mb": float(price.price_per_mb),
            "message": price.message or "",
            "change": float(change)
        }
    
    async def set_daily_price(
        self,
        admin_id: int,
        price_per_gb: float,
        message: Optional[str] = None,
        target_date: Optional[date] = None
    ) -> Dict[str, Any]:
        """
        REAL set daily price (admin only)
        """
        if target_date is None:
            target_date = date.today()
        
        # Validate price
        if price_per_gb < 0.10 or price_per_gb > 10.00:
            raise ValueError("Price must be between $0.10 and $10.00 per GB")
        
        price_per_mb = price_per_gb / 1024
        
        # Check if price already exists for date
        result = await self.db.execute(
            select(DailyPrice)
            .where(DailyPrice.date == target_date)
        )
        existing_price = result.scalar_one_or_none()
        
        if existing_price:
            # Update existing
            old_price = existing_price.price_per_gb
            existing_price.price_per_gb = price_per_gb
            existing_price.price_per_mb = price_per_mb
            existing_price.message = message
            existing_price.admin_id = admin_id
            
            logger.info(
                f"Price updated for {target_date}: "
                f"${old_price:.2f} -> ${price_per_gb:.2f}"
            )
        else:
            # Create new
            new_price = DailyPrice(
                date=target_date,
                price_per_gb=price_per_gb,
                price_per_mb=price_per_mb,
                message=message,
                admin_id=admin_id,
                created_at=datetime.utcnow()
            )
            self.db.add(new_price)
            
            logger.info(f"New price set for {target_date}: ${price_per_gb:.2f}/GB")
        
        await self.db.commit()
        
        # Trigger notification if today's price
        if target_date == date.today():
            try:
                from app.services.notification_service import NotificationService
                notif_service = NotificationService(self.db)
                await notif_service.send_daily_price_notification(
                    price_per_gb=price_per_gb,
                    message=message or f"Bugungi narx: ${price_per_gb:.2f}/GB"
                )
            except Exception as e:
                logger.error(f"Failed to send price notification: {e}")
        
        return {
            "date": target_date.isoformat(),
            "price_per_gb": float(price_per_gb),
            "price_per_mb": float(price_per_mb),
            "message": message,
            "set_by_admin": admin_id
        }
    
    async def get_price_history(
        self,
        days: int = 30
    ) -> List[Dict[str, Any]]:
        """
        REAL price history from database
        """
        start_date = date.today() - timedelta(days=days)
        
        result = await self.db.execute(
            select(DailyPrice)
            .where(DailyPrice.date >= start_date)
            .order_by(DailyPrice.date.desc())
        )
        prices = result.scalars().all()
        
        return [
            {
                "date": p.date.isoformat(),
                "price_per_gb": float(p.price_per_gb),
                "price_per_mb": float(p.price_per_mb),
                "message": p.message,
                "created_at": p.created_at.isoformat()
            }
            for p in prices
        ]
    
    async def calculate_earnings(
        self,
        mb_amount: float,
        price_date: Optional[date] = None
    ) -> float:
        """
        REAL earnings calculation based on price
        """
        if price_date is None:
            price_date = date.today()
        
        # Get price for date
        result = await self.db.execute(
            select(DailyPrice)
            .where(DailyPrice.date == price_date)
        )
        price = result.scalar_one_or_none()
        
        if price:
            price_per_mb = price.price_per_mb
        else:
            price_per_mb = settings.DEFAULT_PRICE_PER_GB / 1024
        
        earnings = mb_amount * price_per_mb
        
        return round(earnings, 6)
