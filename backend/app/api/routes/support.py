from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.db.session import get_db
from app.schemas.support import SupportHistoryResponse, SupportRequestPayload, SupportRequestSchema
from app.services.support_service import SupportService


router = APIRouter(prefix="/api/support", tags=["support"])


@router.post("/send", response_model=SupportRequestSchema)
def send_support(payload: SupportRequestPayload, current_user=Depends(get_current_user), db: Session = Depends(get_db)):
    if payload.telegram_id != current_user.telegram_id and current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Forbidden")
    record = SupportService.create_request(current_user.id, payload.telegram_id, payload, db)
    return SupportRequestSchema.model_validate(record)


@router.get("/history", response_model=SupportHistoryResponse)
def support_history(current_user=Depends(get_current_user), db: Session = Depends(get_db)):
    return SupportService.history(current_user.telegram_id, db)

