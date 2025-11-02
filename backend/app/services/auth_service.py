from datetime import datetime, timezone

from sqlalchemy.orm import Session

from app.core.security import create_access_token, verify_telegram_signature
from app.db.models.user import User
from app.schemas.auth import TelegramAuthPayload


class AuthService:
    @staticmethod
    def authenticate(data: TelegramAuthPayload, db: Session) -> User:
        payload = data.model_dump()
        if not verify_telegram_signature(payload):
            raise ValueError("Invalid Telegram signature")

        telegram_id = data.id
        user = db.query(User).filter(User.telegram_id == telegram_id).one_or_none()

        auth_dt = datetime.fromtimestamp(data.auth_date, tz=timezone.utc)
        if user:
            user.username = data.username or user.username
            user.first_name = data.first_name or user.first_name
            user.photo_url = data.photo_url or user.photo_url
            user.auth_date = auth_dt
        else:
            user = User(
                telegram_id=telegram_id,
                username=data.username,
                first_name=data.first_name,
                photo_url=data.photo_url,
                auth_date=auth_dt,
            )
            db.add(user)

        db.commit()
        db.refresh(user)
        return user

    @staticmethod
    def issue_token(user: User) -> str:
        payload = {"telegram_id": user.telegram_id, "username": user.username, "role": user.role}
        token = create_access_token(payload)
        return token

