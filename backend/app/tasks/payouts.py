"""Payout worker tasks."""

from app.core.celery_app import celery_app


@celery_app.task(name="app.tasks.payouts.process")
def process_withdraw_task(withdraw_id: int) -> dict:
    # Placeholder: integrate with payout provider
    return {"withdraw_id": withdraw_id, "status": "queued"}
