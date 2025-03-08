"""
Модуль содержит контейнер зависимостей.
"""
from dishka.integrations.fastapi import FastapiProvider
from dishka import make_async_container

from .providers.database import DatabaseProvider
from .providers.messaging import RabbitMQProvider
from .providers.cache import RedisProvider
from .providers.storage import S3Provider
from .providers.auth import AuthProvider
from .providers.register import RegisterProvider

container = make_async_container(
    FastapiProvider(),
    DatabaseProvider(),
    RabbitMQProvider(),
    RedisProvider(),
    S3Provider(),
    AuthProvider(),
    RegisterProvider(),
)
