from celery import Celery
from app.core.settings import settings

# Создаем экземпляр Celery
celery_app = Celery(
    "equiply",
    broker=settings.rabbitmq_url,
    backend=settings.redis_url,
)

# Настраиваем Celery
celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="Europe/Moscow",
    enable_utc=True,
    task_track_started=True,
    task_time_limit=30 * 60,  # 30 минут
    worker_prefetch_multiplier=1,
    worker_concurrency=4,
)

# Автоматически обнаруживаем и регистрируем задачи
celery_app.autodiscover_tasks(["app.core.integrations.worker.tasks.mail"])
