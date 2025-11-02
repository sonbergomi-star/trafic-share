"""Celery application configuration."""

from celery import Celery

from app.core.config import settings


celery_app = Celery(
    "traffic_platform",
    broker=settings.celery_broker_url,
    backend=settings.celery_result_backend,
)

celery_app.conf.update(
    task_routes={
        "app.tasks.notifications.*": {"queue": "notifications"},
        "app.tasks.pricing.*": {"queue": "pricing"},
        "app.tasks.payouts.*": {"queue": "payouts"},
        "app.tasks.telemetry.*": {"queue": "telemetry"},
    },
    task_default_queue="default",
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
)


def autodiscover() -> None:
    """Register task modules."""

    celery_app.autodiscover_tasks([
        "app.tasks.notifications",
        "app.tasks.pricing",
        "app.tasks.payouts",
        "app.tasks.telemetry",
    ])


autodiscover()
