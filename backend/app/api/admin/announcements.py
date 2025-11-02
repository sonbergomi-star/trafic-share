from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional
from datetime import datetime

from app.core.database import get_db
from app.middleware.auth import verify_admin
from app.models.user import User
from app.services.admin_service import AdminService

router = APIRouter(prefix="/admin/announcements", tags=["Admin - Announcements"])


@router.post("/create")
async def create_announcement(
    title: str,
    description: str,
    image_url: Optional[str] = None,
    link: Optional[str] = None,
    send_push: bool = False,
    admin: User = Depends(verify_admin),
    db: AsyncSession = Depends(get_db)
):
    """
    Create new announcement (Admin only)
    """
    admin_service = AdminService(db)
    result = await admin_service.create_announcement(
        admin_id=admin.telegram_id,
        title=title,
        description=description,
        image_url=image_url,
        link=link,
        send_push=send_push
    )
    
    return {
        "status": "success",
        "data": result
    }


@router.post("/promo/create")
async def create_promo_code(
    code: str,
    bonus_percent: float,
    description: Optional[str] = None,
    expires_at: Optional[datetime] = None,
    max_uses: Optional[int] = None,
    admin: User = Depends(verify_admin),
    db: AsyncSession = Depends(get_db)
):
    """
    Create new promo code (Admin only)
    """
    admin_service = AdminService(db)
    result = await admin_service.create_promo_code(
        admin_id=admin.telegram_id,
        code=code,
        bonus_percent=bonus_percent,
        description=description,
        expires_at=expires_at,
        max_uses=max_uses
    )
    
    return {
        "status": "success",
        "data": result
    }
