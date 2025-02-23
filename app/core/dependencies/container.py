"""
Модуль содержит контейнер зависимостей.
"""
from dishka import make_container
from .providers.logger import LoggerProvider
from .providers.database import DatabaseProvider
from .providers.messaging import RabbitMQProvider
from .providers.cache import RedisProvider
from .providers.storage import S3Provider

container = make_container(
    LoggerProvider(),
    DatabaseProvider(),
    RabbitMQProvider(),
    RedisProvider(),
    S3Provider(),
)
