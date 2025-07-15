"""
Модуль хуков для управления жизненным циклом системы сообщений.

Содержит обработчики событий FastStream для инициализации и настройки
системы очередей RabbitMQ при запуске и остановке приложения.

Хуки:
- setup_queues: Создание очередей после запуска приложения

Этот модуль обеспечивает:
- Автоматическое создание необходимых очередей
- Правильную инициализацию RabbitMQ при запуске
- Логирование процесса настройки
"""
import logging

from fastapi import FastAPI

from .broker import rabbit_router

logger = logging.getLogger("app.faststream.hooks")


@rabbit_router.after_startup
async def log_system_ready(app: FastAPI) -> None:
    """
    Логирует готовность системы сообщений после запуска приложения.

    Этот хук выполняется после успешного подключения к RabbitMQ
    и автоматического создания очередей через FastStream consumers.

    Args:
        app (FastAPI): Экземпляр FastAPI приложения

    Returns:
        None

    Note:
        FastStream автоматически создает очереди при регистрации
        @rabbit_router.subscriber декораторов, поэтому ручное
        создание не требуется.
    """
    logger.info("🚀 Система сообщений FastStream готова к работе")
    logger.info("📨 Все consumers активны и ожидают сообщения")
