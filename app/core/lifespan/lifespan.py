"""
Модуль жизненного цикла приложения.

Этот модуль содержит функцию жизненного цикла приложения,
которая инициализирует и закрывает сервисы при запуске и остановке приложения.
"""
import asyncio
from contextlib import asynccontextmanager
from fastapi import FastAPI

from dishka.integrations.fastapi import setup_dishka
from app.core.dependencies.container import container
from app.core.lifespan.state import AppState

@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Управляет жизненным циклом приложения.

    Инициализирует:
    - Логгер
    - Redis подключение
    - RabbitMQ подключение
    - Планировщик задач

    При завершении корректно закрывает все соединения.

    Args:
        app: Экземпляр FastAPI приложения
    """
    from app.core.dependencies.rabbitmq import RabbitMQClient
    from app.core.dependencies.redis import RedisClient
    # from app.core.scheduler import scheduler
    from app.core.logging import setup_logging

    AppState.logger = await setup_logging()
    setup_dishka(container=container, app=app)
    # Запускаем планировщик
    # scheduler.start()
    # await AppState.logger.info("🕒 Планировщик запущен")

    # Подключаемся к сервисам
    for attempt in range(RabbitMQClient._max_retries):
        try:
            await RedisClient.get_instance()
            await RabbitMQClient.get_instance()

            if await RabbitMQClient.health_check():
                break

        except Exception as e:
            await AppState.logger.error(f"❌ Ошибка подключения: {str(e)}")

        if attempt == RabbitMQClient._max_retries - 1:
            await AppState.logger.warning("⚠️ RabbitMQ недоступен после всех попыток")
        else:
            await AppState.logger.info(f"🔄 Попытка подключения {attempt + 1}")
            await asyncio.sleep(RabbitMQClient._retry_delay)

    yield

    # Закрываем соединения
    await RedisClient.close()
    await RabbitMQClient.close()

    # scheduler.shutdown()
    # await AppState.logger.info("👋 Планировщик остановлен")
    await app.state.dishka_container.close()

    await AppState.logger.shutdown()
