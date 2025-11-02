from sqlalchemy.orm import Session
from datetime import date
from app.models.daily_price import DailyPrice
from typing import Optional


def get_today_price(db: Session) -> Optional[DailyPrice]:
    """Get today's price"""
    today = date.today()
    return db.query(DailyPrice).filter(DailyPrice.date == today).first()


def get_latest_price(db: Session) -> Optional[DailyPrice]:
    """Get latest price"""
    return db.query(DailyPrice).order_by(DailyPrice.date.desc()).first()


def create_or_update_price(db: Session, date_val: date, price_per_gb: float, message: str = None) -> DailyPrice:
    """Create or update daily price"""
    price = db.query(DailyPrice).filter(DailyPrice.date == date_val).first()
    
    if price:
        price.price_per_gb = price_per_gb
        if message:
            price.message = message
    else:
        price = DailyPrice(
            date=date_val,
            price_per_gb=price_per_gb,
            message=message
        )
        db.add(price)
    
    db.commit()
    db.refresh(price)
    return price
