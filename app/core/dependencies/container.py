"""
Модуль содержит контейнер зависимостей.
"""
from dishka import make_container
from .providers.database import DatabaseProvider
from .providers.messaging import RabbitMQProvider
from .providers.cache import RedisProvider
from .providers.storage import S3Provider
from .providers.auth import AuthProvider
from .providers.register import RegisterProvider

container = make_container(
    DatabaseProvider(),
    RabbitMQProvider(),
    RedisProvider(),
    S3Provider(),
    AuthProvider(),
    RegisterProvider()
)
