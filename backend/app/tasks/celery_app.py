from celery import Celery
from celery.schedules import crontab
from app.core.config import settings

# Create Celery app
celery_app = Celery(
    "traffic_platform",
    broker=settings.redis_url,
    backend=settings.redis_url,
    include=[
        "app.tasks.periodic_tasks",
        "app.tasks.notification_tasks",
        "app.tasks.payment_tasks",
    ]
)

# Celery configuration
celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
    task_track_started=True,
    task_time_limit=30 * 60,  # 30 minutes
    task_soft_time_limit=25 * 60,  # 25 minutes
    worker_prefetch_multiplier=4,
    worker_max_tasks_per_child=1000,
)

# Periodic tasks schedule
celery_app.conf.beat_schedule = {
    # Close orphaned sessions every 5 minutes
    "close-orphaned-sessions": {
        "task": "app.tasks.periodic_tasks.close_orphaned_sessions",
        "schedule": 300.0,  # 5 minutes
    },
    # Reconcile daily stats at midnight
    "reconcile-daily-stats": {
        "task": "app.tasks.periodic_tasks.reconcile_daily_stats",
        "schedule": crontab(hour=0, minute=5),  # 00:05 daily
    },
    # Reconcile weekly stats on Monday
    "reconcile-weekly-stats": {
        "task": "app.tasks.periodic_tasks.reconcile_weekly_stats",
        "schedule": crontab(hour=1, minute=0, day_of_week=1),  # Monday 01:00
    },
    # Reconcile monthly stats on 1st of month
    "reconcile-monthly-stats": {
        "task": "app.tasks.periodic_tasks.reconcile_monthly_stats",
        "schedule": crontab(hour=2, minute=0, day_of_month=1),  # 1st day 02:00
    },
    # Send daily price notifications at 9 AM
    "send-daily-price-notifications": {
        "task": "app.tasks.periodic_tasks.send_daily_price_notifications",
        "schedule": crontab(hour=9, minute=0),  # 09:00 daily
    },
    # Cleanup old data weekly
    "cleanup-old-data": {
        "task": "app.tasks.periodic_tasks.cleanup_old_data",
        "schedule": crontab(hour=3, minute=0, day_of_week=0),  # Sunday 03:00
    },
    # Process pending withdrawals every hour
    "process-pending-withdrawals": {
        "task": "app.tasks.payment_tasks.process_pending_withdrawals",
        "schedule": crontab(minute=0),  # Every hour
    },
    # Send session summaries every 6 hours
    "send-session-summaries": {
        "task": "app.tasks.notification_tasks.send_session_summaries",
        "schedule": 21600.0,  # 6 hours
    },
}

if __name__ == "__main__":
    celery_app.start()
