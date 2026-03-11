"""Celery tasks for VotoClaro."""

from celery import Celery

from app.config import settings

celery_app = Celery(
    "votoclaro",
    broker=settings.REDIS_URL,
    backend=settings.REDIS_URL,
)

celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="America/Lima",
    enable_utc=True,
    task_track_started=True,
    task_default_queue="votoclaro",
)

# Auto-discover tasks in this package
celery_app.autodiscover_tasks(["app.tasks"])
