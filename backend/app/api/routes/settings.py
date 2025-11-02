"""User settings endpoints."""

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user, get_db_session
from app.schemas import SettingsResponse, SettingsUpdateRequest
from app.services.settings_service import SettingsService


router = APIRouter()


@router.get("/user/settings", response_model=SettingsResponse)
async def get_settings(
    session: AsyncSession = Depends(get_db_session),
    current_user=Depends(get_current_user),
):
    service = SettingsService(session)
    settings_obj = await service.get_settings(current_user)
    return SettingsResponse(
        language=settings_obj.language,
        push_notifications=settings_obj.push_notifications,
        session_updates=settings_obj.session_updates,
        system_updates=settings_obj.system_updates,
        two_factor_enabled=settings_obj.two_factor_enabled,
        single_device_mode=settings_obj.single_device_mode,
        battery_saver=settings_obj.battery_saver,
        theme=settings_obj.theme,
    )


@router.patch("/user/settings", response_model=SettingsResponse)
async def update_settings(
    payload: SettingsUpdateRequest,
    session: AsyncSession = Depends(get_db_session),
    current_user=Depends(get_current_user),
):
    service = SettingsService(session)
    settings_obj = await service.update_settings(current_user, payload)
    return SettingsResponse(
        language=settings_obj.language,
        push_notifications=settings_obj.push_notifications,
        session_updates=settings_obj.session_updates,
        system_updates=settings_obj.system_updates,
        two_factor_enabled=settings_obj.two_factor_enabled,
        single_device_mode=settings_obj.single_device_mode,
        battery_saver=settings_obj.battery_saver,
        theme=settings_obj.theme,
    )
