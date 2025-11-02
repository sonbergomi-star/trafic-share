from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.services.daily_price_service import get_today_price, get_latest_price

router = APIRouter()


@router.get("/daily_price")
async def get_daily_price(db: Session = Depends(get_db)):
    """Get today's price"""
    price = get_today_price(db) or get_latest_price(db)
    
    if not price:
        return {
            "date": None,
            "price_per_gb": 1.50,  # Default
            "message": "No price set yet"
        }
    
    return {
        "date": price.date.isoformat(),
        "price_per_gb": float(price.price_per_gb),
        "message": price.message or f"Bugungi narx: ${price.price_per_gb}/GB"
    }
