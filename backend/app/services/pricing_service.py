from datetime import date

from sqlalchemy.orm import Session

from app.core.config import get_settings
from app.db.models.pricing import DailyPrice
from app.schemas.pricing import DailyPriceAdminPayload, DailyPriceResponse


settings = get_settings()


class PricingService:
    @staticmethod
    def get_daily_price(db: Session) -> DailyPriceResponse:
        record = db.query(DailyPrice).order_by(DailyPrice.date.desc()).first()
        if not record:
            return DailyPriceResponse(date=date.today(), price_per_gb=settings.default_price_per_gb, message=None, change=None)
        return DailyPriceResponse.model_validate(record)

    @staticmethod
    def set_daily_price(payload: DailyPriceAdminPayload, db: Session) -> DailyPriceResponse:
        target_date = payload.date or date.today()
        record = db.query(DailyPrice).filter(DailyPrice.date == target_date).one_or_none()

        previous = db.query(DailyPrice).order_by(DailyPrice.date.desc()).first()
        change = None
        if previous and previous.price_per_gb:
            change = round(payload.price_per_gb - previous.price_per_gb, 2)

        if record:
            record.price_per_gb = payload.price_per_gb
            record.message = payload.message
            record.change_delta = change
        else:
            record = DailyPrice(
                date=target_date,
                price_per_gb=payload.price_per_gb,
                message=payload.message,
                change_delta=change,
            )
            db.add(record)

        db.commit()
        db.refresh(record)
        return DailyPriceResponse.model_validate(record)

    @staticmethod
    def compute_earnings_mb(used_mb: float, db: Session) -> float:
        price = db.query(DailyPrice).order_by(DailyPrice.date.desc()).first()
        price_per_gb = price.price_per_gb if price else settings.default_price_per_gb
        earnings = (used_mb / 1024) * price_per_gb
        return round(earnings, 6)

