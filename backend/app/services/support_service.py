from sqlalchemy.orm import Session

from app.db.models.support import SupportRequest
from app.schemas.support import SupportHistoryResponse, SupportRequestPayload


class SupportService:
    @staticmethod
    def create_request(user_id: int, telegram_id: int, payload: SupportRequestPayload, db: Session) -> SupportRequest:
        record = SupportRequest(
            user_id=user_id,
            telegram_id=telegram_id,
            subject=payload.subject,
            message=payload.message,
            attachment_url=payload.attachment_url,
            status="new",
        )
        db.add(record)
        db.commit()
        db.refresh(record)
        return record

    @staticmethod
    def history(telegram_id: int, db: Session) -> SupportHistoryResponse:
        items = (
            db.query(SupportRequest)
            .filter(SupportRequest.telegram_id == telegram_id)
            .order_by(SupportRequest.created_at.desc())
            .all()
        )
        return SupportHistoryResponse(items=items)

