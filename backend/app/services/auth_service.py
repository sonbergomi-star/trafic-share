"""Authentication service."""

from datetime import datetime, timezone

from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import create_access_token, create_refresh_token
from app.models import LoginHistory, User, UserRole
from app.schemas.auth import TelegramAuthRequest
from app.utils.telegram import verify_telegram_auth


class AuthService:
    """Handles Telegram authentication flow."""

    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def authenticate_telegram(
        self, payload: TelegramAuthRequest, client_ip: str | None
    ) -> tuple[User, str, str]:
        """Authenticate or register a user using Telegram payload."""

        data_dict = payload.model_dump()
        if not verify_telegram_auth(data_dict):
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="invalid_signature")

        stmt = select(User).where(User.telegram_id == payload.id)
        result = await self.session.execute(stmt)
        user = result.scalar_one_or_none()

        auth_datetime = datetime.fromtimestamp(payload.auth_date, tz=timezone.utc)
        if user is None:
            user = User(
                telegram_id=payload.id,
                username=payload.username,
                first_name=payload.first_name or payload.username,
                photo_url=payload.photo_url,
                auth_date=auth_datetime,
                role=UserRole.USER,
                last_login_ip=client_ip,
            )
            self.session.add(user)
        else:
            user.username = payload.username or user.username
            user.first_name = payload.first_name or user.first_name
            user.photo_url = payload.photo_url or user.photo_url
            user.auth_date = auth_datetime
            user.last_login_ip = client_ip

        user.last_login_device = "Android"  # refined on client header

        await self.session.flush()

        login_entry = LoginHistory(
            user_id=user.id,
            city=None,
            device=user.last_login_device,
            ip_address=client_ip,
        )
        self.session.add(login_entry)

        access_token = create_access_token(
            subject=str(user.id),
            additional_claims={
                "telegram_id": user.telegram_id,
                "username": user.username,
                "role": user.role.value,
            },
        )
        refresh_token = create_refresh_token(subject=str(user.id))
        user.jwt_token = access_token

        await self.session.commit()
        await self.session.refresh(user)

        return user, access_token, refresh_token
