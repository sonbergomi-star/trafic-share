from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api.deps import require_admin
from app.db.session import get_db
from app.schemas.pricing import DailyPriceAdminPayload, DailyPriceResponse
from app.services.pricing_service import PricingService


router = APIRouter(prefix="/api", tags=["pricing"])


@router.get("/daily_price", response_model=DailyPriceResponse)
def get_daily_price(db: Session = Depends(get_db)):
    return PricingService.get_daily_price(db)


@router.post("/admin/daily_price", response_model=DailyPriceResponse)
def set_daily_price(
    payload: DailyPriceAdminPayload,
    admin=Depends(require_admin),
    db: Session = Depends(get_db),
):
    try:
        return PricingService.set_daily_price(payload, db)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc

