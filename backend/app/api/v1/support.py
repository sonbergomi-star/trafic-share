from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.api.v1.dependencies import get_current_user
from app.models.support import SupportRequest, SupportStatus
from app.core.config import settings
import requests

router = APIRouter()


class SupportMessageRequest(BaseModel):
    subject: str
    message: str
    attachment_url: str = None


@router.post("/send")
async def send_support(
    request: SupportMessageRequest,
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Send support request"""
    # Rate limiting check (can be enhanced with Redis)
    
    support_req = SupportRequest(
        telegram_id=current_user.telegram_id,
        subject=request.subject,
        message=request.message,
        attachment_url=request.attachment_url,
        status=SupportStatus.NEW
    )
    
    db.add(support_req)
    db.commit()
    db.refresh(support_req)
    
    # Send to Telegram admin bot
    if settings.TELEGRAM_BOT_TOKEN:
        try:
            message_text = f"""?? Yangi support xabari:
?? Foydalanuvchi: @{current_user.username or 'N/A'}
?? ID: {current_user.telegram_id}
?? Mavzu: {request.subject}
?? Matn: {request.message}"""
            
            admin_ids = settings.ADMIN_IDS.split(",") if settings.ADMIN_IDS else []
            for admin_id in admin_ids:
                url = f"https://api.telegram.org/bot{settings.TELEGRAM_BOT_TOKEN}/sendMessage"
                requests.post(url, json={
                    "chat_id": int(admin_id.strip()),
                    "text": message_text
                })
        except Exception as e:
            print(f"Telegram notification error: {e}")
    
    return {
        "status": "success",
        "message": "Xabaringiz yuborildi! Admin tez orada siz bilan bog'lanadi.",
        "request_id": support_req.id
    }


@router.get("/history")
async def get_support_history(
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get support request history"""
    requests = db.query(SupportRequest).filter(
        SupportRequest.telegram_id == current_user.telegram_id
    ).order_by(SupportRequest.created_at.desc()).limit(20).all()
    
    return [
        {
            "id": req.id,
            "subject": req.subject,
            "message": req.message,
            "status": req.status.value,
            "created_at": req.created_at.isoformat() if req.created_at else None,
        }
        for req in requests
    ]
