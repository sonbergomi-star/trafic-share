"""Telemetry aggregation tasks."""

from app.core.celery_app import celery_app


@celery_app.task(name="app.tasks.telemetry.aggregate")
def aggregate_telemetry_task() -> dict:
    # Placeholder for telemetry aggregation logic
    return {"status": "ok"}
