"""
Модуль для настройки и инициализации обработчиков сообщений.
"""

import logging

from fastapi import FastAPI

# Импортируем обработчики, чтобы они зарегистрировались
from . import consumers

logger = logging.getLogger(__name__)

def setup_messaging(app: FastAPI):
    """
    Настраивает обработчики сообщений для приложения.

    Args:
        app: FastAPI приложение
    """

    from .broker import rabbit_router

    # Подключаем роутер к приложению
    app.include_router(rabbit_router)

    logger.info("✨ Обработчики сообщений настроены")
