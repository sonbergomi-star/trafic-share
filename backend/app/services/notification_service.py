"""Notification delivery service."""

from typing import Iterable

import firebase_admin
from firebase_admin import credentials, messaging
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.models import DeviceRegistry, NotificationLog, User
from app.schemas.notifications import PushSendRequest


class NotificationService:
    """Sending FCM and logging notifications."""

    _firebase_initialized = False

    def __init__(self, session: AsyncSession) -> None:
        self.session = session
        if settings.fcm_credentials_path and not NotificationService._firebase_initialized:
            cred = credentials.Certificate(settings.fcm_credentials_path)
            firebase_admin.initialize_app(cred, {"projectId": settings.fcm_project_id})
            NotificationService._firebase_initialized = True

    async def register_device(
        self,
        user: User,
        device_id: str,
        device_token: str,
        platform: str,
        notifications_enabled: bool,
    ) -> DeviceRegistry:
        stmt = select(DeviceRegistry).where(DeviceRegistry.device_id == device_id)
        existing = (await self.session.execute(stmt)).scalar_one_or_none()
        if existing:
            existing.device_token = device_token
            existing.notifications_enabled = notifications_enabled
            existing.platform = platform
            await self.session.commit()
            return existing

        registry = DeviceRegistry(
            user_id=user.id,
            device_id=device_id,
            device_token=device_token,
            platform=platform,
            notifications_enabled=notifications_enabled,
        )
        self.session.add(registry)
        await self.session.commit()
        return registry

    async def send_push_to_all(self, payload: PushSendRequest) -> dict:
        stmt = select(DeviceRegistry).where(DeviceRegistry.notifications_enabled.is_(True))
        devices = (await self.session.execute(stmt)).scalars().all()

        sent, failed = 0, 0
        for batch in self._chunk(devices, 500):
            message = messaging.MulticastMessage(
                tokens=[device.device_token for device in batch],
                notification=messaging.Notification(title=payload.title, body=payload.body),
                data={"type": payload.type, **(payload.data or {})},
            )
            if NotificationService._firebase_initialized:
                response = messaging.send_multicast(message)
                sent += response.success_count
                failed += response.failure_count
            else:
                sent += len(batch)

            for device in batch:
                log = NotificationLog(
                    user_id=device.user_id,
                    device_id=device.device_id,
                    notif_type=payload.type,
                    title=payload.title,
                    body=payload.body,
                    payload=payload.data or {},
                    delivered=True,
                )
                self.session.add(log)

        await self.session.commit()
        return {"sent": sent, "failed": failed}

    def _chunk(self, iterable: Iterable[DeviceRegistry], size: int) -> Iterable[list[DeviceRegistry]]:
        batch: list[DeviceRegistry] = []
        for item in iterable:
            batch.append(item)
            if len(batch) == size:
                yield batch
                batch = []
        if batch:
            yield batch
