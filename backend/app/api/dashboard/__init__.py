from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
import logging

from app.core.database import get_db
from app.middleware.auth import get_current_user
from app.models.user import User
from app.services.dashboard_service import DashboardService

logger = logging.getLogger(__name__)

router = APIRouter()


@router.get("/")
async def get_dashboard(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    REAL dashboard data from database
    """
    dashboard_service = DashboardService(db)
    
    try:
        data = await dashboard_service.get_dashboard_data(current_user.telegram_id)
        
        return {
            "status": "success",
            "data": data
        }
    
    except Exception as e:
        logger.error(f"Dashboard error: {e}")
        raise HTTPException(status_code=500, detail="Failed to load dashboard")


@router.post("/refresh")
async def refresh_dashboard(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    REAL refresh dashboard with balance recalculation
    """
    dashboard_service = DashboardService(db)
    
    try:
        # Refresh balance
        balance_result = await dashboard_service.refresh_balance(current_user.telegram_id)
        
        # Get updated dashboard
        data = await dashboard_service.get_dashboard_data(current_user.telegram_id)
        
        logger.info(f"Dashboard refreshed for user {current_user.telegram_id}")
        
        return {
            "status": "success",
            "data": data,
            "balance_delta": balance_result.get('delta', 0)
        }
    
    except Exception as e:
        logger.error(f"Dashboard refresh error: {e}")
        raise HTTPException(status_code=500, detail="Failed to refresh dashboard")
