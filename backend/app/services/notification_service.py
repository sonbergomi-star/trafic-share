from datetime import datetime

import httpx
from sqlalchemy.orm import Session

from app.core.config import get_settings
from app.db.models.notifications import DeviceRegistry, NotificationLog
from app.schemas.notifications import (
    DeviceRegisterPayload,
    NotificationDispatchResult,
    PushNotificationPayload,
)


settings = get_settings()


class NotificationService:
    fcm_endpoint = "https://fcm.googleapis.com/fcm/send"

    @staticmethod
    def register_device(payload: DeviceRegisterPayload, user_id: int, db: Session) -> DeviceRegistry:
        record = (
            db.query(DeviceRegistry)
            .filter(DeviceRegistry.telegram_id == payload.telegram_id, DeviceRegistry.device_id == payload.device_id)
            .one_or_none()
        )
        if record:
            record.device_token = payload.device_token
            record.platform = payload.platform
            record.notifications_enabled = payload.notifications_enabled
            record.last_seen = datetime.utcnow()
            record.updated_at = datetime.utcnow()
        else:
            record = DeviceRegistry(
                user_id=user_id,
                telegram_id=payload.telegram_id,
                device_id=payload.device_id,
                platform=payload.platform,
                device_token=payload.device_token,
                notifications_enabled=payload.notifications_enabled,
                last_seen=datetime.utcnow(),
            )
            db.add(record)

        db.commit()
        db.refresh(record)
        return record

    @classmethod
    def send_push(cls, payload: PushNotificationPayload, db: Session) -> NotificationDispatchResult:
        if not settings.fcm_server_key:
            return NotificationDispatchResult(sent=0, failed=0)

        devices = db.query(DeviceRegistry).filter(DeviceRegistry.notifications_enabled.is_(True)).all()
        sent = 0
        failed = 0

        headers = {
            "Authorization": f"key={settings.fcm_server_key}",
            "Content-Type": "application/json",
        }

        for device in devices:
            body = {
                "to": device.device_token,
                "notification": {
                    "title": payload.title,
                    "body": payload.body,
                },
                "data": {"type": payload.type, **(payload.data or {})},
            }

            try:
                response = httpx.post(cls.fcm_endpoint, headers=headers, json=body, timeout=10.0)
                success = response.status_code == 200
            except Exception as exc:  # pragma: no cover - network issues
                success = False
                response = None
                error_message = str(exc)
            else:
                error_message = None if success else response.text

            if success:
                sent += 1
            else:
                failed += 1

            log = NotificationLog(
                telegram_id=device.telegram_id,
                device_id=device.device_id,
                notif_type=payload.type,
                title=payload.title,
                body=payload.body,
                payload=payload.data or {},
                delivered=success,
                opened=False,
                error=error_message,
            )
            db.add(log)

        db.commit()
        return NotificationDispatchResult(sent=sent, failed=failed)

