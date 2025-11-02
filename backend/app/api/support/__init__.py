from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, desc
from pydantic import BaseModel

from app.core.database import get_db
from app.models.support import SupportRequest
from app.models.user import User


router = APIRouter()


class CreateSupportRequest(BaseModel):
    telegram_id: int
    subject: str
    message: str
    attachment_url: str | None = None


@router.post("/send")
async def create_support_request(request: CreateSupportRequest, db: AsyncSession = Depends(get_db)):
    """
    Create a new support request
    """
    # Get user
    user_result = await db.execute(
        select(User).where(User.telegram_id == request.telegram_id)
    )
    user = user_result.scalar_one_or_none()
    
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Create support request
    support = SupportRequest(
        user_id=user.id,
        telegram_id=request.telegram_id,
        subject=request.subject,
        message=request.message,
        attachment_url=request.attachment_url,
        status="new",
    )
    
    db.add(support)
    await db.commit()
    await db.refresh(support)
    
    # TODO: Send notification to admin via Telegram
    
    return {
        "status": "success",
        "message": "Your support request has been sent. Admin will contact you soon.",
        "ticket_id": support.id,
    }


@router.get("/history/{telegram_id}")
async def get_support_history(telegram_id: int, db: AsyncSession = Depends(get_db)):
    """
    Get support request history
    """
    result = await db.execute(
        select(SupportRequest)
        .where(SupportRequest.telegram_id == telegram_id)
        .order_by(desc(SupportRequest.created_at))
        .limit(10)
    )
    requests = result.scalars().all()
    
    return {
        "requests": [
            {
                "id": r.id,
                "subject": r.subject,
                "message": r.message,
                "status": r.status,
                "admin_reply": r.admin_reply,
                "created_at": r.created_at.isoformat(),
                "replied_at": r.replied_at.isoformat() if r.replied_at else None,
            }
            for r in requests
        ]
    }
