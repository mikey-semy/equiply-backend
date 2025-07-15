"""
Модуль для настройки и инициализации обработчиков сообщений.
"""
"""
Модуль настройки и инициализации системы сообщений.

Предоставляет функции для интеграции системы FastStream сообщений
с FastAPI приложением. Обеспечивает правильную настройку и
подключение всех компонентов системы.

Функции:
- setup_messaging: Главная функция настройки системы

Этот модуль должен быть вызван при инициализации FastAPI приложения
для подключения системы асинхронных сообщений.

Использование:
    from app.core.integrations.messaging.setup import setup_messaging

    app = FastAPI()
    setup_messaging(app)
"""
import logging

from fastapi import FastAPI


logger = logging.getLogger(__name__)


def setup_messaging(app: FastAPI):
    """
    Настраивает систему сообщений для FastAPI приложения.

    Интегрирует FastStream RabbitMQ router с FastAPI приложением,
    что обеспечивает:
    - Автоматическое подключение к RabbitMQ при запуске
    - Регистрацию всех consumers для обработки сообщений
    - Выполнение хуков жизненного цикла (создание очередей)
    - Правильное закрытие соединений при остановке

    Args:
        app (FastAPI): Экземпляр FastAPI приложения для настройки

    Returns:
        None

    Side Effects:
        - Подключает rabbit_router к FastAPI приложению
        - Регистрирует все consumers из модуля consumers
        - Активирует хуки из модуля hooks
        - Настраивает логирование

    Example:
        >>> from fastapi import FastAPI
        >>> from app.core.integrations.messaging.setup import setup_messaging
        >>>
        >>> app = FastAPI()
        >>> setup_messaging(app)
        >>> # Теперь приложение поддерживает асинхронную отправку email
    """

    # Импортируем rabbit_router и все зависимости
    from .broker import rabbit_router

    # Импортируем consumers, чтобы они зарегистрировались в router
    # Это необходимо для того, чтобы декораторы @rabbit_router.subscriber
    # выполнились и обработчики были зарегистрированы
    from . import consumers

    # Импортируем хуки
    from . import hooks

    # Подключаем rabbit_router к FastAPI приложению
    # Это интегрирует FastStream с FastAPI lifecycle
    app.include_router(rabbit_router)

    logger.info("Система сообщений настроена и подключена к приложению")
