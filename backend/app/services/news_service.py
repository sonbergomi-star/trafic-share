from sqlalchemy.orm import Session

from app.db.models.content import Announcement, PromoCode
from app.schemas.news import NewsPromoResponse, PromoActivatePayload, PromoActivateResponse


class NewsService:
    @staticmethod
    def get_news_and_promo(db: Session) -> NewsPromoResponse:
        announcements = db.query(Announcement).order_by(Announcement.created_at.desc()).limit(10).all()
        promo = db.query(PromoCode).filter(PromoCode.is_active.is_(True)).order_by(PromoCode.created_at.desc()).all()
        telegram_links = {
            "channel": "https://t.me/project_news",
            "chat": "https://t.me/project_chat",
        }
        return NewsPromoResponse(telegram_links=telegram_links, announcements=announcements, promo=promo)

    @staticmethod
    def activate_promo(payload: PromoActivatePayload, db: Session) -> PromoActivateResponse:
        promo = db.query(PromoCode).filter(PromoCode.code == payload.code, PromoCode.is_active.is_(True)).one_or_none()
        if not promo:
            raise ValueError("Promo code invalid or expired")
        return PromoActivateResponse(status="success", message="Promo code activated")

