from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from datetime import datetime, date
from typing import Optional
import logging

from app.core.database import get_db
from app.middleware.auth import verify_admin
from app.models.user import User
from app.services.admin_service import AdminService
from app.services.pricing_service import PricingService

logger = logging.getLogger(__name__)

router = APIRouter()


@router.get("/dashboard")
async def admin_dashboard(
    admin: User = Depends(verify_admin),
    db: AsyncSession = Depends(get_db)
):
    """
    REAL admin dashboard with live statistics
    """
    admin_service = AdminService(db)
    
    try:
        stats = await admin_service.get_dashboard_stats()
        
        return {
            "status": "success",
            "data": stats
        }
    
    except Exception as e:
        logger.error(f"Admin dashboard error: {e}")
        raise HTTPException(status_code=500, detail="Failed to load admin dashboard")


@router.post("/price/set")
async def set_daily_price(
    price_per_gb: float,
    message: Optional[str] = None,
    send_notification: bool = True,
    admin: User = Depends(verify_admin),
    db: AsyncSession = Depends(get_db)
):
    """
    REAL set daily price (admin only)
    """
    pricing_service = PricingService(db)
    
    try:
        result = await pricing_service.set_daily_price(
            admin_id=admin.telegram_id,
            price_per_gb=price_per_gb,
            message=message
        )
        
        logger.info(
            f"Admin {admin.telegram_id} set price: ${price_per_gb:.2f}/GB"
        )
        
        return {
            "status": "success",
            "data": result
        }
    
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Set price error: {e}")
        raise HTTPException(status_code=500, detail="Failed to set price")


@router.get("/price/history")
async def get_price_history(
    days: int = 30,
    admin: User = Depends(verify_admin),
    db: AsyncSession = Depends(get_db)
):
    """
    REAL price history (admin only)
    """
    pricing_service = PricingService(db)
    
    try:
        history = await pricing_service.get_price_history(days=days)
        
        return {
            "status": "success",
            "data": {
                "history": history,
                "days": days
            }
        }
    
    except Exception as e:
        logger.error(f"Price history error: {e}")
        raise HTTPException(status_code=500, detail="Failed to get price history")


@router.post("/broadcast")
async def broadcast_notification(
    title: str,
    body: str,
    admin: User = Depends(verify_admin),
    db: AsyncSession = Depends(get_db)
):
    """
    REAL broadcast notification to all users (admin only)
    """
    from app.services.notification_service import NotificationService
    
    notif_service = NotificationService(db)
    
    try:
        result = await notif_service.send_to_all_active_users(
            title=title,
            body=body,
            notif_type="system_update"
        )
        
        logger.info(
            f"Admin {admin.telegram_id} broadcast notification: "
            f"sent={result['sent']}, failed={result['failed']}"
        )
        
        return {
            "status": "success",
            "data": result
        }
    
    except Exception as e:
        logger.error(f"Broadcast error: {e}")
        raise HTTPException(status_code=500, detail="Failed to broadcast")


@router.post("/reconcile")
async def run_reconciliation(
    admin: User = Depends(verify_admin),
    db: AsyncSession = Depends(get_db)
):
    """
    REAL run full reconciliation (admin only)
    """
    from app.services.reconciliation_service import ReconciliationService
    
    reconciliation_service = ReconciliationService(db)
    
    try:
        result = await reconciliation_service.run_full_reconciliation()
        
        logger.info(f"Admin {admin.telegram_id} triggered reconciliation")
        
        return {
            "status": "success",
            "data": result
        }
    
    except Exception as e:
        logger.error(f"Reconciliation error: {e}")
        raise HTTPException(status_code=500, detail="Reconciliation failed")
