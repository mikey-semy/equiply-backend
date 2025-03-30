"""
Модуль для асинхронной обработки сообщений и фоновых задач.

Предоставляет интерфейс для отправки и обработки сообщений через брокер сообщений.
"""

# Импортируем и инициализируем брокер
from .broker import rabbit_router, broker

# Импортируем публичные классы и функции для использования в других модулях
from .producers import MessageProducer, EmailProducer

# Импортируем API роутер для тестирования
from .api import email_test_router

# Импортируем остальные модули для их инициализации
from . import consumers, hooks

__all__ = [
    'rabbit_router',
    'broker',
    'MessageProducer',
    'EmailProducer',
    'email_test_router',
]
