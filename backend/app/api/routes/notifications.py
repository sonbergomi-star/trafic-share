"""Notification endpoints."""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user, get_db_session
from app.schemas import DeviceRegistrationRequest, PushSendRequest, PushSendResponse
from app.services.notification_service import NotificationService


router = APIRouter()


@router.post("/register_device")
async def register_device(
    payload: DeviceRegistrationRequest,
    session: AsyncSession = Depends(get_db_session),
    current_user=Depends(get_current_user),
):
    if current_user.telegram_id != payload.telegram_id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="forbidden")
    service = NotificationService(session)
    registry = await service.register_device(
        current_user,
        device_id=payload.device_id,
        device_token=payload.device_token,
        platform=payload.platform,
        notifications_enabled=payload.notifications_enabled,
    )
    return {"status": "success", "device_id": registry.device_id}


@router.post("/push/send", response_model=PushSendResponse)
async def send_push(
    payload: PushSendRequest,
    session: AsyncSession = Depends(get_db_session),
    current_user=Depends(get_current_user),
):
    if current_user.role.value != "admin":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="forbidden")
    service = NotificationService(session)
    return await service.send_push_to_all(payload)
