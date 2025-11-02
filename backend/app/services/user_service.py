from datetime import datetime

from sqlalchemy.orm import Session

from app.core.security import create_access_token, mask_token
from app.db.models.user import User
from app.schemas.user import SettingsPayload, SettingsResponse, TokenRenewResponse


class UserService:
    @staticmethod
    def get_by_telegram_id(telegram_id: int, db: Session) -> User:
        user = db.query(User).filter(User.telegram_id == telegram_id).one_or_none()
        if not user:
            raise ValueError("User not found")
        return user

    @staticmethod
    def update_settings(user: User, payload: SettingsPayload, db: Session) -> SettingsResponse:
        if payload.language is not None:
            user.language = payload.language
        if payload.push_notifications is not None:
            user.notifications_enabled = payload.push_notifications
        if payload.session_updates is not None:
            user.session_notifications_enabled = payload.session_updates
        if payload.system_updates is not None:
            user.system_notifications_enabled = payload.system_updates
        if payload.single_device_mode is not None:
            user.single_device_mode = payload.single_device_mode
        if payload.battery_saver is not None:
            user.battery_saver = payload.battery_saver
        if payload.theme is not None:
            user.theme = payload.theme

        user.updated_at = datetime.utcnow()
        db.commit()
        db.refresh(user)

        return SettingsResponse(
            language=user.language,
            push_notifications=user.notifications_enabled,
            session_updates=user.session_notifications_enabled,
            system_updates=user.system_notifications_enabled,
            single_device_mode=user.single_device_mode,
            battery_saver=user.battery_saver,
            theme=user.theme,
            two_factor_enabled=user.two_factor_enabled,
            updated_at=user.updated_at,
        )

    @staticmethod
    def renew_token(user: User, db: Session) -> TokenRenewResponse:
        token = create_access_token({"telegram_id": user.telegram_id, "username": user.username, "role": user.role})
        user.jwt_token = token
        user.updated_at = datetime.utcnow()
        db.commit()
        return TokenRenewResponse(message="Token successfully renewed", jwt_token=token, masked_token=mask_token(token))

    @staticmethod
    def logout(user: User, db: Session) -> None:
        user.jwt_token = None
        user.updated_at = datetime.utcnow()
        db.commit()

    @staticmethod
    def logout_all(user: User, db: Session) -> None:
        user.jwt_token = None
        user.single_device_mode = True
        user.updated_at = datetime.utcnow()
        db.commit()

