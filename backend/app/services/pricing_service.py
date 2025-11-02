from datetime import date, datetime
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import Dict, Any, Optional

from app.models.pricing import DailyPrice, PricingLog


class PricingService:
    """Pricing management service"""
    
    def __init__(self, db: AsyncSession):
        self.db = db
    
    async def get_current_price(self) -> Dict[str, Any]:
        """Get current daily price"""
        today = date.today()
        
        result = await self.db.execute(
            select(DailyPrice).where(DailyPrice.date == today)
        )
        daily_price = result.scalar_one_or_none()
        
        if not daily_price:
            # Return default price if not set
            return {
                "date": today.isoformat(),
                "price_per_gb": 1.50,
                "price_per_mb": 0.0015,
                "message": "Default pricing (not set for today)"
            }
        
        return {
            "date": daily_price.date.isoformat(),
            "price_per_gb": daily_price.price_per_gb,
            "price_per_mb": daily_price.price_per_mb,
            "message": daily_price.message,
        }
    
    async def set_daily_price(
        self,
        price_per_gb: float,
        message: Optional[str] = None,
        target_date: Optional[date] = None
    ) -> Dict[str, Any]:
        """Set daily price (admin only)"""
        
        if target_date is None:
            target_date = date.today()
        
        # Calculate price per MB
        price_per_mb = price_per_gb / 1024
        
        # Check if price exists for date
        result = await self.db.execute(
            select(DailyPrice).where(DailyPrice.date == target_date)
        )
        daily_price = result.scalar_one_or_none()
        
        if daily_price:
            # Update existing
            old_price = daily_price.price_per_gb
            daily_price.price_per_gb = price_per_gb
            daily_price.price_per_mb = price_per_mb
            daily_price.message = message
            change = price_per_gb - old_price
        else:
            # Create new
            daily_price = DailyPrice(
                date=target_date,
                price_per_gb=price_per_gb,
                price_per_mb=price_per_mb,
                message=message
            )
            self.db.add(daily_price)
            change = None
        
        # Log price change
        log = PricingLog(
            date=target_date,
            price_per_mb=price_per_mb,
            price_per_gb=price_per_gb,
            source="admin"
        )
        self.db.add(log)
        
        await self.db.commit()
        await self.db.refresh(daily_price)
        
        return {
            "status": "success",
            "date": target_date.isoformat(),
            "price_per_gb": price_per_gb,
            "price_per_mb": price_per_mb,
            "message": message,
            "change": change
        }
    
    async def get_price_history(self, days: int = 30) -> list:
        """Get pricing history"""
        
        from_date = date.today() - timedelta(days=days)
        
        result = await self.db.execute(
            select(DailyPrice)
            .where(DailyPrice.date >= from_date)
            .order_by(DailyPrice.date.desc())
        )
        prices = result.scalars().all()
        
        return [
            {
                "date": p.date.isoformat(),
                "price_per_gb": p.price_per_gb,
                "price_per_mb": p.price_per_mb,
                "message": p.message,
            }
            for p in prices
        ]


from datetime import timedelta
