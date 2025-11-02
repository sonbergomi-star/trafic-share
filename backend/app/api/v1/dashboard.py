from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.api.v1.dependencies import get_current_user
from app.services.dashboard_service import get_dashboard_data

router = APIRouter()


@router.get("/{telegram_id}")
async def get_dashboard(
    telegram_id: int,
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get dashboard data for user"""
    if current_user.telegram_id != telegram_id:
        # Check if admin
        from app.services.user_service import is_admin
        if not is_admin(current_user.telegram_id):
            raise HTTPException(status_code=403, detail="Access denied")
    
    return get_dashboard_data(db, telegram_id)
