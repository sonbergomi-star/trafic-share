from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.db.session import get_db
from app.schemas.news import NewsPromoResponse, PromoActivatePayload, PromoActivateResponse
from app.services.news_service import NewsService


router = APIRouter(prefix="/api", tags=["news"])


@router.get("/news_promo", response_model=NewsPromoResponse)
def news_promo(db: Session = Depends(get_db)):
    return NewsService.get_news_and_promo(db)


@router.post("/promo/activate", response_model=PromoActivateResponse)
def activate_promo(
    payload: PromoActivatePayload,
    current_user=Depends(get_current_user),
    db: Session = Depends(get_db),
):
    if payload.user_id != current_user.id and current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Forbidden")
    try:
        return NewsService.activate_promo(payload, db)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc

