"""Notification Celery tasks."""

import asyncio

from app.core.celery_app import celery_app
from app.db.session import async_session_factory
from app.schemas.notifications import PushSendRequest
from app.services.notification_service import NotificationService


@celery_app.task(name="app.tasks.notifications.broadcast")
def broadcast_notification_task(payload: dict) -> dict:
    async def _run() -> dict:
        async with async_session_factory() as session:
            service = NotificationService(session)
            return await service.send_push_to_all(PushSendRequest(**payload))

    return asyncio.run(_run())
