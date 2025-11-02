"""User settings service."""

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import User, UserSettings
from app.schemas.settings import SettingsUpdateRequest


class SettingsService:
    """Provides settings retrieval and update operations."""

    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def get_settings(self, user: User) -> UserSettings:
        stmt = select(UserSettings).where(UserSettings.user_id == user.id)
        settings_obj = (await self.session.execute(stmt)).scalar_one_or_none()
        if settings_obj is None:
            settings_obj = UserSettings(user_id=user.id)
            self.session.add(settings_obj)
            await self.session.commit()
        return settings_obj

    async def update_settings(self, user: User, payload: SettingsUpdateRequest) -> UserSettings:
        settings_obj = await self.get_settings(user)
        update_data = payload.model_dump(exclude_none=True)
        for key, value in update_data.items():
            setattr(settings_obj, key, value)
        await self.session.commit()
        await self.session.refresh(settings_obj)
        return settings_obj
