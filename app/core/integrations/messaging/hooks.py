from fastapi import FastAPI
import logging
from .broker import rabbit_router

logger = logging.getLogger("app.faststream.hooks")

@rabbit_router.after_startup
async def setup_queues(app: FastAPI):
    """
    Создает необходимые очереди в RabbitMQ после запуска приложения
    """
    logger.info("Настройка очередей RabbitMQ для отправки email")

    # Объявляем все необходимые очереди
    queues = [
        "email_queue",
        "verification_email_queue",
        "password_reset_email_queue",
        "registration_success_email_queue"
    ]

    for queue_name in queues:
        try:
            # В FastStream мы можем объявить очередь через broker
            await rabbit_router.broker.declare_queue(queue_name)
            logger.info(f"Очередь {queue_name} успешно создана/проверена")
        except Exception as e:
            logger.error(f"Ошибка при создании очереди {queue_name}: {str(e)}")
