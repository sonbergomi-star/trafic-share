from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, desc
from pydantic import BaseModel, Field
from datetime import datetime
import logging

from app.core.database import get_db
from app.middleware.auth import get_current_user
from app.models.user import User
from app.models.support import SupportRequest

logger = logging.getLogger(__name__)

router = APIRouter()


class CreateSupportRequest(BaseModel):
    subject: str = Field(..., min_length=5, max_length=200)
    message: str = Field(..., min_length=10, max_length=2000)
    attachment_url: str | None = None


@router.post("/create")
async def create_support_request(
    request: CreateSupportRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    REAL create support request
    """
    # Check rate limit (max 5 per hour)
    from datetime import timedelta
    hour_ago = datetime.utcnow() - timedelta(hours=1)
    
    count_result = await db.execute(
        select(func.count(SupportRequest.id))
        .where(SupportRequest.telegram_id == current_user.telegram_id)
        .where(SupportRequest.created_at >= hour_ago)
    )
    recent_count = count_result.scalar()
    
    if recent_count >= 5:
        raise HTTPException(
            status_code=429,
            detail="Rate limit exceeded. Maximum 5 support requests per hour."
        )
    
    # Create support request
    support_request = SupportRequest(
        telegram_id=current_user.telegram_id,
        subject=request.subject,
        message=request.message,
        attachment_url=request.attachment_url,
        status='new',
        created_at=datetime.utcnow()
    )
    
    db.add(support_request)
    await db.commit()
    await db.refresh(support_request)
    
    logger.info(
        f"Support request created: ID={support_request.id} "
        f"by user {current_user.telegram_id}"
    )
    
    # Notify admins (async task)
    try:
        from app.services.telegram_service import TelegramService
        telegram_service = TelegramService()
        await telegram_service.notify_admin_support_request(
            ticket_id=support_request.id,
            telegram_id=current_user.telegram_id,
            username=current_user.username,
            subject=request.subject,
            message=request.message,
            attachment_url=request.attachment_url
        )
    except Exception as e:
        logger.error(f"Failed to notify admins: {e}")
    
    return {
        "status": "success",
        "data": {
            "ticket_id": support_request.id,
            "subject": support_request.subject,
            "status": support_request.status,
            "created_at": support_request.created_at.isoformat(),
        }
    }


@router.get("/history")
async def get_support_history(
    page: int = Query(1, ge=1),
    per_page: int = Query(20, ge=1, le=100),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    REAL support request history
    """
    # Get total count
    count_result = await db.execute(
        select(func.count(SupportRequest.id))
        .where(SupportRequest.telegram_id == current_user.telegram_id)
    )
    total = count_result.scalar()
    
    # Get requests
    offset = (page - 1) * per_page
    result = await db.execute(
        select(SupportRequest)
        .where(SupportRequest.telegram_id == current_user.telegram_id)
        .order_by(desc(SupportRequest.created_at))
        .offset(offset)
        .limit(per_page)
    )
    requests = result.scalars().all()
    
    return {
        "status": "success",
        "data": {
            "requests": [
                {
                    "id": r.id,
                    "subject": r.subject,
                    "message": r.message,
                    "status": r.status,
                    "attachment_url": r.attachment_url,
                    "admin_reply": r.admin_reply,
                    "created_at": r.created_at.isoformat(),
                    "replied_at": r.replied_at.isoformat() if r.replied_at else None,
                }
                for r in requests
            ],
            "pagination": {
                "page": page,
                "per_page": per_page,
                "total": total,
                "total_pages": (total + per_page - 1) // per_page,
            }
        }
    }


@router.get("/{ticket_id}")
async def get_support_request(
    ticket_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    REAL get single support request
    """
    result = await db.execute(
        select(SupportRequest)
        .where(SupportRequest.id == ticket_id)
        .where(SupportRequest.telegram_id == current_user.telegram_id)
    )
    request = result.scalar_one_or_none()
    
    if not request:
        raise HTTPException(status_code=404, detail="Support request not found")
    
    # Mark as read if new
    if request.status == 'new':
        request.status = 'read'
        await db.commit()
    
    return {
        "status": "success",
        "data": {
            "id": request.id,
            "subject": request.subject,
            "message": request.message,
            "status": request.status,
            "attachment_url": request.attachment_url,
            "admin_reply": request.admin_reply,
            "created_at": request.created_at.isoformat(),
            "replied_at": request.replied_at.isoformat() if request.replied_at else None,
        }
    }
