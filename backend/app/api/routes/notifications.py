from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.api.deps import get_current_user, require_admin
from app.db.session import get_db
from app.schemas.notifications import (
    DeviceRegisterPayload,
    DeviceRegistrySchema,
    NotificationDispatchResult,
    PushNotificationPayload,
)
from app.services.notification_service import NotificationService


router = APIRouter(prefix="/api", tags=["notifications"])


@router.post("/register_device", response_model=DeviceRegistrySchema)
def register_device(
    payload: DeviceRegisterPayload,
    current_user=Depends(get_current_user),
    db: Session = Depends(get_db),
):
    if payload.telegram_id != current_user.telegram_id and current_user.role != "admin":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Forbidden")
    record = NotificationService.register_device(payload, current_user.id, db)
    return DeviceRegistrySchema.model_validate(record)


@router.post("/push/send", response_model=NotificationDispatchResult)
def send_push(
    payload: PushNotificationPayload,
    admin=Depends(require_admin),
    db: Session = Depends(get_db),
):
    result = NotificationService.send_push(payload, db)
    return result

