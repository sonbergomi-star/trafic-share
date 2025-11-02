from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.db.session import get_db
from app.schemas.session import SessionListResponse, SessionSummary
from app.services.session_service import SessionService


router = APIRouter(prefix="/api/sessions", tags=["sessions"])


@router.get("", response_model=SessionListResponse)
def list_sessions(limit: int = 20, offset: int = 0, current_user=Depends(get_current_user), db: Session = Depends(get_db)):
    return SessionService.list_sessions(current_user.telegram_id, limit, offset, db)


@router.get("/summary", response_model=SessionSummary)
def sessions_summary(current_user=Depends(get_current_user), db: Session = Depends(get_db)):
    return SessionService.summary(current_user.telegram_id, db)

