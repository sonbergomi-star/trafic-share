from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.db.session import get_db
from app.schemas.dashboard import DashboardResponse
from app.services.dashboard_service import DashboardService


router = APIRouter(prefix="/api/dashboard", tags=["dashboard"])


@router.get("/{telegram_id}", response_model=DashboardResponse)
def get_dashboard(
    telegram_id: int,
    current_user=Depends(get_current_user),
    db: Session = Depends(get_db),
):
    if current_user.telegram_id != telegram_id and current_user.role != "admin":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Forbidden")

    return DashboardService.get_dashboard(telegram_id, db)

